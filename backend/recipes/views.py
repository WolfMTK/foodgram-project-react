from rest_framework import viewsets, permissions, decorators, response, status
from rest_framework.generics import get_object_or_404
from django.db.models import Sum
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend

from api.filters import BackendSearchFilter, RecipeFilter
from api.pagination import PageNumberAndLimit
from users.serializers import UserRecipeSerializer
from api.permissions import IsAuthorPermission
from services.pdf_gen import PDFGeneratedCartList
from .models import Recipe, Favorite, Cart, AmountIngredient, Tag, Ingredient
from .serializers import (
    ListRecipeSerializer,
    RecipeCreatingSerializer,
    FavoriteAddingSerializer,
    CartAddingSerializer,
    TagSerializer,
    IngredientSerializer,
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (BackendSearchFilter,)
    search_fields = ('$name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet рецептов."""

    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('get', 'post', 'patch', 'delete')
    pagination_class = PageNumberAndLimit
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @decorators.action(detail=True, methods=('post', 'delete'))
    def favorite(self, request, pk=None, *args, **kwargs):
        if request.method == 'POST':
            return self._send_response_data(
                request, FavoriteAddingSerializer, pk, *args, **kwargs
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
            return self._send_response_data(request, CartAddingSerializer, pk)
        cart = Cart.objects.filter(user_id=request.user.id, recipe_id=pk)
        if not cart.exists():
            return response.Response(
                {'error': 'Нет рецепта в списках покупок!'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        cart.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(detail=False, methods=('get',))
    def download_shopping_cart(self, request, *args, **kwargs):
        ingredients = (
            AmountIngredient.objects.filter(recipe__carts__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(amount=Sum('amount'))
        )
        pdf_gen = PDFGeneratedCartList()
        pdf_gen.register_font()
        pdf_gen.set_title(request.user)
        pdf_gen.set_table(ingredients)
        pdf_gen.build()
        return FileResponse(
            pdf_gen.buffer,
            as_attachment=True,
            filename='shopping_cart.pdf',
        )

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (permissions.AllowAny(),)
        elif self.action in ('destroy', 'partial_update'):
            return (IsAuthorPermission(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreatingSerializer
        return ListRecipeSerializer

    def _send_response_data(self, request, serializer, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = serializer(data={'user': request.user, 'recipe': pk})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(
            UserRecipeSerializer(recipe).data,
            status.HTTP_201_CREATED,
        )
