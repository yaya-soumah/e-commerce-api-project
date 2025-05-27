from django.urls import path, include
from apps.products.views import UploadView
from rest_framework_simplejwt.views import (
       TokenObtainPairView,
       TokenRefreshView,
   )

from .swagger import schema_view

urlpatterns = [
    path('api/private/v1/auth/login/',include('apps.auth.urls')),
    path('api/private/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/private/v1/permissions/',include('apps.permissions.urls')),
    path('api/private/v1/roles/',include('apps.roles.urls')),
    path('api/private/v1/categories/',include('apps.categories.urls')),
    path('api/private/v1/categories/<int:cat_id>/attributes/', include('apps.attributes.urls')),
    path('api/private/v1/goods/', include('apps.products.urls')),
    path('api/private/v1/upload/', UploadView.as_view(), name='upload'),
    path('api/private/v1/users/',include('apps.users.urls')),
    path('api/private/v1/orders/',include('apps.orders.urls')),
    path('api/private/v1/reports/',include('apps.analytics.urls')),
    # documentation urls
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
