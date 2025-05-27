from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryAttributeViewSet

router = DefaultRouter()
router.register(r'', CategoryAttributeViewSet, basename='attribute')

urlpatterns = [
    path('', include(router.urls))
]
