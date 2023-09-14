from django import template

from app.models import Order, OrderItem

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        order_query = Order.objects.filter(user=user, order_status=0)
        if order_query.exists():
            order = order_query[0]
            order_item = OrderItem.objects.filter(order=order)
            return order_item.count()
    return 0
