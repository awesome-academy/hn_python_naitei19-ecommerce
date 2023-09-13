from django.contrib import admin

from .models import Item, Order


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


class OrderAdmin(admin.ModelAdmin):
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


admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
