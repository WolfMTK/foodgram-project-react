from djoser.serializers import UserSerializer
from rest_framework import serializers, validators
from django.contrib.auth.validators import UnicodeUsernameValidator

from core.validations import validate_password
from recipes.models import Recipe
from .models import User, Subscription


class SubscriptionMixin:
    """Миксин подписки."""

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None:
            return False
        user = request.user
        if user.is_anonymous or user == obj:
            return False
        return Subscription.objects.filter(user=user, subscribed=obj).exists()


class UserCreateMixin:
    """Миксин создание пользователя."""

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'error': 'Пользователь с такой почтой уже существует!'}
            )
        return email

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {'error': 'Пользователь с таким username уже существует!'}
            )
        elif len(username) < 4:
            raise serializers.ValidationError(
                {'error': 'username не может быть меньше 4!'}
            )
        return username

    # Или лучше было не выносить отдельно в
    # функцию validate_password проверку пароля?
    def validate_password(self, password):
        validate_password(password)
        return password


class UserModelSerializer(SubscriptionMixin, UserCreateMixin, UserSerializer):
    """Пользовательский сериализатор."""

    username = serializers.CharField(
        max_length=150,
        validators=(UnicodeUsernameValidator,),
    )
    email = serializers.EmailField(max_length=254)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password',
        )
        read_only_fields = ('is_subscribed',)
        extra_kwargs = {'password': {'write_only': True}}


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки пользователя."""

    user = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
        default=serializers.CurrentUserDefault(),
    )
    subscribed = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field='username',
    )

    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ('user', 'subscribed')
        validators = (
            validators.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subscribed'),
            ),
        )

    def validate(self, attrs):
        if attrs.get('user') == attrs.get('subscribed'):
            raise serializers.ValidationError(
                {'error': 'Подписка на самого себя невозможна!'}
            )
        return attrs


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов."""

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionSerializer(
    SubscriptionMixin,
    serializers.ModelSerializer,
):
    """Сериализатор подписки."""

    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    recipes = RecipeSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = ('is_subscribed', 'recipes_count', 'recipes')

    def get_recipes_count(self, obj):
        return User.objects.filter(recipes__author=obj).count()
