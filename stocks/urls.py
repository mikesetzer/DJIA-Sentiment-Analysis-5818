from django.urls import path

from . import views

urlpatterns = [
    path('stocks/', views.stocks, name='stocks'),
    path('stocks_load_history/', views.stocks_load_history, name='stocks_load_history'),
]
