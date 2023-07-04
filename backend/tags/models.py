from django.db import models


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Название',
        unique=True,
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        verbose_name='Цвет в HEX',
    )
    slug = models.SlugField(
        max_length=200,
        blank=False,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name
