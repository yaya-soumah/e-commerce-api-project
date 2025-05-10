from django.urls import path, include
from apps.products.views import UploadView

urlpatterns = [
    path('api/private/v1/auth/login/',include('apps.auth.urls')),
    path('api/private/v1/permissions/',include('apps.permissions.urls')),
    path('api/private/v1/roles/',include('apps.roles.urls')),
    path('api/private/v1/categories/',include('apps.categories.urls')),
    path('api/private/v1/categories/<int:cat_id>/attributes/', include('apps.attributes.urls')),
    path('api/private/v1/goods/', include('apps.products.urls')),
    path('api/private/v1/upload/', UploadView.as_view(), name='upload'),
    path('api/private/v1/users/',include('apps.users.urls')),
    path('api/private/v1/orders/',include('apps.orders.urls')),
]
