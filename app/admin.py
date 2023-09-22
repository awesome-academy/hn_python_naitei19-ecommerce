from django.contrib import admin

from .models import Item, Order, OrderItem, Coupon, User, Review


class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'image',
        'title',
        'price',
        'discount_price',
        'category',
        'description',
        'overall',
        'purchases'
    ]

    search_fields = ['title']

    list_display_links = ['image',]

    list_editable = [
        'title',
        'price',
        'discount_price',
        'description',
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_deleted=False)


class OrderItemInlines(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInlines,]

    list_display = ['user',
                    'ref_code',
                    'ordered_date',
                    'shipping_address',
                    'billing_address',
                    'payment',
                    'order_status',
                    'refund_status',
                    'coupon',
                    ]

    list_editable = ['order_status',
                     'refund_status']

    search_fields = [
        'user__username',
        'ref_code'
    ]


class CouponAdmin(admin.ModelAdmin):

    list_display = ['code',
                    'amount',
                    ]

    search_fields = [
        'code',
        'amount'
    ]


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'full_name',
                    'last_login', 'email', 'date_joined', 'is_active']

    list_editable = ['email', 'is_active']

    def full_name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name)


admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Review)
