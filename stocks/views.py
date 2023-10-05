from datetime import datetime, date, timedelta

from django.shortcuts import render

from .models import Stock, StockPrice, SentimentScore
from .stock_api import get_closing_stock_price_on_date, get_closing_stock_prices_date_range, get_stock_candle_info


# Retrieve and display stock price information for the given ticker on the given date
def stocks(request):
    # http://127.0.0.1:8000/stocks?ticker=AAPL&price_date=2023-07-31
    ticker = request.GET.get("ticker") or "AAPL"
    price_date = request.GET.get("price_date") or (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    price_date = datetime.strptime(price_date, "%Y-%m-%d").date()
    print('View for stocks "{}" "{}"'.format(ticker, price_date))
    price = get_or_lookup_stock_price(ticker, price_date)
    return render(request, "stocks/stocks.html", {"ticker": ticker, "price_date": price_date, "price": price})


# Retrieve and display stock price information for the given ticker on the given date
def stock_details(request):
    # http://127.0.0.1:8000/stock_details?ticker=AAPL&price_date=2023-07-31
    ticker = request.GET.get("ticker") or "AAPL"
    price_date = request.GET.get("price_date") or (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
    price_date = datetime.strptime(price_date, "%Y-%m-%d").date()
    print('View for stock_details "{}" "{}"'.format(ticker, price_date))
    stock_dtl = get_stock_details(ticker, price_date)
    return render(request, "stocks/stockdetails.html", stock_dtl)


# Retrieve and display recent sentiment scores for the given ticker
def sentiment_score(request):
    # http://127.0.0.1:8000/sentiment?ticker=AAPL
    ticker = request.GET.get("ticker") or "AAPL"
    print('Sentiment for stock "{}"'.format(ticker))
    sentiment_scores = get_recent_sentiment_scores(ticker)
    return render(request, "stocks/sentiment.html", {"ticker": ticker, "sentiment_scores": sentiment_scores})


def stocks_view_price_history(request):
    # http://127.0.0.1:8000/pricehistory?ticker=AAPL
    ticker = request.GET.get("ticker") or "AAPL"
    print('Price history for stock "{}"'.format(ticker))
    stock_prices = get_recent_stock_prices(ticker)
    return render(request, "stocks/pricehistory.html", {"ticker": ticker, "stock_prices": stock_prices})


# Populates database with stock price history if no history is available
def stocks_load_price_history(request):
    # http://127.0.0.1:8000/loadprices

    # sp = StockPrice.objects.first()
    stock_prices = get_recent_stock_prices()
    if stock_prices:
        sp = stock_prices[0]
        print('StockPrice already present "{}" "{}" "{}"'.format(sp.stock.ticker, sp.date, sp.price))
    else:
        price_count = test_bulk_load_db_stock_price_history()
        stock_prices = get_recent_stock_prices()
        sp = stock_prices[0]
        # sp = StockPrice.objects.first()
        print('StockPrice history loaded "{}" "{}" "{}" "{}"'.format(sp.stock.ticker, sp.date, sp.price, price_count))

    return render(request, "stocks/pricehistory.html", {"ticker": "All", "stock_prices": stock_prices})


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


def get_stock_details(ticker, price_date):
    stock_dtl = {}
    s = Stock.objects.filter(ticker=ticker).first()
    if not s:
        print('Stock not found "{}" "{}"'.format(ticker, price_date))
    else:
        stock_dtl = get_stock_candle_info(ticker, price_date)
        if stock_dtl:
            print('Stock details: "{}"'.format(stock_dtl))
        else:
            print('Stock details not found "{}" "{}"'.format(ticker, price_date))

    return stock_dtl


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


def get_recent_sentiment_scores(ticker):
    sentiment_scores = None
    s = Stock.objects.filter(ticker=ticker).first()
    if s:
        sentiment_scores = SentimentScore.objects.filter(stock=s).order_by('-date')[:10]
    else:
        print('Stock not found "{}"'.format(ticker))

    return sentiment_scores


# Get the most recent stock prices for the given ticker
def get_recent_stock_prices(ticker="", max_records=20):
    stock_prices = None

    if ticker:
        s = Stock.objects.filter(ticker=ticker).first()
        if s:
            stock_prices = StockPrice.objects.filter(stock=s).order_by('-date')[:max_records]
        else:
            print('Stock not found "{}"'.format(ticker))
    if not stock_prices:
        stock_prices = StockPrice.objects.order_by('-date')[:max_records]

    return stock_prices
