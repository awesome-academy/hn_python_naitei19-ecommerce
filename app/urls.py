from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('order-summary/', views.OrderSummaryView.as_view(), name='order-summary'),
    path('register/', views.sign_up, name='register'),
    path('product/<slug>/', views.ItemDetailView.as_view(), name='product'),
    path('add-to-cart/<slug>/', views.add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/',
         views.remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>/',
         views.remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('add-coupon/', views.AddCouponView.as_view(), name='add-coupon'),
    path('payment/<payment_option>/', views.PaymentView.as_view(), name='payment'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/delete/', views.UserDeleteView.as_view(), name='profile-delete'),
    path('purchase/', views.OrderListView.as_view(), name='order-list'),
    path('purchase/order/<int:pk>/',
         views.OrderDetailView.as_view(), name='order-detail'),
    path('purchase/order/<int:pk>/cancel/', views.OrderCancellationView.as_view(), name='cancel-order'),
    path('purchase/order/<int:pk>/refund/', views.RefundRequestView.as_view(), name='refund-order'),
    path('review/<slug>/', views.review, name='review'),
    path('like_item/', views.like_item, name='like_item'),
    path('liked/', views.LikedView.as_view(), name='liked'),
]
