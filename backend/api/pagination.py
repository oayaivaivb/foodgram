from rest_framework.pagination import PageNumberPagination

DEFAULT_PAGE_SIZE = 6


class FoodgramPagination(PageNumberPagination):
    """Кастомная пагинация для Foodgram с параметрами по умолчанию."""

    page_query_param = 'page'
    page_size_query_param = 'limit'
    page_size = DEFAULT_PAGE_SIZE
