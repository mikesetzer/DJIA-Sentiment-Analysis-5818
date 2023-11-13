# home/management/commands/load_db_with_stocks.py
from django.core.management.base import BaseCommand
from home.models import Stock
from django.conf import settings
import os
import csv

class Command(BaseCommand):
    help = 'Load stocks from DJIAStockList.csv and update the database.'

    def handle(self, *args, **options):
        # Define the path to your CSV file
        csv_file_path = os.path.join(settings.BASE_DIR, 'dataload', 'DJIAStockList.csv')

        # Get the current list of stocks from the database
        existing_stocks = set(Stock.objects.values_list('ticker', flat=True))

        # Counter for statistics
        created_count = 0
        updated_count = 0
        removed_count = 0

        try:
            # Use Python's built-in CSV reader to process the file
            with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    ticker = row['ticker']
                    company = row['company']

                    # Create a new stock entry or update the existing one
                    stock, created = Stock.objects.update_or_create(
                        ticker=ticker,  # look up by ticker
                        defaults={'company': company}  # fields to update
                    )

                    # Update the counters
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                    # Remove the ticker from the existing stocks set
                    if ticker in existing_stocks:
                        existing_stocks.remove(ticker)

            # Remove stocks that are no longer in the CSV file
            removed_count = Stock.objects.filter(ticker__in=existing_stocks).delete()[0]

            # Print summary of the operation
            self.stdout.write(self.style.SUCCESS(
                f'Operation completed. {created_count} stocks created, {updated_count} stocks updated, {removed_count} stocks removed.'
            ))

        except Exception as e:
            # If an error occurs during the process, print it to the console
            self.stdout.write(self.style.ERROR(f'An error occurred during the stock loading process: {e}'))
