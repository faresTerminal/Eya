import json
from django.core.management.base import BaseCommand
from orders.models import State, City

class Command(BaseCommand):
    help = 'Load cities and states of Algeria into the database from a JSON file'

    def handle(self, *args, **kwargs):
        # Path to your JSON file
        file_path = 'cities/cities.json'

        # Open and load the JSON data
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Iterate over each record in the JSON file
        for record in data:
            state_name = record['wilaya_name']
            city_name = record['commune_name']

            # Get or create the state (wilaya)
            state, created = State.objects.get_or_create(name=state_name, code=record['wilaya_code'])
            print(f"Created or found state: {state_name} (Code: {record['wilaya_code']})")
            
            # Create the city (commune) for that state
            city, city_created = City.objects.get_or_create(name=city_name, state=state)
            if city_created:
                print(f"Created city: {city_name} in state {state_name}")
            else:
                print(f"City {city_name} already exists in state {state_name}")

        self.stdout.write(self.style.SUCCESS('Successfully loaded all states and cities.'))
