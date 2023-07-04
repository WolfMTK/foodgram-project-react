from django.contrib import admin

from .models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для модели Ingredient."""

    ordering = ('name',)
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
