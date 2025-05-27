import pytest
from rest_framework.test import APIClient
from pytest_factoryboy import register
from apps.analytics.tests.factories import UserFactory, CategoryFactory, ProductFactory, OrderFactory, OrderItemFactory

register(UserFactory)
register(CategoryFactory)
register(ProductFactory)
register(OrderFactory)
register(OrderItemFactory)


@pytest.fixture
def api_client():
    """DRF test client"""
    return APIClient()

@pytest.fixture
def admin_client(api_client, user_factory):
    """Authenticated API client with an admin user"""
    user = user_factory(is_staff=True)
    api_client.force_authenticate(user=user)
    return api_client