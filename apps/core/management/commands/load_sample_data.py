from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.categories.models import Category
from apps.attributes.models import CategoryAttribute
from apps.roles.models import Role
from apps.permissions.models import Permission
from apps.users.models import UserProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Load sample data into the database'

    def handle(self, *args, **kwargs):
        # Clear existing data
        User.objects.all().delete()
        UserProfile.objects.all().delete()
        Category.objects.all().delete()
        CategoryAttribute.objects.all().delete()
        Role.objects.all().delete()
        Permission.objects.all().delete()

        # Create permissions
        manage_categories = Permission.objects.create(
            name='Manage Categories',
            level=1
        )
        view_products = Permission.objects.create(
            name='View Products',
            level=1
        )
        manage_subcategories = Permission.objects.create(
            name='Manage Subcategories',
            level=2,
            parent=manage_categories
        )

        # Create roles
        admin_role = Role.objects.create(name='Admin', description='Administrator role')
        customer_role = Role.objects.create(name='Customer', description='Customer role')
        admin_role.permissions.set([manage_categories, view_products, manage_subcategories])
        customer_role.permissions.set([view_products])

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

        # Assign roles to profiles (profiles auto-created by signal)
        UserProfile.objects.filter(user=admin).update(role=admin_role)
        UserProfile.objects.filter(user=user1).update(role=customer_role)

        # Create categories
        electronics = Category.objects.create(name='Electronics')
        laptops = Category.objects.create(name='Laptops', parent=electronics, level=2)
        smartphones = Category.objects.create(name='Smartphones', parent=electronics, level=2)
        accessories = Category.objects.create(name='Accessories', parent=laptops, level=3)

        # Create attributes
        CategoryAttribute.objects.create(
            attr_name='Color',
            cat_id=electronics,
            attr_sel='many',
            attr_write='list',
            attr_vals='Red,Blue,Black'
        )
        CategoryAttribute.objects.create(
            attr_name='Screen Size',
            cat_id=laptops,
            attr_sel='only',
            attr_write='list',
            attr_vals='13-inch,15-inch,17-inch'
        )
        CategoryAttribute.objects.create(
            attr_name='Storage',
            cat_id=smartphones,
            attr_sel='only',
            attr_write='list',
            attr_vals='64GB,128GB,256GB'
        )
        CategoryAttribute.objects.create(
            attr_name='Material',
            cat_id=accessories,
            attr_sel='many',
            attr_write='manual',
            attr_vals=None
        )

        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully!'))