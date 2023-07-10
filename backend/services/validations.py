from rest_framework import serializers
from django.core import exceptions
from django.conf import settings
from django.contrib.auth import password_validation as validation


def validate_password(password, key='password'):
    if len(password) < settings.LEN_PASSWORD:
        raise serializers.ValidationError(
            {'error': 'Пароль меньше 6 символов!'}
        )
    data = {}
    try:
        validation.validate_password(password)
    except exceptions.ValidationError as error:
        data[key] = list(error.message)
    if data:
        raise serializers.ValidationError(data)
