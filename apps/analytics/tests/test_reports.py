import pytest
from django.core.management import call_command
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import datetime, timedelta
from apps.orders.models import Order, OrderItem 
from apps.products.models import Product
from apps.categories.models import Category
import logging

logger = logging.getLogger(__name__)

class TestSalesReport:
    @pytest.mark.django_db
    def test_sales_report(self,admin_client, user_factory, order_factory):
        admin = user_factory(is_staff=True)
        order = order_factory(user=admin)
        order.created_at = timezone.make_aware(datetime(2025, 5, 10))
        order.total_amount = 100.00
        order.save()

        response = admin_client.get(
            "/api/private/v1/reports/sales/?start_date=2025-05-01&end_date=2025-05-20",
            HTTP_ACCEPT='application/json'
        )

        assert response.status_code == 200
        assert response.data['status'] == 'success'
        assert 'data' in response.data
        assert len(response.data['data']) > 0, f"Expected non-empty data, got: {response.data['data']}"

    @pytest.mark.django_db
    def test_sales_report_empty(self,admin_client):
        response = admin_client.get(
            "/api/private/v1/reports/sales/?start_date=2024-01-01&end_date=2024-01-31",
            HTTP_ACCEPT='application/json',
            HTTP_HOST='localhost'
        )
        assert response.status_code == 200
        assert response.data['status'] == 'success'
        assert len(response.data['data']) == 0, f"Expected empty data, got: {response.data['data']}"
        assert response.data['message'] == "Sales report generated successfully"
    
    @pytest.mark.django_db
    def test_sales_report_invalid_date_format(self,admin_client):
        
        response = admin_client.get(
            "/api/private/v1/reports/sales/?start_date=invalid&end_date=2025-05-20",
            HTTP_ACCEPT='application/json',
            HTTP_HOST='localhost'
        )

        assert response.status_code == 400
        assert response.data['status'] == 'error'
        assert 'Invalid start_date format' in response.data['message']
    
    @pytest.mark.django_db
    def test_invalid_start_date_format(self,admin_client):
        response = admin_client.get("/api/private/v1/reports/sales/?start_date=2024-99-99")
        
        assert response.status_code == 400
        assert response.data["message"] == "Invalid start_date format"
    
    @pytest.mark.django_db
    def test_start_date_after_end_date(self,admin_client):
        response = admin_client.get("/api/private/v1/reports/sales/?start_date=2025-06-01&end_date=2025-05-01")
        
        assert response.status_code == 400
    
    @pytest.mark.django_db
    def test_sales_report_schema(self,admin_client, user_factory, order_factory):
        admin = user_factory(is_staff=True)
        order = order_factory(user=admin, total_amount=100.00, created_at=timezone.make_aware(datetime(2025, 5, 10)))
        
        response = admin_client.get("/api/private/v1/reports/sales/?start_date=2025-05-01&end_date=2025-05-20")
        
        assert response.status_code == 200
        assert isinstance(response.data['data'], list)
        if response.data['data']:
            row = response.data['data'][0]
            assert 'date' in row
            assert 'revenue' in row

    @pytest.mark.django_db
    def test_single_day_report(self, admin_client, order_factory):
        today = timezone.now().date()
        order_factory(total_amount=150.00, created_at=today)
        
        response = admin_client.get(
            f"/api/private/v1/reports/sales/?start_date={today}&end_date={today}"
        )
        
        assert response.status_code == 200
        assert len(response.data['data']) == 1
        assert str(response.data['data'][0]['date']) == str(today)
        assert float(response.data['data'][0]['revenue']) == 150.00

