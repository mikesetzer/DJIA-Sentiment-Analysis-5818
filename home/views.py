from django.shortcuts import render
from django.http import HttpResponse
from finnhub import Client
import os
from datetime import datetime


# Create your views here.

def home_view(request):
    # Example dummy data, replace with actual logic
    stocks_list = [
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 150.00, 'change': -0.50, 'percent_change': -0.33,
         'low': 149.50, 'high': 151.00, 'prev_close': 150.50},
        {'symbol': 'AXP', 'name': 'American Express', 'price': 160.00, 'change': 1.50, 'percent_change': 0.94,
         'low': 159.00, 'high': 162.00, 'prev_close': 158.50},
        {'symbol': 'BA', 'name': 'Boeing Co.', 'price': 220.00, 'change': -2.00, 'percent_change': -0.90, 'low': 219.00,
         'high': 223.00, 'prev_close': 222.00},
        {'symbol': 'CAT', 'name': 'Caterpillar Inc.', 'price': 210.00, 'change': 3.00, 'percent_change': 1.44,
         'low': 207.00, 'high': 213.00, 'prev_close': 207.00},
        {'symbol': 'CRM', 'name': 'Salesforce', 'price': 240.00, 'change': 2.50, 'percent_change': 1.05, 'low': 238.00,
         'high': 243.00, 'prev_close': 237.50},
        {'symbol': 'CSCO', 'name': 'Cisco Systems', 'price': 55.00, 'change': -0.50, 'percent_change': -0.90,
         'low': 54.50, 'high': 56.00, 'prev_close': 55.50},
        {'symbol': 'CVX', 'name': 'Chevron Corporation', 'price': 110.00, 'change': 1.00, 'percent_change': 0.91,
         'low': 109.00, 'high': 111.00, 'prev_close': 109.00},
        {'symbol': 'DIS', 'name': 'Walt Disney', 'price': 180.00, 'change': -1.00, 'percent_change': -0.55,
         'low': 179.00, 'high': 181.00, 'prev_close': 181.00},
        {'symbol': 'DOW', 'name': 'Dow Inc.', 'price': 60.00, 'change': 0.50, 'percent_change': 0.84, 'low': 59.50,
         'high': 60.50, 'prev_close': 59.50},
        {'symbol': 'GS', 'name': 'Goldman Sachs', 'price': 380.00, 'change': 5.00, 'percent_change': 1.33,
         'low': 375.00, 'high': 385.00, 'prev_close': 375.00},
        {'symbol': 'HD', 'name': 'Home Depot', 'price': 340.00, 'change': -3.00, 'percent_change': -0.88, 'low': 337.00,
         'high': 343.00, 'prev_close': 343.00},
        {'symbol': 'IBM', 'name': 'IBM', 'price': 140.00, 'change': 1.50, 'percent_change': 1.08, 'low': 138.50,
         'high': 141.50, 'prev_close': 138.50},
        {'symbol': 'INTC', 'name': 'Intel Corp.', 'price': 53.00, 'change': -0.50, 'percent_change': -0.93,
         'low': 52.50, 'high': 53.50, 'prev_close': 53.50},
        {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'price': 165.00, 'change': 2.00, 'percent_change': 1.22,
         'low': 163.00, 'high': 167.00, 'prev_close': 163.00},
        {'symbol': 'JPM', 'name': 'JPMorgan Chase', 'price': 160.00, 'change': -1.50, 'percent_change': -0.93,
         'low': 158.50, 'high': 161.50, 'prev_close': 161.50},
        {'symbol': 'KO', 'name': 'Coca-Cola', 'price': 56.00, 'change': 0.00, 'percent_change': 0.00, 'low': 56.00,
         'high': 56.00, 'prev_close': 56.00},
        {'symbol': 'MCD', 'name': 'McDonald\'s Corp.', 'price': 240.00, 'change': 3.00, 'percent_change': 1.27,
         'low': 237.00, 'high': 243.00, 'prev_close': 237.00},
        {'symbol': 'MMM', 'name': '3M Co.', 'price': 190.00, 'change': -2.00, 'percent_change': -1.04, 'low': 188.00,
         'high': 192.00, 'prev_close': 192.00},
        {'symbol': 'MRK', 'name': 'Merck & Co.', 'price': 75.00, 'change': 1.00, 'percent_change': 1.35, 'low': 74.00,
         'high': 76.00, 'prev_close': 74.00},
        {'symbol': 'MSFT', 'name': 'Microsoft Corp.', 'price': 300.00, 'change': 2.00, 'percent_change': 0.67,
         'low': 298.00, 'high': 302.00, 'prev_close': 298.00},
        {'symbol': 'NKE', 'name': 'Nike', 'price': 150.00, 'change': 1.50, 'percent_change': 1.01, 'low': 148.50,
         'high': 151.50, 'prev_close': 148.50},
        {'symbol': 'PG', 'name': 'Procter & Gamble', 'price': 140.00, 'change': -1.00, 'percent_change': -0.71,
         'low': 139.00, 'high': 141.00, 'prev_close': 141.00},
        {'symbol': 'TRV', 'name': 'Travelers Companies Inc.', 'price': 150.00, 'change': -1.50, 'percent_change': -0.99,
         'low': 148.50, 'high': 151.50, 'prev_close': 151.50},
        {'symbol': 'UNH', 'name': 'UnitedHealth Group Inc.', 'price': 420.00, 'change': 4.00, 'percent_change': 0.96,
         'low': 416.00, 'high': 424.00, 'prev_close': 416.00},
        {'symbol': 'V', 'name': 'Visa Inc.', 'price': 230.00, 'change': -2.50, 'percent_change': -1.08, 'low': 227.50,
         'high': 232.50, 'prev_close': 232.50},
        {'symbol': 'VZ', 'name': 'Verizon Communications', 'price': 55.00, 'change': -0.50, 'percent_change': -0.90,
         'low': 54.50, 'high': 55.50, 'prev_close': 55.50},
        {'symbol': 'WBA', 'name': 'Walgreens Boots Alliance', 'price': 50.00, 'change': 0.50, 'percent_change': 1.01,
         'low': 49.50, 'high': 50.50, 'prev_close': 49.50},
        {'symbol': 'WMT', 'name': 'Walmart', 'price': 145.00, 'change': 0.50, 'percent_change': 0.35, 'low': 144.50,
         'high': 145.50, 'prev_close': 144.50},
        {'symbol': 'XOM', 'name': 'Exxon Mobil Corp.', 'price': 60.00, 'change': -0.50, 'percent_change': -0.83,
         'low': 59.50, 'high': 60.50, 'prev_close': 60.50},
    ]

    context = {
        'stocks_list': stocks_list,
    }

    # Page from the theme
    return render(request, 'stocks_list.html', context)


def stock_detail_view(request, symbol):
    finnhub_api_key = os.getenv("FINNHUB_API_KEY")

    if finnhub_api_key is None:
        raise ValueError("API Key for Finnhub is missing!")

    finnhub_client = Client(api_key=finnhub_api_key)

    # Replace with actual logic to fetch and process stock and news data
    stock = {
        'name': 'Apple Inc.',
        'recommendation': 'Buy',
        'price': 150.00,
        'market_cap': '2.41T',
        # Add more properties as needed
    }

    current_date = datetime.now().strftime("%Y-%m-%d")
    # Example of fetching news from the Finnhub API, replace with actual logic
    news_list = finnhub_client.company_news(symbol, _from="2022-01-01", to=current_date)[:5]

    context = {
        'stock': stock,
        'news_list': news_list,
    }

    return render(request, 'stock_detail.html', context)
