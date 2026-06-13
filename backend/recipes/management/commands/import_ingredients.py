import json
import os

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из JSON'

    def handle(self, *args, **options):
        file_path = '/app/data/ingredients.json'
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Файл не найден: {file_path}'))
            return
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        objs = [
            Ingredient(name=i['name'],
                           measurement_unit=i[
                               'measurement_unit']) for i in data]
        Ingredient.objects.bulk_create(objs, ignore_conflicts=True)
        self.stdout.write(self.style.SUCCESS('Готово!'))
