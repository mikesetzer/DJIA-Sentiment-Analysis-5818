# python.exe .\manage.py loadcsv --csv .\stocks\management\commands\InitialDJIAStockData.csv
# python.exe .\manage.py loadcsv --csv .\stocks\management\commands\sentiment.csv
# python.exe .\manage.py loadcsv --csv .\stocks\management\commands\recommendation.csv

import csv
import re
from datetime import datetime

# from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from stocks.models import Stock, Portfolio, SentimentScore, Recommendation


class Command(BaseCommand):
    help = 'Load the stock data from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('--csv', type=str)

    @staticmethod
    def row_to_dict(row, header):
        if len(row) < len(header):
            row += [''] * (len(header) - len(row))
        return dict([(header[i], row[i]) for i, head in enumerate(header) if head])

    def handle(self, *args, **options):
        m = re.compile(r'content:(\w+)')
        header = None
        models = dict()

        try:
            with open(options['csv']) as csvfile:

                model_data = csv.reader(csvfile)

                for i, row in enumerate(model_data):
                    # print("debug: i = ", i)
                    if max([len(cell.strip()) for cell in row[1:] + ['']]) == 0 and m.match(row[0]):
                        model_name = m.match(row[0]).groups()[0]

                        models[model_name] = []
                        header = None
                        continue

                    if header is None:
                        header = row
                        continue

                    row_dict = self.row_to_dict(row, header)
                    if set(row_dict.values()) == {''}:
                        continue
                    models[model_name].append(row_dict)

        except FileNotFoundError:
            raise CommandError('File "{}" does not exist'.format(options['csv']))

        for data_dict in models.get('Stock', []):
            s, created = Stock.objects.get_or_create(ticker=data_dict['stock_ticker'],
                                                     defaults={'company': data_dict['stock_company']})

            if created:
                print('Created Stock "{}"'.format(s.ticker))

        for data_dict in models.get('Portfolio', []):
            p, created = Portfolio.objects.get_or_create(name=data_dict['portfolio_name'],
                                                         defaults={'description': data_dict['portfolio_description']})

            if created:
                print('Created Portfolio "{}"'.format(p.name))

        for data_dict in models.get('PortfolioStocks', []):
            portfolio = Portfolio.objects.get(name=data_dict['portfolio_stocks_portfolio'])
            stock = Stock.objects.get(ticker=data_dict['portfolio_stocks_stock'])
            # ps, created = PortfolioStocks.objects.get_or_create(portfolio=portfolio, stock=stock)
            portfolio.stocks.add(stock)
            # if created:
            print('Created PortfolioStocks "{}" -> "{}"'.format(portfolio.name, stock.ticker))

        for data_dict in models.get('SentimentScore', []):

            stock = Stock.objects.get(company=data_dict['sentiment_score_company'])

            # Need to convert date format from "01/14/2022" to "2022-01-14"
            sentiment_score_date = datetime.strptime(data_dict['sentiment_score_date'], '%m/%d/%Y').date().strftime(
                '%Y-%m-%d')

            ss, created = SentimentScore.objects.get_or_create(stock=stock, date=sentiment_score_date,
                                                               defaults={'score': data_dict['sentiment_score_score'],
                                                                         'recommendation': data_dict[
                                                                             'sentiment_score_recommendation']})

            if created:
                print('Created SentimentScore "{}" "{}" "{}" "{}"'.format(stock.ticker, ss.date, ss.score,
                                                                          ss.recommendation))

        for data_dict in models.get('Recommendation', []):

            # print('Started Recommendation "{}"'.format(data_dict['symbol']))

            stock = Stock.objects.get(ticker=data_dict['symbol'])

            # Need to convert date format from "01/14/2022" to "2022-01-14"
            # recommendation_date = datetime.strptime(data_dict['date'], '%m/%d/%Y').date().strftime('%Y-%m-%d')
            recommendation_date = data_dict['date']

            rec, created = Recommendation.objects.get_or_create(stock=stock, date=recommendation_date, defaults={

                'primary_key_text': data_dict['primary_key'], 'sentiment_score': data_dict['sentiment_score'],
                'stock_recommendation': data_dict['stock_rec'], 'total_recommendation': data_dict['total_rec']

            })

            if created:
                print('Created Recommendation "{}" "{}" "{}" "{}" "{}"'.format(stock.ticker, rec.date,
                                                                               rec.sentiment_score,
                                                                               rec.stock_recommendation,
                                                                               rec.total_recommendation))

        print("Import complete")
