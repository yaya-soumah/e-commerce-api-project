from rest_framework import serializers
from django.db.models import Sum, Count, F, Q, ExpressionWrapper, DecimalField
from apps.orders.models import Order, OrderItem
from django.db.models.functions import TruncDate
from apps.categories.models import Category

class SalesReportSerializer(serializers.Serializer):
    date = serializers.DateField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    orders = serializers.IntegerField()

    def get_queryset(self, start_date, end_date):
        return Order.objects.filter(
                    created_at__date__gte=start_date,
                    created_at__date__lte=end_date
                ).annotate(
                    date=TruncDate('created_at')
                ).values('date').annotate(
                    revenue=Sum('total_amount'),
                    orders=Count('id')
                ).order_by('date')

    def to_representation(self, instance):
        return {
            'date': instance['date'],
            'revenue': instance['revenue'] or 0.0,
            'orders': instance['orders'] or 0
        }

class ProductPopularitySerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    units_sold = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)

    def get_queryset(self, start_date, end_date):
        return OrderItem.objects.filter(
            order__created_at__date__gte=start_date,
            order__created_at__date__lte=end_date
        ).annotate(
            product_name=F('product__goods_name')
        ).values(
            'product_id',
            'product_name'
        ).annotate(
            units_sold=Sum('quantity', default=0),
            revenue=Sum(ExpressionWrapper(
                F('quantity') * F('unit_price'),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            ), default=0)
        ).order_by('-units_sold')

    def to_representation(self, instance):
        return {
            'product_id': instance['product_id'],
            'product_name': instance['product_name'],
            'units_sold': instance['units_sold'] or 0,
            'revenue': instance['revenue'] or 0.0
        }

class PaymentStatusSerializer(serializers.Serializer):
    status = serializers.CharField()
    order_count = serializers.IntegerField()
    percentage = serializers.FloatField()

    def get_queryset(self, start_date, end_date):
        total_orders = Order.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).count()
        queryset = Order.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).values('payment_status').annotate(
            order_count=Count('id')
        )
        for item in queryset:
            item['percentage'] = (item['order_count'] / total_orders * 100) if total_orders else 0
        return queryset

    def to_representation(self, instance):
        return {
            'status': instance['payment_status'],
            'order_count': instance['order_count'],
            'percentage': round(instance['percentage'], 2)
        }

class ProductCategoryReportSerializer(serializers.Serializer):
    category_id = serializers.IntegerField()
    category_name = serializers.CharField()
    total_sales = serializers.DecimalField(max_digits=10, decimal_places=2)
    order_count = serializers.IntegerField()

    def get_queryset(self, start_date, end_date):       
        return Category.objects.filter(
            is_deleted=False,
            products__order_items__order__created_at__date__gte=start_date,
            products__order_items__order__created_at__date__lte=end_date

            ).annotate(
                
            category_id=F('id'),
            category_name=F('name'),
            total_sales=Sum(F('products__order_items__unit_price') * F('products__order_items__quantity')),
            order_count=Count('products__order_items__order', distinct=True),
            product_count=Count('products',distinct=True, filter=Q(products__is_deleted=False)),
            total_quantity=Sum('products__order_items__quantity')            
            ).values(
            'category_id',
            'category_name',
            'total_sales',
            'order_count',
            'product_count',
            'total_quantity'
        ).order_by('-total_sales')

