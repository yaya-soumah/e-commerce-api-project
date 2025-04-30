from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, PermissionViewSet, RoleViewSet

app_name = "users"

router = DefaultRouter()

router.register(r'users', UserViewSet, basename='user')
router.register(r'permissions', PermissionViewSet, basename='permission' )
router.register(r'roles', RoleViewSet, basename='role')

urlpatterns = [
    path('', include(router.urls)),
]