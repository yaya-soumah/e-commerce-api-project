from django.urls import path
from .views import LoginViewSet

urlpatterns = [
    path('', LoginViewSet.as_view({'post':'login'}), name='login'),
]