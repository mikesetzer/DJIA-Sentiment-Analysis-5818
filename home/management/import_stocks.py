from django.core.management.base import BaseCommand
from home.views import load_db_with_stocks  # Adjust the import statement if your function is in a different location

class Command(BaseCommand):
    help = 'Import stocks data into the database'

    def handle(self, *args, **options):
        # Adding some output to the console to indicate the script is running
        self.stdout.write('Starting to import stocks...')

        try:
            # Call your import function
            load_db_with_stocks()

            # Indicate success
            self.stdout.write(self.style.SUCCESS('Successfully imported stocks!'))

        except Exception as e:
            # If the function call failed, print the error to the console
            self.stdout.write(self.style.ERROR('Failed to import stocks: {}'.format(e)))
