from django.contrib import admin

from .models import Item


class ItemAdmin(admin.ModelAdmin):
    list_display = [
        'image',
        'title',
        'price',
        'discount_price',
        'category',
        'overall',
        'purchases'
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_deleted=False)


admin.site.register(Item, ItemAdmin)
