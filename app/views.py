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


class HomeView(ListView):
    model = Item
    paginate_by = 10
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
            print(order.amount)
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
