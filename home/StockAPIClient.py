import random
import time

from finnhub import Client, FinnhubRequestException, FinnhubAPIException


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
            api_result = super().quote(symbol)
            # print("api_result = ", api_result)
        except (FinnhubAPIException, FinnhubRequestException) as error:
            # Populate dictionary with random values for now.
            # todo: Update to pull stored values from database.
            api_result['pc'] = round(random.uniform(33.33, 333.33), 2)
            api_result['d'] = round(random.uniform(-10.0, 10.0), 2)
            api_result['c'] = round(api_result['pc'] + api_result['d'], 2)
            api_result['dp'] = round(api_result['d'] / api_result['pc'] * 100.0, 4)
            api_result['h'] = round(api_result['c'] + random.uniform(1.0, 10.0), 2)
            api_result['l'] = round(api_result['c'] + random.uniform(-1.0, -10.0), 2)
            api_result['o'] = round(api_result['c'] + random.uniform(-1.0, 1.0), 2)
            api_result['t'] = int(time.time())  # Current time in seconds since the epoch
            print("api failed - quote({}) = {} ".format(symbol, api_result))
        except Exception as e:
            print("quote({}) - api failed - uncaught exception {} ".format(symbol, e))
            raise e

        if not api_result or any(key not in api_result for key in ('c', 'o', 'h', 'l')):
            raise ValueError(f"No quote available for symbol {symbol}")

        return api_result

    # todo: might need to add overrides for stock_candles, company_profile2, company_news to handle exceeding api limit
