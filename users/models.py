from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    email = models.EmailField(unique=True, max_length=254)

    class Meta:
        db_table = 'auth_user'

class Permission(models.Model):
    name = models.CharField(max_length=100, unique=True)
    level = models.PositiveIntegerField(default=1) # Depth (1 to 4)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Enforce max depth of 4
        if self.parent:
            depth = 1
            current = self.parent

            while current.parent and depth < 4:
                depth += 1
                current = current.parent
            if depth >= 4:
                raise ValueError("Permission hierarchy cannot exceed depth of 4")
        super().save(*args, **kwargs)

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    permissions = models.ManyToManyField(Permission, related_name='roles', blank=True)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.ForeignKey(Role,null=True, blank=True, on_delete=models.SET_NULL)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users_userprofile'

    def __str__(self):
        return f"{self.user.username}'s Profile"
