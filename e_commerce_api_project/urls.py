from django.urls import path, include

urlpatterns = [
    path('api/private/v1/auth/login/',include('apps.auth.urls')),
    path('api/private/v1/permissions/',include('apps.permissions.urls')),
    path('api/private/v1/roles/',include('apps.roles.urls')),
    path('api/private/v1/categories/',include('apps.categories.urls')),
    path('api/private/v1/categories/<int:cat_id>/attributes/', include('apps.attributes.urls')),
    path('api/private/v1/users/',include('apps.users.urls')),
]
