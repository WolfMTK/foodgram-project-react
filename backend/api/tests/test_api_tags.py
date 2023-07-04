from rest_framework import status
from rest_framework.test import APITestCase

from tags.models import Tag
from .utils import check_list_and_id_tags, check_validate_data


class TagsApiTest(APITestCase):
    URL = '/api/tags/'
    VALIDE_DATA = (
        ['кулинария', 'EE9933', 'cooking'],
        ['еда', '5F3D14', 'meal'],
        ['вкусно', 'EFEBE7', 'delicious'],
        ['рецепты', 'BFBCB8', 'recipes'],
        ['завтрак', 'C5C2BF', 'breakfast'],
        ['обед', '4E4D4C', 'lunch'],
        ['ужин', '343433', 'dinner'],
    )
    FIELDS = ['name', 'color', 'slug']

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        tags = []
        for tag in cls.VALIDE_DATA:
            data = {}
            for value in zip(cls.FIELDS, tag):
                data[value[0]] = value[1]
            tags.append(Tag(**data))
        Tag.objects.bulk_create(tags)

    def test_getting_list_tags(self):
        """Проверка получения списка тегов."""
        request = self.client.get(self.URL)
        self.assertEqual(
            request.status_code,
            status.HTTP_200_OK,
            f'С {self.URL} возвращается неверный код! '
            'Не приходят данные при запросе!',
        )
        result = request.json()[0]
        check_validate_data(
            self, self.URL, check_list_and_id_tags, result
        )

    def test_getting_tag_id(self):
        """Проверка получения тега по id."""
        url = self.URL + f'{Tag.objects.first().id}/'
        request = self.client.get(url)
        self.assertEqual(
            request.status_code,
            status.HTTP_200_OK,
            f'Неверный код при получении данных с {url}!'
            'Не приходят данные при запросе!',
        )
        check_validate_data(
            self, self.URL, check_list_and_id_tags, request.json()
        )
        url = self.URL + f'{Tag.objects.last().id + 1}/'
        request = self.client.get(url)
        self.assertEqual(
            request.status_code,
            status.HTTP_404_NOT_FOUND,
            'Неверный код при получении данных с '
            f'несуществующей странице: {url}!',
        )
