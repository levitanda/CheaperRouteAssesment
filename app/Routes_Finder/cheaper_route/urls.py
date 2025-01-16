# api/urls.py
from django.urls import path
from . import views  # Import your views here

urlpatterns = [
    path('get_cheaper_route/', views.find_cheapest_route, name='get_route'),  # Example endpoint
]
