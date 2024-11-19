import csv
from django.core.management.base import BaseCommand
from webadmin.models import Category

class Command(BaseCommand):
    help = 'Bulk upload categories from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row
            for row in reader:
                name, description, icon, url = row
                Category.objects.create(
                    name=name,
                    description=description,
                    icon=icon,
                    url=url
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully added category {name}'))
