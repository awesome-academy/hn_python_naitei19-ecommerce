import random
import string
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
from django.db import transaction
from django.contrib.auth import logout

from .constants import CATEGORY_CHOICES, ORDER_STATUS
from .utils import int_or_none, float_or_none, is_valid_form
from .forms import RegisterForm, CheckoutForm, CouponForm, PaymentForm, ReviewForm
from .models import Address, Coupon, Item, Order, OrderItem, Payment, Review


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
    def DEFAULT_SORT(x): return -x.overall

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


class CheckoutView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, order_status=0)
            order_items = OrderItem.objects.filter(order=order)
            coupon = 0
            if (order.coupon == None):
                coupon = 0
            else:
                coupon = order.coupon.amount
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'order_items': order_items,
                'total': order.amount - coupon,
                'DISPLAY_COUPON_FORM': True
            }

            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type=1,
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs.last()})

            billing_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type=0,
                default=True
            )
            if billing_address_qs.exists():
                context.update(
                    {'default_billing_address': billing_address_qs.last()})
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, _("You do not have an active order"))
            return redirect("app:home")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, order_status=0)
            if form.is_valid():

                self.process_shipping_address(form, order)
                self.process_billing_address(form, order)
                return self.redirect_payment(form)

            else:
                return messages.info(
                    self.request, _("Please fill in the required fields"))

        except ObjectDoesNotExist:
            messages.warning(self.request, _(
                "You do not have an active order"))
            return redirect("app:order-summary")

    def process_shipping_address(self, form, order):
        use_default_shipping = form.cleaned_data.get('use_default_shipping')
        if use_default_shipping:
            address_qs = Address.objects.filter(
                user=self.request.user,
                address_type=1,
                default=True
            )
            if address_qs.exists():
                shipping_address = address_qs[0]
                order.shipping_address = shipping_address
                order.save()
            else:
                messages.info(
                    self.request, _("No default shipping address available"))
                return redirect('app:checkout')
        else:
            shipping_address1 = form.cleaned_data.get('shipping_address')
            shipping_address2 = form.cleaned_data.get('shipping_address2')
            shipping_country = form.cleaned_data.get('shipping_country')
            shipping_zip = form.cleaned_data.get('shipping_zip')

            if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                shipping_address = Address(
                    user=self.request.user,
                    street_address=shipping_address1,
                    apartment_address=shipping_address2,
                    country=shipping_country,
                    zip=shipping_zip,
                    address_type=1
                )
                shipping_address.save()
                order.shipping_address = shipping_address
                order.save()

                set_default_shipping = form.cleaned_data.get(
                    'set_default_shipping')
                if set_default_shipping:
                    shipping_address.default = True
                    shipping_address.save()
            else:
                messages.info(
                    self.request, _("Please fill in the required shipping address fields"))

    def process_billing_address(self, form, order):
        use_default_billing = form.cleaned_data.get('use_default_billing')
        if use_default_billing:
            address_qs = Address.objects.filter(
                user=self.request.user,
                address_type=0,
                default=True
            )
            if address_qs.exists():
                billing_address = address_qs[0]
                order.billing_address = billing_address
                order.save()
            else:
                messages.info(
                    self.request, _("No default billing address available"))
                return redirect('app:checkout')
        else:
            billing_address1 = form.cleaned_data.get('billing_address')
            billing_address2 = form.cleaned_data.get('billing_address2')
            billing_country = form.cleaned_data.get('billing_country')
            billing_zip = form.cleaned_data.get('billing_zip')

            if is_valid_form([billing_address1, billing_country, billing_zip]):
                billing_address = Address(
                    user=self.request.user,
                    street_address=billing_address1,
                    apartment_address=billing_address2,
                    country=billing_country,
                    zip=billing_zip,
                    address_type=0
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                set_default_billing = form.cleaned_data.get(
                    'set_default_billing')
                if set_default_billing:
                    billing_address.default = True
                    billing_address.save()
            else:
                messages.info(
                    self.request, _("Please fill in the required billing address fields"))

    def redirect_payment(self, form):
        payment_option = form.cleaned_data.get('payment_option')
        if payment_option == 'S':
            return redirect("app:payment", payment_option='card')
        else:
            messages.warning(
                self.request, _("Invalid payment option selected"))
            return redirect("app:checkout")


@login_required
@csrf_exempt
def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, _("This coupon does not exist"))
        return redirect("app:checkout")


