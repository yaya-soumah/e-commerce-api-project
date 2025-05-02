from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoginViewSet, CategoryViewSet

app_name = 'core'

router = DefaultRouter()

router.register(r'categories', CategoryViewSet, basename='categories')

urlpatterns = [
    path('auth/login/', LoginViewSet.as_view({'post':'login'}), name='login'),
    path('', include(router.urls)),
]