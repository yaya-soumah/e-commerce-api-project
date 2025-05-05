from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.categories.models import Category
from apps.roles.models import Role
from apps.permissions.models import Permission
from apps.users.models import UserProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Load sample data into the database'

    def handle(self, *args, **kwargs):
        # Clear existing data
        User.objects.all().delete()
        Category.objects.all().delete()
        Role.objects.all().delete()
        Permission.objects.all().delete()
        UserProfile.objects.all().delete()

        # Create users
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user123'
        )

        # Create profiles (should be auto-created by signal)
        # UserProfile.objects.get_or_create(user=admin)
        # UserProfile.objects.get_or_create(user=user1)

        # Create roles
        admin_role = Role.objects.create(name='Admin', description='administrator')
        customer_role = Role.objects.create(name='Customer',description='Manages Products and orders')

        # Assign roles
        # admin_role.users.add(admin)
        # customer_role.users.add(user1)

        # Create permissions
        manage_categories = Permission.objects.create(
            name='Manage Categories',
        )
        view_products = Permission.objects.create(
            name='View Products',
        )

        # Create categories
        electronics = Category.objects.create(name='Electronics')
        laptops = Category.objects.create(name='Laptops', parent=electronics)
        smartphones = Category.objects.create(name='Smartphones', parent=electronics)
        accessories = Category.objects.create(name='Accessories', parent=laptops)

        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))