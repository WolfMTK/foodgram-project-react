from django.contrib import admin

from .models import Recipe, Tag, Ingredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецептов."""

    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для модели Tag."""

    ordering = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для модели Ingredient."""

    ordering = ('name',)
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
