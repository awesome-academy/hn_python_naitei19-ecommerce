from django.contrib import admin

from .models import Item


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


admin.site.register(Item, ItemAdmin)