class TestProductReport:

    @pytest.mark.django_db
    def test_products_report(self,admin_client,user_factory, product_factory, order_factory, order_item_factory):
        admin = user_factory(is_staff=True)
        product = product_factory(goods_name="Test Product", goods_price=10.00, goods_weight=1.0)
        order = order_factory(user=admin)
        order.created_at = timezone.make_aware(datetime(2025, 5, 10))
        order.save()
        order_item = order_item_factory(order=order, product=product, quantity=2, unit_price=10.00)

        response = admin_client.get(
            "/api/private/v1/reports/products/?start_date=2025-05-01&end_date=2025-05-26",
            HTTP_ACCEPT='application/json'
        )
        
        assert response.status_code == 200
        assert response.data['status'] == 'success'
        assert 'data' in response.data
        assert len(response.data['data']) > 0, f"Expected non-empty data, got: {response.data['data']}"
        assert response.data['data'][0]['product_name'] == "Test Product"
    
    @pytest.mark.django_db
    def test_product_report_empty(self,admin_client, user_factory, product_factory, order_factory, order_item_factory):
        response = admin_client.get(
            "/api/private/v1/reports/products/?start_date=2024-01-10&end_date=2024-01-31",
            HTTP_ACCEPT='application/json',
            HTTP_HOST='localhost'
        )

        assert response.status_code == 200
        assert response.data['status'] == 'success'
        assert len(response.data['data']) == 0 , f"Expected empty data, got: {response.data['data']}"
        assert response.data['message'] == "Product popularity report generated successfully"

    @pytest.mark.django_db
    def test_product_popularity(self,admin_client, order_factory, order_item_factory, product_factory):
        product = product_factory(goods_name="Phone", goods_price=500)
        order = order_factory()
        order_item_factory(order=order, product=product, quantity=3, unit_price=500)

        start = (timezone.now() - timedelta(days=10)).date()
        end = timezone.now().date()

        response = admin_client.get(f"/api/private/v1/reports/products/?start_date={start}&end_date={end}")
        
        assert response.status_code == 200
        assert any(item["product_name"] == "Phone" for item in response.data["data"])

    @pytest.mark.django_db
    def test_products_error_response(self, admin_client):
        response = admin_client.get(
            "/api/private/v1/reports/products/?start_date=2025-05-20&end_date=2025-05-01",
            HTTP_ACCEPT='application/json'
        )

        logger.info(f"PRODUCTS_ERROR_RESPONSE: {response.data}")
        assert response.status_code == 400
        assert response.data['status'] == 'error'
        assert 'start_date cannot be after end_date' in response.data['message']

   
