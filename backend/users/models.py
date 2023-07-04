from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator


class User(AbstractUser):
    """Модель пользователей."""

    username = models.CharField(
        max_length=150,
        unique=True,
        blank=True,
        validators=(UnicodeUsernameValidator,),
        verbose_name='Уникальный юзернейм',
        error_messages={
            'unique': 'Пользователь с таким юзернеймом уже существует!',
        },
    )
    email = models.EmailField(
        blank=True,
        unique=True,
        verbose_name='Адрес электронной почты',
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия',
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Пользователь',
    )
    subscribed = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribed',
        verbose_name='Подписчик',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                name='unique_subscription',
                fields=['user', 'subscribed'],
            ),
        ]
