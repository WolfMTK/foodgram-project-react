from rest_framework import viewsets, permissions, decorators, response, status
from rest_framework.generics import get_object_or_404

from core.pagination import PageNumberAndLimit
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
            return response.Response(
                self._get_favorite_data(request, pk, *args, **kwargs),
                status.HTTP_201_CREATED,
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
            return response.Response(
                self._get_cart_data(request, pk, *args, **kwargs),
                status.HTTP_201_CREATED,
            )
        cart = Cart.objects.filter(user_id=request.user.id, recipe_id=pk)
        if not cart.exists():
            return response.Response(
                {'error': 'Нет рецепта в списках покупок!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return response.Response(
            ListRecipeSerializer(serializer.save()).data,
            status.HTTP_201_CREATED,
        )

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (permissions.AllowAny(),)
        elif self.action in ('destroy',):
            return (IsAuthorPermission(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('create',):
            return RecipeCreatedSerializer
        return ListRecipeSerializer

    def _get_favorite_data(self, request, pk=None, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoriteSerializer(
            data={'user': request.user, 'recipe': recipe}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return RecipeSerializer(recipe).data

    def _get_cart_data(self, request, pk=None, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = CartSerializer(
            data={'user': request.user, 'recipe': recipe}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return RecipeSerializer(recipe).data
