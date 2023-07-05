from rest_framework import pagination


class PageNumberAndLimit(pagination.PageNumberPagination):
    """
    Пагинатор с заданным числом страниц и лимитом на вывод.
    """

    page_size = 10
    page_size_query_param = 'limit'
