# Foodgram

На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

Проект доступен по адресу: [foodgram](https://foodgramfoods.ddns.net/)

### Технологии

- python

- Django

- Django REST Framework

- Docker

- Postgres

### Запуск проекта

1. Запустите Docker Compose (для linux от `sudo` вводить команды): `docker compose -f docker-compose.production.yml up`

2. Проверьте, что страница заработала:

`http://localhost:8080/`

`http://localhost:8080/api/`

`http://localhost:8080/admin/`

`http://localhost:8080/api/docs/`

### Другие параметры

1. Создание superuser:

`docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser`

2. Загрузка данных (рецепты):

`docker compose -f docker-compose.production.yml exec backend python manage.py load_data -p path_ingredients_csv`

### Вход в админку

Логин: Alexander

Пароль: Dbu7-Qskf12_sifs12

### Пример заполнения файла .env

Пример заполнения: [.env](https://github.com/WolfMTK/foodgram-project-react/blob/master/.env.example)

### Примеры запросов

1. [Регистрация пользователя](https://foodgramfoods.ddns.net/api/users/) (POST-запрос)

|Поле      |Описание               |
|----------|-----------------------|
|email     |Адрес электронной почты|
|username  |Уникальный юзернейм    |
|first_name|Имя                    |
|last_name |Фамилия                |
|password  |Пароль                 |

Запрос: POST

Пример:

```
{
    "email": "ivan.ivanov@yandex.ru",
    "username": "ivan",
    "first_name": "Ivan",
    "last_name": "Ivanov",
    "password": "Qwerty123"
}
```

201 - пользователь успешно создан;

400 - ошибка валидации.

2. [Изменение пароля](https://foodgramfoods.ddns.net/api/users/set_password/) (POST-запрос)

|Поле              |Описание               |
|------------------|-----------------------|
|new_password      |Новый пароль           |
|current_password  |Старый пароль          |

Пример:

```
{
    "new_password": "Qwerty1234",
    "current_password": "Qwerty123"
}
```

204 - пароль успешно изменен;

400 - ошибка валидации;

401 - пользователь не авторизован.

3. [Получение токена авторизации](https://foodgramfoods.ddns.net/api/auth/token/login/) (POST-запрос)

|Поле              |Описание               |
|------------------|-----------------------|
|password          |Пароль                 |
|email             |Адрес электронной почты|

Пример:
```
{
    "password": "Qwerty1234",
    "email": "ivan.ivanov@yandex.ru"
}
```

200 - токен создан и получен;

400 - ошибка валидации;

401 - пользователь не авторизован.

4. [Удаление токена](https://foodgramfoods.ddns.net/api/auth/token/logout/) (POST-запрос)

204 - токен удален;

401 - пользователь не авторизован.

### Полная документация к API

Документация к API: [API_DOCS](https://foodgramfoods.ddns.net/api/docs/)
