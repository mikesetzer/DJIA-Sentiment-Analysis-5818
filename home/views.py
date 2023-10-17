from django.shortcuts import render
from django.http import HttpResponse
from finnhub import Client
import os
from datetime import datetime
import time


# Create your views here.

def home_view(request):
    # Setup client
    finnhub_api_key = os.getenv('FINNHUB_API_KEY')  # Make sure this is set in your environment variables
    finnhub_client = Client(api_key=finnhub_api_key)

    # Hardcoded list of stock symbols and corresponding company names
    stock_symbols_and_names = {
        'AAPL': 'Apple Inc.',
        'AXP': 'American Express Company',
        'BA': 'The Boeing Company',
        'CAT': 'Caterpillar Inc.',
        'CRM': 'Salesforce.com, Inc.',
        'CSCO': 'Cisco Systems, Inc.',
        'CVX': 'Chevron Corporation',
        'DIS': 'The Walt Disney Company',
        'DOW': 'Dow Inc.',
        'GS': 'The Goldman Sachs Group, Inc.',
        'HD': 'The Home Depot, Inc.',
        'IBM': 'International Business Machines Corporation',
        'INTC': 'Intel Corporation',
        'JNJ': 'Johnson & Johnson',
        'JPM': 'JPMorgan Chase & Co.',
        'KO': 'The Coca-Cola Company',
        'MCD': "McDonald's Corporation",
        'MMM': '3M Company',
        'MRK': 'Merck & Co., Inc.',
        'MSFT': 'Microsoft Corporation',
        'NKE': 'NIKE, Inc.',
        'PG': 'The Procter & Gamble Company',
        'TRV': 'The Travelers Companies, Inc.',
        'UNH': 'UnitedHealth Group Incorporated',
        'V': 'Visa Inc.',
        'VZ': 'Verizon Communications Inc.',
        'WBA': 'Walgreens Boots Alliance, Inc.',
        'WMT': 'Walmart Inc.',
        'XOM': 'Exxon Mobil Corporation'
    }

    stocks_list = []

    for symbol, company_name in stock_symbols_and_names.items():
        # Fetch stock quote
        quote = finnhub_client.quote(symbol)

        if quote:
            # Calculate change and percent_change
            change = quote['c'] - quote['pc']
            percent_change = (change / quote['pc']) * 100 if quote['pc'] else 0

            stock_info = {
                'symbol': symbol,
                'name': company_name,  # Using the hardcoded company name
                'price': '${:.2f}'.format(quote['c']),
                'change': '$ {:.2f}'.format(change),
                'percent_change': f'{percent_change:.2f}%',
                'low': '${:.2f}'.format(quote['l']),
                'high': '${:.2f}'.format(quote['h']),
                'prev_close': '${:.2f}'.format(quote['pc']),
            }

            stocks_list.append(stock_info)

    context = {
        'stocks_list': stocks_list,
    }

    return render(request, 'stocks_list.html', context)


def stock_detail_view(request, symbol):
    finnhub_api_key = os.environ.get('FINNHUB_API_KEY')

    if finnhub_api_key is None:
        raise ValueError("API Key for Finnhub is missing!")

    finnhub_client = Client(api_key=finnhub_api_key)

    # Get general information about the company
    company_info = finnhub_client.company_profile2(symbol=symbol)
    if not company_info or 'name' not in company_info:
        raise ValueError(f"No data available for symbol {symbol}")

    # Get the current quote for the stock
    quote = finnhub_client.quote(symbol)
    if not quote or any(key not in quote for key in ('c', 'o', 'h', 'l')):
        raise ValueError(f"No quote available for symbol {symbol}")

    # Assuming 'recommendation' is calculated somehow based on available data
    recommendation = "Buy"  # Placeholder, you should implement your logic here

    # Calculate the percent change between the current price and the previous close price.
    # Make sure 'previous_close' is available and is a float to avoid a ZeroDivisionError.
    if quote.get('pc') and isinstance(quote.get('o'), float):
        percent_change = ((quote['c'] - quote['o']) / quote['o']) * 100  # This can be negative if the price decreased
    else:
        percent_change = None  # or some default value, or raise an exception

    # Market capitalization is typically represented in millions of dollars in financial data.
    # We'll convert it to billions and round to two decimal places. If the market cap is not available,
    # we default to 'N/A'. You may need to adjust this based on how your data is represented.

    market_cap_in_billions = None
    if company_info.get('marketCapitalization') is not None:
        market_cap_in_millions = company_info['marketCapitalization']
        market_cap_in_billions = round(market_cap_in_millions / 1000, 2)  # Convert to billions

    # Construct the stock information dictionary
    stock = {
        'name': company_info['name'],
        'symbol': symbol,
        'recommendation': recommendation,
        'price': quote['c'],
        'previous_close': quote['pc'],
        'percent_change': f'{percent_change:.2f}' if percent_change is not None else 'N/A',
        'market_cap': f'{market_cap_in_billions}' if market_cap_in_billions is not None else 'N/A',
        'open_price': quote['o'],
        'high_price': quote['h'],
        'low_price': quote['l'],
    }

    # Get the current date in the required format
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Fetch news with a limit
    news_params = {
        'symbol': symbol,
        '_from': "2022-01-01",  # Consider making this dynamic as well
        'to': current_date
    }
    news_list = finnhub_client.company_news(**news_params)
    if news_list is None or isinstance(news_list, dict):
        news_list = []  # or handle it appropriately, maybe there was an error

    current_timestamp = int(time.time())  # Current time in seconds since the epoch
    ten_days_ago_timestamp = current_timestamp - (10 * 24 * 60 * 60)  # 10 days ago

    # Fetching candlestick data
    candlestick_data = finnhub_client.stock_candles(
        symbol=symbol,
        resolution='D',
        _from=ten_days_ago_timestamp,  # 10 days ago
        to=current_timestamp
    )

    # Validate candlestick data and prepare it for the frontend
    if not candlestick_data or candlestick_data['s'] != 'ok':
        prepared_candlestick_data = []  # Handle the lack of data appropriately
    else:
        # Structure of the candlestick data is different, we need to adjust the data parsing
        prepared_candlestick_data = []
        for i in range(len(candlestick_data['c'])):
            ohlcv = {
                'timestamp': candlestick_data['t'][i],
                'open': candlestick_data['o'][i],
                'high': candlestick_data['h'][i],
                'low': candlestick_data['l'][i],
                'close': candlestick_data['c'][i],
                'volume': candlestick_data['v'][i]  # if volume data is needed
            }
            prepared_candlestick_data.append(ohlcv)

    context = {
        'stock': stock,
        'news_list': news_list[:3],  # Limiting to 5 news items
        'candlestick_data': prepared_candlestick_data,  # This can be used by a JS charting library
    }

    return render(request, 'stock_detail.html', context)
