from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size_query_param = 'pagesize'
    page_query_param = 'pagenum'
