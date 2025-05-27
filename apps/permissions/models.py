from django.db import models

class Permission(models.Model):
    name = models.CharField(max_length=100, unique=True)
    level = models.PositiveIntegerField(default=1) # Depth (1 to 4)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'apps_permissions_permission'

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