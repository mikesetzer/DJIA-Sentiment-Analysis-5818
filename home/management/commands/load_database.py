from django.core.management.base import BaseCommand
from home.views import load_db_with_stocks, load_db_with_recommendations
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Load initial stock and recommendation data into the database.'

    def handle(self, *args, **options):
        # Call the function to load stocks
        try:
            self.stdout.write('Loading stocks...')
            load_db_with_stocks()
            self.stdout.write(self.style.SUCCESS('Stocks have been loaded successfully.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred while loading stocks: {e}'))

        # Call the function to load recommendations
        try:
            csvfilename = os.path.join(settings.BASE_DIR, 'dataload', 'COP_DJIA_Total_Dataset.csv')
            self.stdout.write('Loading recommendations...')
            load_db_with_recommendations(csvfilename)
            self.stdout.write(self.style.SUCCESS('Recommendations have been loaded successfully.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred while loading recommendations: {e}'))
