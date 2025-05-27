from rest_framework import serializers
from .models import Order, OrderItem, ShippingTracking
from apps.products.models import Product
from apps.products.serializers import ProductSerializer
from django.db import transaction
from apps.users.models import User

class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product'
    )
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_id', 'product', 'quantity', 'unit_price']
        read_only_fields = ['id', 'unit_price']

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity')
        if product.goods_quantity < quantity:
            raise serializers.ValidationError({
                'quantity': f'Only {product.goods_quantity} units of {product.goods_name} available.'
            })
        return data

class ShippingTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingTracking
        fields = ['carrier', 'tracking_number', 'status', 'updated_at']
        read_only_fields = ['updated_at']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    tracking = ShippingTrackingSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user_id', 'total_amount', 'status',
            'payment_status', 'shipping_address', 'notes', 'created_at',
            'updated_at', 'items', 'tracking'
        ]
        read_only_fields = ['id', 'order_number', 'total_amount', 'created_at', 'updated_at']

    def validate(self, data):
        items = data.get('items', [])
        if not items:
            raise serializers.ValidationError({'items': 'At least one item is required.'})
        total_amount = sum(item['quantity'] * item['product'].goods_price for item in items)
        data['total_amount'] = total_amount
        return data

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=product.goods_price
            )
            product.goods_quantity -= quantity
            product.save()

        return order

class ChangeShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['shipping_address']

    def validate_shipping_address(self, value):
        if not value.strip():
            raise serializers.ValidationError('Shipping address cannot be empty.')
        return value

    def validate(self, data):
        order = self.instance
        if order.status in ['SHIPPED', 'DELIVERED']:
            raise serializers.ValidationError('Cannot change address for shipped or delivered orders.')
        return data

class UpdateTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingTracking
        fields = ['carrier', 'tracking_number', 'status']

    def validate(self, data):
        order = self.instance.order
        if order.status.upper() not in ['PENDING','PROCESSING', 'SHIPPED']:
            raise serializers.ValidationError('Tracking can only be updated for processing or shipped orders.')
        return data