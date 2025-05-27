import factory
from django.utils import timezone
from apps.categories.models import Category
from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from apps.users.models import User, UserProfile
from datetime import datetime
from factory import LazyFunction

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True  # Fix DeprecationWarning

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.PostGenerationMethodCall('set_password', 'test123')
    is_staff = False

    @factory.post_generation
    def create_user_profile(self, create, extracted, **kwargs):
        if create and not UserProfile.objects.filter(user=self).exists():
            UserProfile.objects.create(user=self, **kwargs)

class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    goods_name = factory.Sequence(lambda n: f"Product {n}")
    goods_price = 10.00
    goods_quantity = 3
    goods_weight = 1.0

class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    user = factory.SubFactory(UserFactory)
    order_number = factory.Sequence(lambda n: f"ORD-{n:06d}")
    total_amount = 20.00
    status = 'PENDING'
    payment_status = 'PENDING'
    shipping_address = "123 Main St"
    
class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = None
    product = None
    quantity = 1
    unit_price = 10.00

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Faker('word')