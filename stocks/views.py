from datetime import datetime, timezone

from django.shortcuts import render

from .models import Stock, StockPrice
from .stock_api import get_closing_stock_price_on_date, get_closing_stock_prices_date_range


def stocks(request):
    # http://127.0.0.1:8000/stocks?ticker=AAPL&price_date=2023-07-31
    ticker = request.GET.get("ticker") or "AAPL"
    price_date = request.GET.get("price_date") or datetime.today().strftime('%Y-%m-%d')
    price_date = datetime.strptime(price_date, "%Y-%m-%d")
    # price_date = datetime(price_date.year, price_date.month, price_date.day)
    print('View for stocks "{}" "{}"'.format(ticker, price_date))
    price = get_or_lookup_stock_price(ticker, price_date)
    return render(request, "stocks/stocks.html", {"ticker": ticker, "price_date": price_date, "price": price})


def get_or_lookup_stock_price(ticker, price_date):
    stock_price = 0
    s = Stock.objects.get(ticker=ticker)
    sp = StockPrice.objects.filter(stock=s, date=price_date).first()
    if sp:
        stock_price = sp.price
        print('Found StockPrice "{}" "{}" "{}"'.format(s.ticker, sp.date, sp.price))
    else:
        stock_price = get_closing_stock_price_on_date(ticker, price_date)
        sp = StockPrice.objects.create(stock=s, date=price_date, price=stock_price)
        print('Created StockPrice "{}" "{}" "{}"'.format(s.ticker, sp.date, sp.price))

    return stock_price


def test_bulk_load_db_stock_price_history():
    dt_from = datetime(2022, 6, 1, 0, 0, 0, 0, timezone.utc)
    dt_to = datetime(2022, 6, 11, 0, 0, 0, 0, timezone.utc)
    print('Loading stock prices from "{}" to "{}"'.format(dt_from, dt_to))
    print('Loading stock prices from "{}" to "{}"'.format(dt_from.timestamp(), dt_to.timestamp()))

    price_count = 0
    for stock in Stock.objects.all():
        print(stock.ticker)
        price_dict = get_closing_stock_prices_date_range(stock.ticker, dt_from, dt_to)
        # print(price_dict)

        for dt, prc in price_dict.items():
            sp, created = StockPrice.objects.get_or_create(stock=stock, date=dt, defaults={'price': prc})

            if created:
                print('Created StockPrice "{}" "{}" "{}"'.format(stock.ticker, sp.date, sp.price))
                price_count += 1

    return price_count
