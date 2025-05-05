from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryAttributeViewSet

router = DefaultRouter()
router.register(r'attributes', CategoryAttributeViewSet, basename='category-attribute')

urlpatterns = [
    path('', include(router.urls))
]
