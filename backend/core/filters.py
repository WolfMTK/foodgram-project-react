from rest_framework import filters


class BackendSearchFilter(filters.SearchFilter):
    """Фильтр поиска."""

    search_param = 'name'
