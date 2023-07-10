import logging
from pathlib import Path
from csv import reader

from django.core.management import BaseCommand

from ingredients.models import Ingredient
from .exceptions import PathDirError


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Команда загрузки данных в модель ингредиенты."""

    def add_arguments(self, parser) -> None:
        parser.add_argument('-p', '--path', type=str, help='Path to data')

    def handle(self, *args, **options):
        path = options.get('path')
        if not path or not Path(path).is_dir():
            msg = 'Ошибка! Не найдена папка data!'
            logger.error(msg)
            raise PathDirError(msg)
        self.stdout.write('Загрузка данных: ингредиенты!')
        self._load_data(path)
        self.stdout.write('Загрузка данных завершена!')

    def _load_data(self, path):
        with open(
            f'{path}ingredients.csv', mode='r', encoding='utf-8'
        ) as file:
            read_file = reader(file)
            if next(read_file) in ['name', 'measurement_unit']:
                file = read_file
            for row in reader(file):
                Ingredient.objects.get_or_create(
                    name=row[0], measurement_unit=row[1]
                )
