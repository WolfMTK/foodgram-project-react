from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from colorfield import fields

from ingredients.models import Ingredient

User = get_user_model()


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Название',
        unique=True,
    )
    color = fields.ColorField(format='hex', verbose_name='Цвет в HEX')
    slug = models.SlugField(
        max_length=200,
        blank=False,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='recipes',
        verbose_name='Тег',
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    text = models.TextField(verbose_name='Описание')
    image = models.ImageField(
        upload_to='foods/images/',
        null=True,
        default=None,
    )
    cooking_time = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=(MinValueValidator(1),),
        verbose_name='Время приготовления (в минутах)',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата создания',
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created']

    def __str__(self):
        return self.name


class Cart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='Рецепт',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_carts', fields=['user', 'recipe']
            ),
        ]


class Favorite(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_favorites', fields=['user', 'recipe']
            ),
        ]


class AmountIngredient(models.Model):
    """Модель количества ингредиентов."""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amounts',
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amounts',
        verbose_name='Рецепт',
    )
    amount = models.PositiveIntegerField(
        blank=True,
        null=True,
        validators=(MinValueValidator(1),),
        verbose_name='Количество',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_recipe_and_ingredient',
                fields=['ingredient', 'recipe'],
            ),
        ]
