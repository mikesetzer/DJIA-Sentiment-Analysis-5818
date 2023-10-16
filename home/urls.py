from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),  # Keeps the home view
    path('stock/<str:symbol>/', views.stock_detail_view, name='stock_detail'),  # Added stock detail view
]
