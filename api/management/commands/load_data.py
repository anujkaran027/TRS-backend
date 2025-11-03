import csv
from django.core.management.base import BaseCommand
from api.models import Location
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
CSV_PATH = BASE_DIR / 'dataset.csv'

class Command(BaseCommand):
    help = 'Load data from CSV file into Django database'

    def handle(self, *args, **kwargs):
        if not CSV_PATH.exists():
            self.stdout.write(self.style.ERROR(f'CSV file not found at {CSV_PATH}'))
            return
    
        with open(CSV_PATH, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                Location.objects.create(name=row['Name'],
                                        zone=row['Zone'],
                                        state=row['State'],
                                        city=row['City'],
                                        entryprice=row['Entrance Fee in INR'],
                                        description=row['Type']
                                        )
        self.stdout.write(self.style.SUCCESS('Data loaded successfully'))