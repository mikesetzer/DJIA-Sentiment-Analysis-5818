import random
import time
from datetime import datetime

from finnhub import Client, FinnhubRequestException, FinnhubAPIException

from home.models import StockQuote, Stock


# Custom version of finnhub's client class that can handle exceptions more gracefully
# https://finnhub.io/docs/api/
class StockAPIClient(Client):
    def __init__(self, api_key):
        super().__init__(api_key)

    # https://finnhub.io/docs/api/quote
    # if quote() is successful, it returns a dictionary of the following items:
    #   {'c': 176.495, 'd': -0.655, 'dp': -0.3697, 'h': 177.57, 'l': 175.4242, 'o': 175.58, 'pc': 177.15, 't': 1697650902}
    # invalid ticker returns the following:
    #   {'c': 0, 'd': None, 'dp': None, 'h': 0, 'l': 0, 'o': 0, 'pc': 0, 't': 0}
    # exceeding the api limit raises the following exception:
    #   FinnhubAPIException(status_code: 429): API limit reached. Please try again later. Remaining Limit: 0
    def quote(self, symbol):
        api_result = {}
        # print("quote({})".format(symbol))
        try:
            # Get the current date in the required format
            current_date = datetime.now().strftime("%Y-%m-%d")

            # Retrieve the stock record
            stock = Stock.objects.filter(ticker=symbol).first()

            api_result = super().quote(symbol)
            # print("api_result = ", api_result)

            # store this stock quote in the database in case we need it later
            sq, created = StockQuote.objects.update_or_create(stock=stock, date=current_date, defaults={
                'current_price': api_result['c'], 'change': api_result['d'], 'percent_change': api_result['dp'],
                'high_price': api_result['h'], 'low_price': api_result['l'], 'open_price': api_result['o'],
                'prev_close_price': api_result['pc'], 'time_stamp': api_result['t']
            })

            if created:
                print('Created StockQuote "{}"'.format(sq))

        except (FinnhubAPIException, FinnhubRequestException):
            # Pull most recent stored values from database.
            sq = StockQuote.objects.filter(stock=stock, date=current_date).first()

            if sq:
                # Populate dictionary with database values that were just retrieved
                api_result['pc'] = sq.prev_close_price
                api_result['d'] = sq.change
                api_result['c'] = sq.current_price
                api_result['dp'] = sq.percent_change
                api_result['h'] = sq.high_price
                api_result['l'] = sq.low_price
                api_result['o'] = sq.open_price
                api_result['t'] = sq.time_stamp
                print("api failed - using quote found in db - quote({}) = {} ".format(symbol, api_result))
            else:
                # Didn't find an old quote in the database so populate dictionary with random values
                api_result['pc'] = round(random.uniform(33.33, 333.33), 2)
                api_result['d'] = round(random.uniform(-10.0, 10.0), 2)
                api_result['c'] = round(api_result['pc'] + api_result['d'], 2)
                api_result['dp'] = round(api_result['d'] / api_result['pc'] * 100.0, 4)
                api_result['h'] = round(api_result['c'] + random.uniform(1.0, 10.0), 2)
                api_result['l'] = round(api_result['c'] + random.uniform(-1.0, -10.0), 2)
                api_result['o'] = round(api_result['c'] + random.uniform(-1.0, 1.0), 2)
                api_result['t'] = int(time.time())  # Current time in seconds since the epoch
                print("api failed - no quote found in db - quote({}) = {} ".format(symbol, api_result))

        except Exception as e:
            print("quote({}) - api failed - uncaught exception {} ".format(symbol, e))
            raise e

        if not api_result or any(key not in api_result for key in ('c', 'o', 'h', 'l')):
            raise ValueError(f"No quote available for symbol {symbol}")

        return api_result

    # todo: might need to add overrides for stock_candles, company_profile2, company_news to handle exceeding api limit
