from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet

router = DefaultRouter()
router.register(r'', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),    
    path('<int:pk>/reactivate/', CategoryViewSet.as_view({'patch':'reactivate'}), name='category-reactivate'),
    path('deleted/', CategoryViewSet.as_view({'get':'deleted'}, name='category-deleted')),
    path('<int:pk>/permanent/', CategoryViewSet.as_view({'delete':'permanent'}), name='category-permanent'),
    path('permanent/bulk/', CategoryViewSet.as_view({'post':'permanent_bulk'}), name='category-permanent-bulk')
]
