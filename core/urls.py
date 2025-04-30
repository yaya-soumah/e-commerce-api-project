from django.urls import path, include
from .views import LoginView
app_name = 'core'

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
]