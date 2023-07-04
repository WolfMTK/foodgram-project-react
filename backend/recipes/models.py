from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

from tags.models import Tag
from ingredients.models import Ingredient

User = get_user_model()


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
    ingredients = models.ManyToManyField(
        Ingredient,
        blank=True,
        related_name='recipes',
        verbose_name='Ингредиенты',
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

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

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
