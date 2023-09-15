from django.views.generic import ListView, DetailView, View
from django.shortcuts import get_object_or_404, redirect, render
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth import login
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import RegisterForm
from .models import Item, Order, OrderItem
from .constants import CATEGORY_CHOICES
from .utils import int_or_none, float_or_none


class HomeView(ListView):
    SORT_CHOICES = [
        {
            'text': _('Price: low to high'),
            'func': lambda x: x.discount_price if x.discount_price else x.price},
        {
            'text': _('Price: high to low'),
            'func': lambda x: -x.discount_price if x.discount_price else -x.price},
        {
            'text': _('% Discount'),
            'func': lambda x: (x.discount_price if x.discount_price else x.price)/x.price * 100 - 100}
    ]
    DEFAULT_SORT = lambda x: -x.overall

    model = Item
    paginate_by = 10

    def get_queryset(self):
        params = self.request.GET
        category_option = params.get('category')
        price_from = params.get('price_from')
        price_to = params.get('price_to')
        star_from = params.get('star_from')
        star_to = params.get('star_to')
        sort = params.get('sort')
        product_name = params.get('name')

        filter_options = {}
        if category_option:
            filter_options.update(category=category_option)
        if price_from:
            filter_options.update(price__gte=price_from)
        if price_to:
            filter_options.update(price__lte=price_to)
        if star_from:
            filter_options.update(overall__gte=star_from)
        if star_to:
            filter_options.update(overall__lte=star_to)
        if product_name:
            filter_options.update(title__icontains=product_name)

        sort_option = self.__class__.DEFAULT_SORT
        if sort:
            sort_option = self.SORT_CHOICES[int(sort)]['func']

        result = Item.objects.filter(**filter_options)
        result = sorted(result, key=sort_option)

        return result

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['category_choices'] = CATEGORY_CHOICES
        context['sort_choices'] = self.SORT_CHOICES

        params = self.request.GET
        context['category_option'] = int_or_none(params.get('category'))
        context['price_from'] = float_or_none(params.get('price_from'))
        context['price_to'] = float_or_none(params.get('price_to'))
        context['star_from'] = float_or_none(params.get('star_from'))
        context['star_to'] = float_or_none(params.get('star_to'))
        context['sort'] = int_or_none(params.get('sort'))
        context['product_name'] = params.get('name')

        return context

    template_name = "home.html"


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, order_status=0)
            order_item = OrderItem.objects.filter(order=order)
            coupon = 0
            if (order.coupon == None):
                coupon = 0
            else:
                coupon = order.coupon.amount
            context = {
                'object': order_item,
                'cart_total': order.amount - coupon,
                'coupon': coupon
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, _(
                "You do not have an active order"))
            return redirect("/")


def sign_up(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'registration/register.html', {'form': form})
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            messages.success(request, _('You have singed up successfully.'))
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'registration/register.html', {'form': form})


@login_required
@csrf_exempt
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_query = Order.objects.filter(user=request.user, order_status=0)
    if order_query.exists():
        order = order_query[0]
        order_item = OrderItem.objects.filter(
            order=order, item=item).first()
        if order_item:
            order.amount += order_item.get_single_price()
            order.save()
            order_item.quantity += 1
            order_item.save()
        else:
            order_item = OrderItem.objects.create(
                order=order, price=item.price, item=item)
            order.amount += order_item.get_single_price()
            order.save()
        if (order.coupon == None):
            coupon = 0
        else:
            coupon = order.coupon.amount
        order.amount -= coupon
        if request.method == 'POST':
            return JsonResponse({'message': 'Item added to your cart.', 'quantity': order_item.quantity,
                                 'cart_total': order.amount, 'item_total': order_item.get_final_price()})
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date, amount=0)
        order_item = OrderItem.objects.create(
            order=order, price=item.price, item=item)
        order.amount += order_item.get_single_price()
        order.save()
        messages.info(request, _('The item was added to your cart.'))
    return redirect('app:order-summary')


@login_required
@csrf_exempt
def remove_from_cart(request, slug):
    if request.method == 'POST':
        item = get_object_or_404(Item, slug=slug)
        order_query = Order.objects.filter(user=request.user, order_status=0)
        if order_query.exists():
            order = order_query[0]
            order_item = OrderItem.objects.filter(order=order, item=item)
            if order_item:
                for cart_item in order_item:
                    order.amount -= cart_item.get_final_price()
                    order.save()
                    cart_item.delete()
                return JsonResponse({'message': 'Items removed from your cart.', 'cart_total': order.amount})
            else:
                return JsonResponse({'message': 'Item was not in your cart.'})
        else:
            messages.info(request, _('You do not have an active order.'))
            return JsonResponse({'message': 'You do not have an active order.'})
    return JsonResponse({'message': 'Failed to POST'})


@login_required
@csrf_exempt
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_query = Order.objects.filter(user=request.user, order_status=0)
    if order_query.exists():
        order = order_query[0]
        order_item = OrderItem.objects.filter(order=order, item=item).first()
        if order_item:
            if (order_item.quantity > 1):
                order.amount -= order_item.get_single_price()
                order.save()
                order_item.quantity -= 1
                order_item.save()
            else:
                order.amount -= order_item.get_single_price()
                order.save()
                order_item.delete()
                return JsonResponse({'message': 'Item removed from your cart.', 'quantity': 0, 'cart_total': order.amount})
            if (order.coupon == None):
                coupon = 0
            else:
                coupon = order.coupon.amount
            order.amount -= coupon
            return JsonResponse({'message': 'Item removed from your cart.', 'quantity': order_item.quantity,
                                 'cart_total': order.amount, 'item_total': order_item.get_final_price()})
        else:
            messages.info(request, _('Item was not in your cart.'))
            return redirect('app:order-summary')
    else:
        messages.info(request, _('You do not have an active order.'))
        return redirect('app:order-summary')
