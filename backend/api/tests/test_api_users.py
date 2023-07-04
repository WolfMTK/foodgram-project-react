from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status

from .utils import (
    check_list_and_id_users,
    check_validate_data,
    check_page,
    check_signup_user,
    invalid_data_by_signup_user,
    check_profile_user,
    get_token,
    invalid_data_change_password,
)


# Model User
User = get_user_model()

# consts
USER_NUMS = 100
LIMIT = 10
INDEX = 20


class UsersAPITest(APITestCase):
    URL = '/api/users/'
    TOKEN_URL = '/api/auth/token/'
    VALIDE_DATA_FOR_SIGNUP_USER = {
        'email': 'testemail@yandex.ru',
        'username': 'UserTestName',
        'first_name': 'TestFirstName',
        'last_name': 'TestLastName',
        'password': 'TestPassword!3842_13',
    }
    VALIDE_NEW_PASSWORD = {
        'new_password': 'TestNewPassword12',
        'current_password': 'TestPassword!3842_13',
    }

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        User.objects.bulk_create(
            [
                User(
                    username=f'TestUsername{i}',
                    email=f'test{i}email@email.ml',
                    last_name='TestLastName',
                    first_name='TestFirstName',
                )
                for i in range(USER_NUMS)
            ]
        )

    def setUp(self):
        self.user = User.objects.create_user(
            **self.VALIDE_DATA_FOR_SIGNUP_USER
        )
        self.authorized_user = self.client
        self.authorized_user.force_login(self.user)

    def test_getting_list_user(self):
        """
        Проверка получения данных списка пользователей.
        """
        self.user.delete()
        request = self.client.get(self.URL)
        self.assertEqual(
            request.status_code,
            status.HTTP_200_OK,
            f'Возвращается неверный статус при обращении к {self.URL}',
        )
        check_page(self, self.URL, request)
        results = request.json().get('results')
        self.assertEqual(
            len(results),
            LIMIT,
            f'Для {self.URL} не работает пагинация!',
        )
        check_validate_data(
            self, self.URL, check_list_and_id_users, results[0]
        )

    def test_signup_user(self):
        """Проверка регистрации аккаунта."""
        self.user.delete()
        request = self.client.post(
            self.URL,
            self.VALIDE_DATA_FOR_SIGNUP_USER,
        )
        self.assertEqual(
            request.status_code,
            status.HTTP_201_CREATED,
            f'Для {self.URL} возвращается неверный код при '
            'регистрации пользователя!',
        )
        user = User.objects.filter(
            username=self.VALIDE_DATA_FOR_SIGNUP_USER.get('username'),
            email=self.VALIDE_DATA_FOR_SIGNUP_USER.get('email'),
        ).first()
        data = dict(check_signup_user)
        data['id'] = user.id
        for key in data:
            with self.subTest(key=key):
                self.assertEqual(
                    request.json().get(key),
                    data.get(key),
                    f'Для {self.URL} приходят неверные данные '
                    'при регистрации пользователя!',
                )
        user.delete()
        for key, value in invalid_data_by_signup_user.items():
            with self.subTest(key=key):
                request = self.client.post(self.URL, value)
                self.assertEqual(
                    request.status_code,
                    status.HTTP_400_BAD_REQUEST,
                    f'При остутствии ключа {key} создается пользователь!',
                )

    def test_getting_user_id_and_me(self):
        """
        Проверка получения данных пользователя.
        """
        url = self.URL + f'{self.user.id - INDEX}/'
        password = self.VALIDE_DATA_FOR_SIGNUP_USER.get('password')
        email = self.VALIDE_DATA_FOR_SIGNUP_USER.get('email')
        check_profile_user(self, url, password, email)
        url = self.URL + f'{self.user.id}/'
        check_profile_user(self, url, password, email)
        url = self.URL + 'me/'
        check_profile_user(self, url, password, email)
        url = self.URL + f'{self.user.id + INDEX}/'
        request = self.client.get(url)
        self.assertEqual(
            request.status_code,
            status.HTTP_401_UNAUTHORIZED,
            f'Возвращается неверный код при обращении к странице {url}!',
        )
        client = self.client
        token = get_token(
            self,
            self.VALIDE_DATA_FOR_SIGNUP_USER.get('email'),
            self.VALIDE_DATA_FOR_SIGNUP_USER.get('password'),
        )
        client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        request = client.get(url)
        self.assertEqual(
            request.status_code,
            status.HTTP_404_NOT_FOUND,
            f'Возвращается неверный код при обращении к странице {url}!',
        )

    def test_changins_password(self):
        """Проверка изменения пароля."""
        client = self.client
        token = get_token(
            self,
            self.VALIDE_DATA_FOR_SIGNUP_USER.get('email'),
            self.VALIDE_DATA_FOR_SIGNUP_USER.get('password'),
        )
        client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        url = self.URL + 'set_password/'
        request = client.post(url, self.VALIDE_NEW_PASSWORD)
        self.assertEqual(
            request.status_code,
            status.HTTP_204_NO_CONTENT,
            f'Для {url} возвращается неверный код!',
        )
        for data in invalid_data_change_password:
            request = client.post(url, data)
            self.assertEqual(
                request.status_code,
                status.HTTP_400_BAD_REQUEST,
                f'Для {url} возвращается неверный код!',
            )
        client.logout()
        request = self.client.post(url, data)
        self.assertEqual(
            request.status_code,
            status.HTTP_401_UNAUTHORIZED,
            f'Для {url} возвращается неверный код!',
        )

    def test_getting_token(self):
        """Проверка получения токена."""
        token = get_token(
            self,
            self.VALIDE_DATA_FOR_SIGNUP_USER.get('email'),
            self.VALIDE_DATA_FOR_SIGNUP_USER.get('password'),
        )
        self.authorized_user.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        token = Token.objects.filter(
            user__username=self.VALIDE_DATA_FOR_SIGNUP_USER.get('username')
        ).first()
        self.assertTrue(token, 'Токен пользователя не сохраняется!')

    def test_deleting_token(self):
        """Проверка удаления токена."""
        token = get_token(
            self,
            self.VALIDE_DATA_FOR_SIGNUP_USER.get('email'),
            self.VALIDE_DATA_FOR_SIGNUP_USER.get('password'),
        )
        self.authorized_user.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        url = self.TOKEN_URL + 'logout/'
        self.authorized_user.post(url)
        token = Token.objects.filter(
            user__username=self.VALIDE_DATA_FOR_SIGNUP_USER.get('username')
        ).first()
        self.assertFalse(token, 'Токен пользователя не удаляется!')
