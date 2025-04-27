from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'core'

urlpatterns = [
    path('auth/login/', obtain_auth_token, name='login'),
]