from rest_framework import filters
from django_filters.rest_framework import (FilterSet,
                                           AllValuesMultipleFilter,
                                           BooleanFilter)

from recipes.models import Recipe


class BackendSearchFilter(filters.SearchFilter):
    """Фильтр поиска."""

    search_param = 'name'


class RecipeFilter(FilterSet):
    """Фильтр рецептов."""

    tags = AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = BooleanFilter(method='get_favorited')
    is_in_shopping_cart = BooleanFilter(method='get_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def get_favorited(self, queryset, name, value):
        user = self.request.user
        return (
            queryset.filter(favorites__user=user)
            if value and not user.is_anonymous
            else queryset
        )

    def get_shopping_cart(self, queryset, name, value):
        user = self.request.user
        return (
            queryset.filter(carts__user=user)
            if value and not user.is_anonymous
            else queryset
        )
