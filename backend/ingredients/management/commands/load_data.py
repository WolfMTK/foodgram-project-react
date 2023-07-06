import logging
from pathlib import Path
from csv import DictReader

from django.core.management import BaseCommand

from ingredients.models import Ingredient
from .exceptions import PathDirError


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Команда загрузки данных в модель ингредиенты."""

    def handle(self, *args, **options):
        if not Path('./data').is_dir():
            msg = 'Ошибка! Не найдена папка data'
            logger.error(msg)
            raise PathDirError(msg)
        self.stdout.write('Загрузка данных: ингредиенты!')
        with open(
            './data/ingredients.csv', mode='r', encoding='utg-8'
        ) as file:
            for row in DictReader(file):
                Ingredient.objects.get_or_create(
                    name=row.get('name'),
                    measurement_unit=row.get('measurement_unit'),
                )
            file.close()
