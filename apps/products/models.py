from django.db import models
from apps.categories.models import Category
from apps.attributes.models import CategoryAttribute

STATE = [(0, 'Non-Confirmed'), (1, 'Pending'),(2, 'Confirmed')]

class Product(models.Model):
    goods_name = models.CharField(max_length=255)
    goods_description = models.TextField(blank=True, null=True)
    goods_price = models.DecimalField(decimal_places=2,max_digits=10)
    goods_quantity = models.PositiveIntegerField()
    goods_weight = models.DecimalField(max_digits=10, decimal_places=2)
    goods_state =models.IntegerField(choices=STATE, default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hot_quantity = models.PositiveIntegerField(default=0)
    is_promote = models.BooleanField(default=False)
    goods_big_logo = models.CharField(max_length=255, blank=True, null=True)
    goods_small_logo = models.CharField(max_length=255, blank=True, null=True)
    categories = models.ManyToManyField(Category, related_name='products')
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'apps_products_product'
    
    def __str__(self):
        return self.goods_name
    

class ProductPicture(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='pics')
    pics_big = models.CharField(max_length=255)
    pics_mid = models.CharField(max_length=255)
    pics_sma = models.CharField(max_length=255)

    class Meta:
        db_table = 'apps_products_productpicture'
    
    def __str__(self):
        return f"Picture for {self.product.goods_name}"
    
class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='attrs')
    attribute = models.ForeignKey(CategoryAttribute, on_delete=models.CASCADE, related_name='attrs')
    attr_value = models.CharField(max_length=255)
    attr_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        db_table = 'apps_products_productattribute'
        unique_together = ['product', 'attribute','attr_value']
    
    def __str__(self):
        return f"{self.attribute.attr_name}: {self.attr_value}"
