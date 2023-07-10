from django.contrib import admin

from .models import Recipe, Tag


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка для рецептов."""

    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Админка для модели Tag."""

    ordering = ('name',)
