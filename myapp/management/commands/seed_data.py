import pandas as pd
from django.core.management.base import BaseCommand
from myapp.models import Pokemon, PokemonType, DataRun


class Command(BaseCommand):
    help = 'Load Pokemon data from CSV'

    def handle(self, *args, **kwargs):
        df = pd.read_csv('data/pokemon.csv')

        run = DataRun.objects.create(source='csv')

        for _, row in df.iterrows():
            p_type, _ = PokemonType.objects.get_or_create(name=row['type_1'])

            
            Pokemon.objects.get_or_create(
                name=row['name'],
                primary_type=p_type,
                defaults={
                    'hp': row['hp'],
                    'data_run': run
                }
            )
            

        self.stdout.write("Seed complete")
