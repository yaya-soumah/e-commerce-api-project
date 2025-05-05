from django.db import models
from apps.permissions.models import Permission

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    permissions = models.ManyToManyField(Permission, related_name='roles', blank=True)

    class Meta:
        db_table = 'apps_roles_role'

    def __str__(self):
        return self.name