from rest_framework import pagination, generics

class ResourcePagination(pagination.PageNumberPagination):
    page_size = 9
