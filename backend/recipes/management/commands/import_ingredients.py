import json
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из JSON'

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'ingredients.json')

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('Файл не найден!'))
            return

        ingredients_to_create = []
        for item in data:
            ingredients_to_create.append(
                Ingredient(
                    name=item.get('name'),
                    measurement_unit=item.get('measurement_unit')
                )
            )
        Ingredient.objects.bulk_create(ingredients_to_create, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Готово!'))
