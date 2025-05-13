from django.urls import path
from django.views.decorators.cache import cache_page
from .views import ReportViewSet

urlpatterns = [
    path('sales/', cache_page(60 * 60)(ReportViewSet.as_view({'get': 'sales'})), name='sales-report'),
    path('products/', cache_page(60 * 60)(ReportViewSet.as_view({'get': 'products'})), name='products-report'),
    path('payment_status/', cache_page(60 * 60)(ReportViewSet.as_view({'get': 'payment_status'})), name='payment-status-report'),
    path('categories/', cache_page(60 * 60)(ReportViewSet.as_view({'get': 'categories'})), name='categories-report'),
]
