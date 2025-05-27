from django.db import models
from apps.categories.models import Category

class CategoryAttribute(models.Model):
    attr_name = models.CharField(max_length=255)
    cat_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='attributes')
    attr_sel = models.CharField(max_length=10, choices=[('only', 'Only'), ('many', 'Many')])
    attr_write = models.CharField(max_length=10, choices=[('manual', 'Manual'), ('list', 'List')])
    attr_vals = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'apps_attributes_categoryattribute'
        unique_together = ('cat_id', 'attr_name')
        verbose_name = 'Category Attribute'
        verbose_name_plural = 'Category Attributes'
        

    def __str__(self):
        return f"{self.attr_name} ({self.cat_id.name})"