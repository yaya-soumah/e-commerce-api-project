from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register(r'', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('<int:pk>/pics/', ProductViewSet.as_view({'put':'update_pics'}), name='product-pics'),
    path('<int:pk>/attributes/', ProductViewSet.as_view({'put':'update_attributes'}), name='product-attributes'),
    path('<int:pk>/state/', ProductViewSet.as_view({'patch':'update_state'}), name='product-state'),
    path('bulk/', ProductViewSet.as_view({'post':'bulk', 'put':'bulk'}), name='product-bulk'),
]
