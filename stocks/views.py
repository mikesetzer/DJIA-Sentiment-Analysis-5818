from datetime import datetime, timezone
import os

from django.shortcuts import render

from .models import Stock, StockPrice
from .stock_api import get_daily_closing_stock_prices


def stocks(request):
    stock_price_count = load_db_stock_prices()
    return render(request, "stocks/stocks.html", {"stock_price_count": stock_price_count})


# https://finnhub.io/docs/api/stock-candles
def load_db_stock_prices():
    dt_from = datetime(2022, 6, 1, 0, 0, 0, 0, timezone.utc)
    dt_to = datetime(2022, 6, 11, 0, 0, 0, 0, timezone.utc)

    print('Loading stock prices from "{}" to "{}"'.format(dt_from, dt_to))
    print('Loading stock prices from "{}" to "{}"'.format(dt_from.timestamp(), dt_to.timestamp()))

    finnhub_api_key = os.getenv("FINNHUB_API_KEY")

    # print(finnhub_api_key)
    price_count = 0
    for stock in Stock.objects.all():
        print(stock.ticker)
        price_dict = get_daily_closing_stock_prices(finnhub_api_key, stock.ticker, dt_from, dt_to)
        # print(price_dict)

        for dt, prc in price_dict.items():
            sp, created = StockPrice.objects.get_or_create(stock=stock, date=dt, defaults={'price': prc})

            if created:
                print('Created StockPrice "{}" "{}" "{}"'.format(stock.ticker, sp.date, sp.price))
                price_count += 1

    return price_count
