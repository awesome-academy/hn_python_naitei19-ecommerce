from django.urls import path
from .views import HomeView, OrderSummaryView, ItemDetailView, add_to_cart, remove_from_cart, remove_single_item_from_cart, sign_up

app_name = 'app'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('register/', sign_up, name='register'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>/',
         remove_single_item_from_cart, name='remove-single-item-from-cart'),
]
