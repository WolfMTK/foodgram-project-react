from rest_framework import status
from rest_framework.test import APITestCase

from ingredients.models import Ingredient
from .utils import check_list_and_id_ingredients, check_validate_data


# consts
INDEX = 100
SEARCH_FILTER = 'name'
NAME = 'TestName'


class IngredientAPITest(APITestCase):
    URL = '/api/ingredients/'

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        Ingredient.objects.bulk_create(
            [
                Ingredient(name=f'{NAME}{i}', measurement_unit=f't{i}')
                for i in range(INDEX)
            ]
        )

    def test_getting_list_ingredients(self):
        """Проверка получения списка ингредиентов."""
        request = self.client.get(self.URL)
        self.assertEqual(
            request.status_code,
            status.HTTP_200_OK,
            f'С {self.URL} возвращается неверный код! '
            'Не приходят данные при запросе!',
        )
        result = request.json()[0]
        check_validate_data(
            self, self.URL, check_list_and_id_ingredients, result
        )
        url = self.URL + f'?{SEARCH_FILTER}={NAME.lower()}{INDEX - 10}'
        request = self.client.get(url)
        self.assertEqual(
            request.status_code,
            status.HTTP_200_OK,
            f'С {self.URL} возвращается неверный код! '
            'Не приходят данные при запросе!',
        )
        self.assertTrue(
            request.json(), f'Не работает фильтрация для {self.URL}!'
        )

    def test_getting_ingredient_id(self):
        """Проверка получения ингредиента по id."""
        url = self.URL + f'{Ingredient.objects.first().id}/'
        request = self.client.get(url)
        self.assertEqual(
            request.status_code,
            status.HTTP_200_OK,
            f'Неверный код при получении данных с {url}!'
            'Не приходят данные при запросе!',
        )
        check_validate_data(
            self, url, check_list_and_id_ingredients, request.json()
        )
        url = self.URL + f'{Ingredient.objects.last().id + 1}/'
        request = self.client.get(url)
        self.assertEqual(
            request.status_code,
            status.HTTP_404_NOT_FOUND,
            'Неверный код при получении данных с '
            f'несуществующей странице: {url}!',
        )
