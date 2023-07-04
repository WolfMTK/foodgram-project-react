import base64

from rest_framework import serializers, validators
from django.core.files.base import ContentFile

from tags.serializers import TagSerializer
from users.serializers import UserModelSerializer
from users.models import User
from ingredients.models import Ingredient
from .models import Recipe, AmountIngredient, Favorite, Cart, Tag


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientAmountSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    id = serializers.ReadOnlyField(source='ingredient.id')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ListRecipeSerializer(serializers.ModelSerializer):
    author = UserModelSerializer()
    tags = TagSerializer(
        many=True,
        required=False,
        read_only=True,
    )
    image = Base64ImageField(required=False)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, obj):
        serializer = IngredientAmountSerializer(
            AmountIngredient.objects.filter(recipe=obj), many=True
        )
        return serializer.data

    def get_is_favorited(self, obj):
        return self._get_model_exists(obj, Favorite)

    def get_is_in_shopping_cart(self, obj):
        return self._get_model_exists(obj, Cart)

    def _get_model_exists(self, obj, model):
        request = self.context.get('request')
        if request is None:
            return False
        user = request.user
        if user.is_anonymous:
            return False
        return model.objects.filter(user=user, recipe=obj).exists()


class RecipeAndUserSerializerMixin(serializers.Serializer):
    user = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault(),
    )
    recipe = serializers.SlugRelatedField(
        queryset=Recipe.objects.all(),
        slug_field='name',
    )


class FavoriteSerializer(
    RecipeAndUserSerializerMixin,
    serializers.ModelSerializer,
):
    class Meta:
        model = Favorite
        fields = '__all__'
        read_only_fields = ('user', 'recipe')
        validators = (
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт добавлен в избранное!',
            ),
        )


class CartSerializer(
    RecipeAndUserSerializerMixin,
    serializers.ModelSerializer,
):
    class Meta:
        model = Cart
        fields = '__all__'
        read_only_fields = ('user', 'recipe')
        validators = (
            validators.UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт добавлен в список покупок!',
            ),
        )


class AmountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount')
        extra_kwargs = {
            'amount': {'write_only': True},
        }


class RecipeCreatedSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = AmountSerializer(many=True)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )
        extra_kwargs = {
            'cooking_time': {'write_only': True},
            'name': {'write_only': True},
            'text': {'write_only': True},
        }

    def validate_tags(self, tag):
        if not tag:
            return serializers.ValidationError({'error': 'Тег отсутсвует!'})
        return tag

    def validate_ingredients(self, ingredient):
        if not ingredient:
            return serializers.ValidationError(
                {'error': 'Ингредиент отсутсвует!'}
            )
        return ingredient

    def create(self, data):
        ingredients = data.pop('ingredients')
        tags = data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user, **data
        )
        AmountIngredient.objects.bulk_create(
            [
                AmountIngredient(
                    ingredient=Ingredient.objects.get(id=value.get('id')),
                    recipe=recipe,
                    amount=value.get('amount'),
                )
                for value in ingredients
            ]
        )
        recipe.tags.set(tags)
        return recipe
