from django.urls import path

from . import views

urlpatterns = [
    path('stocks/', views.stocks, name='stocks'),
    path('pricehistory/', views.stocks_view_price_history, name='stocks_load_price_history'),
    path('loadprices/', views.stocks_load_price_history, name='stocks_load_history'),
    path('sentiment/', views.sentiment_score, name='sentiment_score'),
    path('stockdetails/', views.stock_details, name='stock_details'),
]
