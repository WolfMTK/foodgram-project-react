from rest_framework import viewsets, permissions

from api.filters import BackendSearchFilter
from .models import Ingredient
from .serializers import IngredientSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (BackendSearchFilter,)
    search_fields = ('$name',)
