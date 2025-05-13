from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from apps.users.models import User
from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from apps.categories.models import Category
from rest_framework_simplejwt.tokens import RefreshToken

class CategoryReportTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.defaults['HTTP_ACCEPT'] = 'application/json'
        self.client.defaults['CONTENT_TYPE'] = 'application/json'

        self.admin = User.objects.create(username='admin',is_staff=True,password='admin123')
        self.category = Category.objects.create(name='Electronics')
        self.product = Product.objects.create(goods_name='Smartphone', 
                                              goods_price=599.99, 
                                              goods_weight=0.5,
                                              goods_quantity=100)
        self.product.categories.set([self.category])
        self.order = Order.objects.create(user_id=self.admin.id, total_amount=599.99)
        order_item = OrderItem.objects.create(product_id=self.product.id,
                                              quantity=1,
                                              order_id=self.order.id,
                                              unit_price=599.99)
        self.order.items.set([order_item])
               
    
    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    def test_category_report(self):   
        tokens = self.get_tokens_for_user(self.admin)
        access_token = tokens['access']     
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        url = reverse('categories-report') + '?start_date=2025-05-10&end_date=2025-05-31'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['data'][0]['category_name'], 'Electronics')
        self.assertEqual(response.json()['data'][0]['total_sales'], 599.99)

    def test_invalid_date_format(self):
        tokens = self.get_tokens_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        url = reverse('categories-report') + '?start_date=invalid&end_date=2025-05-31'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_no_data(self):
        tokens = self.get_tokens_for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        url = reverse('categories-report') + '?start_date=2024-05-10&end_date=2024-05-31'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()['data']), 0)
    
    