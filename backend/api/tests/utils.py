from rest_framework import status

check_list_and_id_users = (
    'id',
    'email',
    'username',
    'first_name',
    'last_name',
    'is_subscribed',
)

check_signup_user = {
    'email': 'testemail@yandex.ru',
    'username': 'UserTestName',
    'first_name': 'TestFirstName',
    'last_name': 'TestLastName',
}

check_list_and_id_tags = ('id', 'name', 'color', 'slug')

check_list_and_id_ingredients = ('id', 'name', 'measurement_unit')

valide_data_for_signup_user = {
    'email': 'testemail@yandex.ru',
    'username': 'UserTestName',
    'first_name': 'TestFirstName',
    'last_name': 'TestLastName',
    'password': 'TestPassword!3842_13',
}

invalid_data_by_signup_user = {
    'username': {
        'email': 'testemail@yandex.ru',
        'first_name': 'TestFirstName',
        'last_name': 'TestLastName',
        'password': 'TestPassword!3842_13',
    },
    'email': {
        'username': 'UserTestName',
        'first_name': 'TestFirstName',
        'last_name': 'TestLastName',
        'password': 'TestPassword!3842_13',
    },
    'first_name': {
        'email': 'testemail@yandex.ru',
        'username': 'UserTestName',
        'last_name': 'TestLastName',
        'password': 'TestPassword!3842_13',
    },
    'last_name': {
        'email': 'testemail@yandex.ru',
        'username': 'UserTestName',
        'first_name': 'TestFirstName',
        'password': 'TestPassword!3842_13',
    },
    'password': {
        'email': 'testemail@yandex.ru',
        'username': 'UserTestName',
        'first_name': 'TestFirstName',
        'last_name': 'TestLastName',
    },
    'invalid_data': {
        'email': 'testemail@yandex.ru',
        'username': 'UserTestName',
        'first_name': 'TestFirstName',
        'last_name': 'TestLastName',
        'password': 'Test1',
    },
}

invalid_data_change_password = (
    {'password': 'TestPassword'},
    {'new_password': 'TestNewPassword'},
    {'current_password': 'TestNewPassword'},
)


def check_validate_data(cls, url, data, result):
    """Проверка валидных данных."""
    ignore_filds = ('is_subscribed',)
    for value in data:
        with cls.subTest(value=value):
            cls.assertIn(
                value,
                result,
                f'Нет ключа {value} при запросе к {url}!',
            )
            if value not in ignore_filds:
                cls.assertTrue(
                    result.get(value),
                    f'Для ключа {value} возвращаются пустые данные '
                    f'при запросе к {url}!',
                )


def check_page(cls, url, request, limit):
    """Проверка пагинации."""
    data = ('count', 'next', 'previous', 'results')
    for value in data:
        with cls.subTest(value=value):
            cls.assertIn(
                value,
                request.json(),
                f'Пагинация работает неправильно для {url}!',
            )
    results = request.json().get('results')
    cls.assertEqual(
        len(results),
        limit,
        f'Для {cls.URL} не работает пагинация!',
    )


def get_token(cls, email, password):
    data = {'email': email, 'password': password}
    request = cls.client.post('/api/auth/token/login/', data)
    cls.assertEqual(
        request.status_code,
        status.HTTP_200_OK,
        'Пользователь не получает токен!',
    )
    token = request.json().get('auth_token')
    return token


def check_profile_user(cls, url, password, email):
    """Проверка профиля поьзователя."""
    request_anonym_user = cls.client.get(url)
    request_authorized_user = cls.authorized_user.get(url)
    cls.assertEqual(
        request_anonym_user.status_code,
        status.HTTP_401_UNAUTHORIZED,
        'Возвращается неверный код для анонимного пользователя '
        f'при обращении к {url}!',
    )
    cls.assertEqual(
        request_authorized_user.status_code,
        status.HTTP_401_UNAUTHORIZED,
        'Возвращается неверный код для пользователя не имеющего токен '
        f'при обращении к {url}!',
    )
    token = get_token(cls, email, password)
    client = cls.client
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    request = client.get(url)
    cls.assertEqual(
        request.status_code,
        status.HTTP_200_OK,
        'Возвращается неверный код для пользователя с токеном '
        f'при обращении к {url}',
    )
    result = request.json()
    check_validate_data(cls, url, check_list_and_id_users, result)
    client.logout()
