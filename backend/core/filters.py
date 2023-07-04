from rest_framework import filters


class BackendSearchFilter(filters.SearchFilter):
    search_param = 'name'
