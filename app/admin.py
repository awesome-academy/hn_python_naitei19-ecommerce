from operator import itemgetter
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from django.db import models

from .models import Address, Item, Order, OrderItem, Coupon, Refund, ShopInfor, User, Review
from app import constants as const


class OrderItemInlines(admin.TabularInline):
    model = OrderItem


class OrderAdmin(admin.ModelAdmin):
    change_list_template = 'admin/app/order/change_list.html'

    inlines = [OrderItemInlines,]

    list_display = ['user',
                    'ref_code',
                    'ordered_date',
                    'shipping_address',
                    'billing_address',
                    'payment',
                    'order_status',
                    'coupon',
                    ]

    list_editable = ['order_status',
                     ]

    search_fields = [
        'user__username',
        'ref_code'
    ]

    def analytics(self, request):
        orders = list(Order.objects.all())
        status = list(itemgetter(1)(choice)
                      for choice in const.ORDER_STATUS)
        orders_count = list(Order.objects.values(
            'order_status').annotate(count=models.Count('order_status'),
                                     ))
        order_count_data = [{
            'name': const.ORDER_STATUS[order['order_status']][1],
            'y': order['count']} for order in orders_count]
        data = {
            'orders': orders,
            'status': status,
            'order_count_data': order_count_data,
        }
        return render(request, "order_analytics.html", {"data": data, "title": "Order analytics"})

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [path("analytics/", self.analytics), ]
        return custom_urls + urls


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


class ShopInforAdmin(admin.ModelAdmin):

    list_display = ['name',
                    'description',
                    'address',
                    'logo',
                    'insta',
                    'facebook',
                    'youtube',
                    ]

    # Only added when there is no data
    def has_add_permission(self, request):
        return not ShopInfor.objects.exists()


class ItemResource(resources.ModelResource):
    class Meta:
        model = Item
        store_instance = True
        import_id_fields = ('slug', )
        exclude = ('id',)


class ItemAdmin(ImportExportModelAdmin):
    resource_classes = [ItemResource]
    change_list_template = 'admin/app/item/change_list.html'

    list_display = [
        'id',
        'title',
        'image',
        'price',
        'discount_price',
        'category',
        'description',
        'overall',
        'purchases'
    ]
    search_fields = ['title']

    list_display_links = ['id',]

    list_editable = [
        'title',
        'price',
        'discount_price',
        'description',
        'category'
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_deleted=False)

    def analytics(self, request):
        items = list(Item.objects.all())
        categories = list(itemgetter(1)(choice)
                          for choice in const.CATEGORY_CHOICES)
        items_count = list(Item.objects.values(
            'category').annotate(count=models.Count('category'),
                                 overall=models.Sum(
                                     'overall')/models.Count('category'),
                                 purchases=models.Sum('purchases')))
        item_count_data = [{
            'name': const.CATEGORY_CHOICES[item['category']][1],
            'data': [item['count']]} for item in items_count]
        item_sale_data = [{
            'name': const.CATEGORY_CHOICES[item['category']][1],
            'data': [item['purchases']]} for item in items_count]
        data = {
            'items': items,
            'categories': categories,
            'items_count': item_count_data,
            'items_sale': item_sale_data
        }
        return render(request, "item_analytics.html", {"data": data, "title": "Items analytics"})

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [path("analytics/", self.analytics), ]
        return custom_urls + urls


admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Review)
admin.site.register(ShopInfor, ShopInforAdmin)
admin.site.register(Address)
