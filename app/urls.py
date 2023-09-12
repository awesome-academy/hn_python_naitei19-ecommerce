from django.urls import path
from .views import HomeView, sign_up

app_name = 'app'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('register/', sign_up, name='register'),
]
