from datetime import datetime, date, timedelta

from django.shortcuts import render

from .models import Stock, StockPrice
from .stock_api import get_closing_stock_price_on_date, get_closing_stock_prices_date_range


# Retrieve and display stock price information for the given ticker on the given date
def stocks(request):
    # http://127.0.0.1:8000/stocks?ticker=AAPL&price_date=2023-07-31
    ticker = request.GET.get("ticker") or "AAPL"
    price_date = request.GET.get("price_date") or (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    price_date = datetime.strptime(price_date, "%Y-%m-%d").date()
    print('View for stocks "{}" "{}"'.format(ticker, price_date))
    price = get_or_lookup_stock_price(ticker, price_date)
    return render(request, "stocks/stocks.html", {"ticker": ticker, "price_date": price_date, "price": price})


# Populates database with stock price history if no history is available
def stocks_load_history(request):
    # http://127.0.0.1:8000/stocks_load_history

    sp = StockPrice.objects.first()
    if sp:
        print('StockPrice already present "{}" "{}" "{}"'.format(sp.stock.ticker, sp.date, sp.price))
    else:
        price_count = test_bulk_load_db_stock_price_history()
        sp = StockPrice.objects.first()
        print('StockPrice history loaded "{}" "{}" "{}" "{}"'.format(sp.stock.ticker, sp.date, sp.price, price_count))

    return render(request, "stocks/stocks.html", {"ticker": sp.stock.ticker, "price_date": sp.date, "price": sp.price})


def get_or_lookup_stock_price(ticker, price_date):
    stock_price = 0
    s = Stock.objects.filter(ticker=ticker).first()
    if not s:
        print('Stock not found "{}" "{}" "{}"'.format(ticker, price_date, stock_price))
    else:
        sp = StockPrice.objects.filter(stock=s, date=price_date).first()
        if sp:
            stock_price = sp.price
            print('Found StockPrice "{}" "{}" "{}"'.format(s.ticker, sp.date, sp.price))
        else:
            stock_price = get_closing_stock_price_on_date(ticker, price_date)
            if stock_price > 0:
                sp = StockPrice.objects.create(stock=s, date=price_date, price=stock_price)
                print('Created StockPrice "{}" "{}" "{}"'.format(s.ticker, sp.date, sp.price))
            else:
                print('StockPrice not found "{}" "{}" "{}"'.format(s.ticker, price_date, stock_price))

    return stock_price


# Populates database with stock price history from finhub.
# Uses all stocks in the database for a hard coded date range.
def test_bulk_load_db_stock_price_history():
    dt_from = date(2022, 6, 1)
    dt_to = date(2022, 6, 11)
    print('Loading stock prices from "{}" to "{}"'.format(dt_from, dt_to))

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
