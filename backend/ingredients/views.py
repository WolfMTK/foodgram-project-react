from rest_framework import viewsets, permissions

from .models import Ingredient
from .serializers import IngredientSerializer
from core.filters import BackendSearchFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (BackendSearchFilter,)
    search_fields = ('$name',)