class TestCategoryReport:
    
    @pytest.mark.django_db
    def test_product_category_report(self,admin_client, user_factory, category_factory, product_factory, order_factory, order_item_factory):
        
        category = category_factory(name="Electronics", is_deleted=False)
        product = product_factory(goods_name="Laptop", goods_price=1000, goods_quantity=100)
        product.categories.set([category])
        product.save()

        order_date = timezone.make_aware(datetime(2025, 5, 10))
        order = order_factory(created_at=order_date)
        order_item_factory(order=order, product=product, quantity=2, unit_price=1000)

        response = admin_client.get(
            f"/api/private/v1/reports/categories/?start_date=2025-05-01&end_date=2025-05-30"
        )

        assert response.status_code == 200
        assert len(response.data["data"]) > 0
        assert response.data["data"][0]["category_name"] == "Electronics"

    @pytest.mark.django_db
    def test_categories_report_invalid_dates(self,admin_client):
        response = admin_client.get(
            "/api/private/v1/reports/categories/?start_date=invalid&end_date=2025-05-01",
            HTTP_ACCEPT='application/json',
            HTTP_HOST='localhost'
        )

        assert response.status_code == 400
        assert response.data['status'] == 'error'
        assert 'Invalid start_date format' in response.data['message']
    
    @pytest.mark.django_db
    def test_category_invalid_date_format(self,admin_client, user_factory):
                
        response = admin_client.get(
            "/api/private/v1/reports/categories/?start_date=invalid&end_date=2025-05-20",
            HTTP_ACCEPT='application/json',
            HTTP_HOST='localhost'
        )
        
        assert response.status_code == 400
        assert response.data['status'] == 'error'
        assert 'Invalid start_date format' in response.data['message']

    @pytest.mark.django_db
    def test_no_data(self, admin_client):        
        response = admin_client.get(
            "/api/private/v1/reports/categories/?start_date=2024-01-01&end_date=2024-01-31",
            HTTP_ACCEPT='application/json',
            HTTP_HOST='localhost'
        )
        
        assert response.status_code == 200
        assert response.data['status'] == 'success'
        assert len(response.data['data']) == 0

    @pytest.mark.django_db    
    def test_categories_report_null_values(self,admin_client, user_factory, category_factory, product_factory, order_factory, order_item_factory):
        category = category_factory(name="Electronics", is_deleted=False)
        product = product_factory(goods_name="Laptop", goods_price=0.0, goods_quantity=100)
        product.categories.add(category)

        order = order_factory(created_at=timezone.now())
        order_item_factory(order=order, product=product, quantity=1, unit_price=0.0)

        start = (timezone.now() - timedelta(days=1)).date()
        end = (timezone.now() + timedelta(days=1)).date()

        response = admin_client.get(
            f"/api/private/v1/reports/categories/?start_date={start}&end_date={end}"
        )

        assert response.status_code == 200
        assert len(response.data["data"]) > 0
        assert response.data["data"][0]["category_name"] == "Electronics"

    @pytest.mark.django_db
    def test_category_no_products(self, admin_client, category_factory):
        category = category_factory(name="Empty Category", is_deleted=False)
        
        response = admin_client.get(
            "/api/private/v1/reports/categories/?start_date=2025-05-01&end_date=2025-05-20",
            HTTP_ACCEPT='application/json'
        )

        logger.info(f"CATEGORY_NO_PRODUCTS_RESPONSE: {response.data}")
        assert response.status_code == 200
        assert response.data['status'] == 'success'
        assert len(response.data['data']) == 0

    @pytest.mark.django_db
    def test_category_deleted(self, admin_client, category_factory, product_factory, order_factory, order_item_factory):
        
        category = category_factory(name="Deleted Category", is_deleted=True)
        product = product_factory(goods_name="Laptop", goods_price=1000)
        product.categories.add(category)
        product.save()
        order = order_factory(created_at=timezone.make_aware(datetime(2025, 5, 10)))
        order_item = order_item_factory(order=order, product=product, quantity=1, unit_price=1000)
        
        response = admin_client.get(
            "/api/private/v1/reports/categories/?start_date=2025-05-01&end_date=2025-05-20",
            HTTP_ACCEPT='application/json'
        )

        logger.info(f"CATEGORY_DELETED_RESPONSE: {response.data}")
        assert response.status_code == 200
        assert response.data['status'] == 'success'
        assert len(response.data['data']) == 0

class TestPaymentStatusReport:
    
    @pytest.mark.django_db
    def test_payment_status_report(self,admin_client,user_factory, order_factory):
        admin = user_factory(is_staff=True)

        date = timezone.make_aware(datetime(2025, 5, 10))

        order1 = order_factory(user=admin, payment_status='PAID')
        order1.created_at = date
        order1.save()

        order2 = order_factory(user=admin, payment_status='PENDING')
        order2.created_at = date
        order2.save()

        response = admin_client.get(
            "/api/private/v1/reports/payment_status/?start_date=2025-05-01&end_date=2025-05-20",
            HTTP_ACCEPT='application/json'
        )

        assert response.status_code == 200
        assert response.data['status'] == 'success'
        assert 'data' in response.data
        assert len(response.data['data']) == 2, f"Expected 2 items, got: {response.data['data']}"
        statuses = {item['status']: item for item in response.data['data']}
        assert statuses['PAID']['order_count'] == 1
        assert statuses['PAID']['percentage'] == 50.0

    @pytest.mark.django_db
    def test_payment_status_report_empty(self,admin_client):
        
        response = admin_client.get(
            "/api/private/v1/reports/payment_status/?start_date=2024-01-01&end_date=2024-01-31",
            HTTP_ACCEPT='application/json',
            HTTP_HOST='localhost'
        )

        assert response.status_code == 200
        assert response.data['status'] == 'success'
        assert len(response.data['data']) == 0
        assert response.data['message'] == 'Payment status report generated successfully'

    @pytest.mark.django_db
    def test_payment_status_zero_orders(self, admin_client, user_factory):
        
        response = admin_client.get(
            "/api/private/v1/reports/payment_status/?start_date=2025-05-19&end_date=2025-05-20",
            HTTP_ACCEPT='application/json'
        )
        
        assert response.status_code == 200
        assert response.data['status'] == 'success'
        assert len(response.data['data']) == 0
        assert response.data['message'] == "Payment status report generated successfully"