class AddCouponView(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, order_status=0)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, _("Successfully added coupon"))
                return redirect("app:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, _(
                    "You do not have an active order"))
                return redirect("app:checkout")


@csrf_exempt
def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


class PaymentView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, order_status=0)
        order_items = OrderItem.objects.filter(order=order)
        coupon = 0
        if (order.coupon == None):
            coupon = 0
        else:
            coupon = order.coupon.amount
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False,
                'order_items': order_items,
                'total': order.amount - coupon,
            }
            return render(self.request, "payment.html", context)
        else:
            messages.warning(
                self.request, _("You have not added a billing address"))
            return redirect("app:checkout")

    @transaction.atomic
    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, order_status=0)
        form = PaymentForm(self.request.POST)
        if form.is_valid():
            card_number = form.cleaned_data.get('card_number')
            coupon = 0
            if (order.coupon == None):
                coupon = 0
            else:
                coupon = order.coupon.amount

            try:
                with transaction.atomic():
                    # create the payment
                    payment = Payment()
                    payment.card_number = card_number
                    payment.user = self.request.user
                    payment.amount = order.amount - coupon
                    payment.status = 1
                    payment.save()

                    # assign the payment to the order
                    order.order_status = 1
                    order.payment = payment
                    order.ref_code = create_ref_code()
                    order.save()

                messages.success(self.request, _("Your order was successful!"))
                return redirect("/")

            except Exception as e:
                messages.warning(
                    self.request, _("A serious error occurred. We have been notifed."))
                return redirect("/")

        messages.warning(self.request, _("Invalid data received"))
        return redirect("/payment/card/")


class ProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'registration/profile.html')


class UserDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = request.user
        user.is_active = False
        user.save()
        logout(request)
        messages.success(request, _("Account has been successfully deleted."))
        return redirect('app:home')


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'order_list.html'

    def get_queryset(self):
        filter_options = {
            'user': self.request.user
        }
        type = self.request.GET.get('type')
        if type:
            filter_options.update(order_status=type)
        order_list = (Order.objects.filter(**filter_options)
                      .exclude(order_status=0)
                      .select_related('coupon'))

        result = []
        for order in order_list:
            result.append({
                'id': order.id,
                'ref_code': order.ref_code,
                'ordered_date': order.ordered_date,
                'order_status': ORDER_STATUS[order.order_status],
                'total': order.amount - (order.coupon if order.coupon else 0)
            })
        return result

    def get_context_data(self, **kwargs):
        context = super(OrderListView, self).get_context_data(**kwargs)
        context['order_status'] = ORDER_STATUS[1:]
        context['CAN_CANCEL'] = 1

        type = self.request.GET.get('type')
        context['type'] = int_or_none(type)

        return context


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order_detail.html'

    progress = [0, 20, 60, 100]

    def get_object(self):
        try:
            order = Order.objects.get(
                user=self.request.user,
                order_status__gt=0,
                pk=self.kwargs['pk'],
            )
            return order
        except ObjectDoesNotExist:
            messages.info(self.request,
                          _("The order does not exist or you do not have access"))
            return redirect("app:order-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_item = OrderItem.objects.filter(order=self.object)
        context['order_item_list'] = order_item
        context['order_status'] = ORDER_STATUS[1:4]
        context['order_progress'] = self.progress[self.object.order_status]
        context['coupon'] = self.object.coupon if self.object.coupon else 0
        context['order_total'] = self.object.amount - context['coupon']
        context['current_status'] = ORDER_STATUS[self.object.order_status][1]
        if self.object.order_status == 3:
            context['can_rate'] = True
        return context


@login_required
def review(request, slug):
    if request.method == 'GET':
        form = ReviewForm()
        item = get_object_or_404(Item, slug=slug)
        return render(request, 'review.html', {'form': form, 'item': item})
    else:
        messages.info(request, _('Failed to get item'))
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        rating = request.POST.get('rating')
        description = request.POST.get('review')
        item = get_object_or_404(Item, slug=slug)
        review_query = Review.objects.filter(
            user=request.user, item=item).first()
        if (review_query):
            review_query.description = description
            review_query.overall = rating
            review_query.save()
        else:
            new_review = Review.objects.create(
                user=request.user, item=item, description=description, overall=rating)
            new_review.save()
        return redirect('/')
    else:
        messages.info(request, _('Failed to get review'))
    return redirect('/')
