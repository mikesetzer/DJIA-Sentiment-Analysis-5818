import os
from datetime import datetime, timezone

from finnhub import Client


# https://finnhub.io/docs/api/stock-candles
def get_finhub_stock_candles(ticker, dt_from, dt_to):
    finnhub_api_key = os.getenv("FINNHUB_API_KEY")

    # Convert from datetime to UNIX timestamp
    int_from = int(round(dt_from.timestamp()))
    int_to = int(round(dt_to.timestamp()))

    # Setup client
    finnhub_client = Client(api_key=finnhub_api_key)

    candles = finnhub_client.stock_candles(ticker, 'D', int_from, int_to)
    # print(candles)
    return candles


def get_closing_stock_prices_date_range(ticker, dt_from, dt_to):
    price_dict = {}
    candles = get_finhub_stock_candles(ticker, dt_from, dt_to)

    for dt, price in zip(candles['t'], candles['c']):
        price_dict[datetime.fromtimestamp(dt, timezone.utc).strftime("%Y-%m-%d")] = price

    return price_dict


def get_closing_stock_price_on_date(ticker, dt_price):
    stock_price = 0
    candles = get_finhub_stock_candles(ticker, dt_price, dt_price)

    if candles and candles['s'] != 'no_data':
        stock_price = candles['c'][0]

    return stock_price

# from dotenv import load_dotenv
# load_dotenv()  # take environment variables from .env.
# def test_get_daily_closing_stock_prices():
#     dt_from = datetime(2022, 6, 1, 0, 0, 0, 0, timezone.utc)
#     print(dt_from)
#     print(dt_from.timestamp())
#
#     dt_to = datetime(2022, 6, 11, 0, 0, 0, 0, timezone.utc)
#     print(dt_to)
#     print(dt_to.timestamp())
#
#     finnhub_api_key = os.getenv("FINNHUB_API_KEY")
#     print(finnhub_api_key)
#     ticker = "AAPL"
#     price_dict = get_daily_closing_stock_prices(finnhub_api_key, ticker, dt_from, dt_to)
#     print(price_dict)
#
#
# test_get_daily_closing_stock_prices()
