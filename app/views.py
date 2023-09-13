from django.views.generic import ListView

from .models import Item


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home.html"
