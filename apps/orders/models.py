from django.db import models
# from django.conf import settings
from apps.products.models import Product
from apps.categories.models import Category
from apps.users.models import User

class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    )
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('FAILED', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    shipping_address = models.TextField()
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'apps_orders_order'
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f'ORD-{Category.objects.count():06d}{self.user.id}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Order {self.order_number} - {self.user.username}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='order_items')
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'apps_orders_orderitem'
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f'{self.quantity} x {self.product.goods_name} in {self.order.order_number}'

class ShippingTracking(models.Model):
    CARRIER_CHOICES = (
        ('FEDEX', 'FedEx'),
        ('UPS', 'UPS'),
        ('DHL', 'DHL'),
        ('USPS', 'USPS'),
    )
    STATUS_CHOICES = (
        ('PREPARING', 'Preparing'),
        ('IN_TRANSIT', 'In Transit'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='tracking')
    carrier = models.CharField(max_length=20, choices=CARRIER_CHOICES)
    tracking_number = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PREPARING')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'apps_orders_shippingtracking'
        verbose_name = 'Shipping Tracking'
        verbose_name_plural = 'Shipping Trackings'

    def __str__(self):
        return f'Tracking {self.tracking_number} for {self.order.order_number}'