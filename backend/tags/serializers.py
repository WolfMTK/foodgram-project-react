import webcolors
from rest_framework import serializers

from .models import Tag


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


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
