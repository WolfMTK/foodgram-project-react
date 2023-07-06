from rest_framework import viewsets, permissions, decorators, response, status
from rest_framework.generics import get_object_or_404

from services.pagination import PageNumberAndLimit
from users.serializers import RecipeSerializer
from users.permissions import IsAuthorPermission
from .models import Recipe, Favorite, Cart
from .serializers import (
    ListRecipeSerializer,
    RecipeCreatedSerializer,
    FavoriteSerializer,
    CartSerializer,
)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    pagination_class = PageNumberAndLimit

    @decorators.action(detail=True, methods=('post', 'delete'))
    def favorite(self, request, pk=None, *args, **kwargs):
        if request.method == 'POST':
            return self._send_response_data(
                request, FavoriteSerializer, pk, *args, **kwargs
            )
        favorite = Favorite.objects.filter(
            user_id=request.user.id, recipe_id=pk
        )
        if not favorite.exists():
            return response.Response(
                {'error': 'Нет рецепта в избранных!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        favorite.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=True, methods=('post', 'delete'))
    def shopping_cart(self, request, pk=None, *args, **kwargs):
        if request.method == 'POST':
            return self._send_response_data(request, CartSerializer, pk)
        cart = Cart.objects.filter(user_id=request.user.id, recipe_id=pk)
        if not cart.exists():
            return response.Response(
                {'error': 'Нет рецепта в списках покупок!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (permissions.AllowAny(),)
        elif self.action in ('destroy', 'partial_update'):
            return (IsAuthorPermission(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreatedSerializer
        return ListRecipeSerializer

    def _send_response_data(self, request, serializer, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        # error handling: MultipleObjectsReturned
        if request.user == recipe.author:
            return response.Response(
                {'error': self._get_error_message(serializer())},
                status.HTTP_400_BAD_REQUEST,
            )
        serializer = serializer(data={'user': request.user, 'recipe': recipe})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(
            RecipeSerializer(recipe).data,
            status.HTTP_201_CREATED,
        )

    def _get_error_message(self, serializer):
        if type(serializer).__name__ == 'FavoriteSerializer':
            return 'Собственный рецепт невозможно добавить в избранное!'
        elif type(serializer).__name__ == 'CartSerializer':
            return 'Собственный рецепт невозможно добавить в список покупок!'
        return 'Произошла ошибка!'
