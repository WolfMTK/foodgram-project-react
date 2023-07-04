from django.contrib import admin

from .models import Recipe, AmountIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('author', 'name', 'tags')


@admin.register(AmountIngredient)
class AmountIngredient(admin.ModelAdmin):
    list_display = ('id', 'amount')
