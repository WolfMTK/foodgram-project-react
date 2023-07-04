from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Админка для модели User."""

    ordering = ('first_name',)
    list_display = ('id', 'username', 'email', 'first_name', 'last_name')
    list_filter = ('first_name', 'email')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    empty_value_display = "unknown"
