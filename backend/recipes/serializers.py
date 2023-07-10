import base64

import webcolors
from rest_framework import serializers, validators
from django.core.files.base import ContentFile

from users.serializers import UserModelSerializer
from users.models import User
from .models import Recipe, AmountIngredient, Favorite, Cart, Tag, Ingredient


class Hex2NameColor(serializers.Field):
    """Поле цвета."""

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени!')
        return data


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class Base64ImageField(serializers.ImageField):
    """Поле base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор количества ингредиентов."""

    name = serializers.ReadOnlyField(source='ingredient.name')
    id = serializers.ReadOnlyField(source='ingredient.id')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ListRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор списка рецептов."""

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
    """Миксин рецептов и пользователей."""

    user = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault(),
    )
    recipe = serializers.SlugRelatedField(
        queryset=Recipe.objects.all(),
        slug_field='id',
    )


class FavoriteAddingSerializer(
    RecipeAndUserSerializerMixin,
    serializers.ModelSerializer,
):
    """Сериализатор избранных рецептов."""

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


class CartAddingSerializer(
    RecipeAndUserSerializerMixin,
    serializers.ModelSerializer,
):
    """Сериализатор списка покупок."""

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
    """Сериализатор количества ингредиентов."""

    id = serializers.IntegerField()

    class Meta:
        model = AmountIngredient
        fields = ('id', 'amount')


class RecipeCreatingSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""

    image = Base64ImageField(required=False, allow_null=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    ingredients = AmountSerializer(many=True, write_only=True)

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
            'image': {'write_only': True},
            'tags': {'write_only': True},
        }

    def validate_tags(self, tags):
        if not tags:
            return serializers.ValidationError({'error': 'Тег отсутсвует!'})
        if len(tags) != len(set(tags)):
            return serializers.ValidationError(
                {'error': 'Тег не должен повторяться!'}
            )
        return tags

    def validate_ingredients(self, ingredients):
        if not ingredients:
            return serializers.ValidationError(
                {'error': 'Ингредиент отсутсвует!'}
            )
        for ingredient in ingredients:
            if ingredient.get('amount') < 0:
                return serializers.ValidationError(
                    {
                        'error': (
                            'Количество ингредиентов не '
                            'должно быть меньше 1!'
                        )
                    }
                )
        return ingredients

    def create(self, data):
        ingredients = data.pop('ingredients')
        tags = data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user, **data
        )
        return self._set_recipe_data(ingredients, recipe, tags)

    def update(self, recipe, data):
        AmountIngredient.objects.filter(recipe=recipe).delete()
        ingredients = data.pop('ingredients')
        tags = data.pop('tags')
        return self._set_recipe_data(ingredients, recipe, tags)

    def to_representation(self, instance):
        return ListRecipeSerializer(instance).data

    def _set_recipe_data(self, ingredients, recipe, tags):
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
