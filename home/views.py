import csv
import os
import time
import logging
from datetime import datetime

from django.shortcuts import render, redirect
from home.StockAPIClient import StockAPIClient
from home.models import Stock, Recommendation
from django.conf import settings

logger = logging.getLogger(__name__)

def home_view(request):
    stocks_list = []
    if request.user.is_authenticated:
        finnhub_api_key = os.getenv('FINNHUB_API_KEY_STOCKS')
        if not finnhub_api_key:
            raise ValueError("API Key for Finnhub is missing!")

        finnhub_client = StockAPIClient(api_key=finnhub_api_key)
        stocks = Stock.objects.all().order_by('ticker')
        if not stocks:
            context = {'error': 'No stock information available.'}
        else:
            for stock in stocks:
                try:
                    quote = finnhub_client.quote(stock.ticker)
                    if quote and 'c' in quote and 'pc' in quote:
                        change = quote['c'] - quote['pc']
                        percent_change = (change / quote['pc']) * 100 if quote['pc'] else 0
                        stock_info = {
                            'symbol': stock.ticker,
                            'name': stock.company,
                            'price': '${:.2f}'.format(quote['c']),
                            'change': '$ {:.2f}'.format(change),
                            'percent_change': f'{percent_change:.2f}%',
                            'low': '${:.2f}'.format(quote.get('l', 0)),
                            'high': '${:.2f}'.format(quote.get('h', 0)),
                            'prev_close': '${:.2f}'.format(quote['pc']),
                        }
                        stocks_list.append(stock_info)
                except Exception as e:
                    logger.error(f"Error processing stock {stock.ticker}: {e}")

    context = {'stocks_list': stocks_list}
    template_path = os.path.join(settings.BASE_DIR, 'templates', 'stocks_list.html')
    return render(request, template_path, context)

def stock_detail_view(request, symbol):
    finnhub_api_key = os.getenv('FINNHUB_API_KEY_NEWS')
    if not finnhub_api_key:
        raise ValueError("API Key for Finnhub is missing!")

    finnhub_client = StockAPIClient(api_key=finnhub_api_key)
    company_info = finnhub_client.company_profile2(symbol=symbol)
    if not company_info or 'name' not in company_info:
        raise ValueError(f"No data available for symbol {symbol}")

    quote = finnhub_client.quote(symbol)
    if not quote or 'c' not in quote or 'o' not in quote or 'h' not in quote or 'l' not in quote:
        raise ValueError(f"No quote available for symbol {symbol}")

    recommendation = get_most_recent_stock_rec(symbol)
    sentiment = get_most_recent_stock_sentiment(symbol)

    percent_change = ((quote['c'] - quote['o']) / quote['o']) * 100 if quote.get('o') else None

    market_cap_in_billions = None
    if 'marketCapitalization' in company_info and company_info['marketCapitalization'] is not None:
        market_cap_in_millions = company_info['marketCapitalization']
        market_cap_in_billions = f'{round(market_cap_in_millions / 1000, 2)}B'

    stock = {
        'name': company_info['name'],
        'symbol': symbol,
        'recommendation': recommendation,
        'sentiment': sentiment,
        'price': quote['c'],
        'previous_close': quote['pc'],
        'percent_change': f'{percent_change:.2f}%' if percent_change is not None else 'N/A',
        'market_cap': market_cap_in_billions or 'N/A',
        'open_price': quote['o'],
        'high_price': quote['h'],
        'low_price': quote['l'],
    }

    current_date = datetime.now().strftime("%Y-%m-%d")
    news_params = {'symbol': symbol, '_from': "2022-01-01", 'to': current_date}
    news_list = finnhub_client.company_news(**news_params)
    if not news_list or isinstance(news_list, dict):
        news_list = []

    current_timestamp = int(time.time())
    ten_days_ago_timestamp = current_timestamp - (10 * 24 * 60 * 60)
    candlestick_data = finnhub_client.stock_candles(symbol=symbol, resolution='D', _from=ten_days_ago_timestamp, to=current_timestamp)
    if not candlestick_data or 's' not in candlestick_data or candlestick_data['s'] != 'ok':
        prepared_candlestick_data = []
    else:
        prepared_candlestick_data = [{'timestamp': candlestick_data['t'][i], 'open': candlestick_data['o'][i], 'high': candlestick_data['h'][i], 'low': candlestick_data['l'][i], 'close': candlestick_data['c'][i], 'volume': candlestick_data['v'][i]} for i in range(len(candlestick_data['c']))]

    context = {'stock': stock, 'news_list': news_list[:3], 'candlestick_data': prepared_candlestick_data}
    template_path = os.path.join(settings.BASE_DIR, 'templates', 'stock_detail.html')

    # Check if data is received
    if not candlestick_data or 's' not in candlestick_data or candlestick_data['s'] != 'ok':
        logger.error("Failed to fetch candlestick data")
        prepared_candlestick_data = []
    else:
        prepared_candlestick_data = [
            {'timestamp': candlestick_data['t'][i], 'open': candlestick_data['o'][i], 'high': candlestick_data['h'][i],
             'low': candlestick_data['l'][i], 'close': candlestick_data['c'][i], 'volume': candlestick_data['v'][i]} for
            i in range(len(candlestick_data['c']))]
        logger.info(f"Candlestick Data: {prepared_candlestick_data}")

    return render(request, template_path, context)

def load_db_view(request):
    load_db_with_stocks()
    csvfilename = os.path.join(settings.BASE_DIR, 'dataload', 'COP_DJIA_Total_Dataset.csv')
    if not os.path.exists(csvfilename):
        print("Error: CSV file does not exist.")
    else:
        load_db_with_recommendations(csvfilename)
    return redirect(home_view)

def load_db_with_stocks():
    csv_file_path = os.path.join(settings.BASE_DIR, 'dataload', 'DJIAStockList.csv')
    created_count = 0
    updated_count = 0
    try:
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                ticker = row['ticker']
                company = row['company']
                stock, created = Stock.objects.update_or_create(
                    ticker=ticker,
                    defaults={'company': company}
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1
        print(f'Operation completed. {created_count} stocks created, {updated_count} stocks updated.')
    except Exception as e:
        print(f'An error occurred during the stock loading process: {e}')

def load_db_with_recommendations(csvfilename):
    try:
        with open(csvfilename, mode='r') as csvfile:
            csv_reader = csv.DictReader(csvfile)
            for row in csv_reader:
                symbol = row['symbol']
                stock, _ = Stock.objects.get_or_create(ticker=symbol)
                recommendation_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                Recommendation.objects.get_or_create(
                    stock=stock,
                    date=recommendation_date,
                    defaults={
                        'sentiment_score': row['sentiment_score'],
                        'stock_recommendation': row['stock_rec'],
                        'total_recommendation': row['total_rec']
                    }
                )
        print("Recommendations data loaded successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

def get_most_recent_stock_rec(ticker):
    latest_recommendation = Recommendation.objects.filter(stock__ticker=ticker).order_by('-date').first()
    return latest_recommendation.total_recommendation.capitalize() if latest_recommendation else None

def get_most_recent_stock_sentiment(ticker):
    latest_recommendation = Recommendation.objects.filter(stock__ticker=ticker).order_by('-date').first()
    return latest_recommendation.sentiment_score.capitalize() if latest_recommendation else None
