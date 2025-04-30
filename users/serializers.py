from rest_framework import serializers
from .models import UserProfile, Role, Permission, User

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id','name','level','parent']

class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id','name','description','permissions']

class UserListSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='profile.role.name', read_only=True, allow_blank=True)
    created_at = serializers.DateTimeField(source='profile.created_at', read_only=True)

    class Meta:
        model = User
        fields = ['id','username', 'email', 'created_at', 'role_name']

class UserCreateSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='profile.role.name', read_only=True, allow_null=True)
    created_at = serializers.DateTimeField(source='profile.created_at', read_only=True)
    updated_at = serializers.DateTimeField(source='profile.updated_at', read_only=True)
    is_deleted = serializers.BooleanField(source='profile.is_deleted', read_only=True)
    is_active = serializers.BooleanField( read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role_name', 'created_at', 'updated_at', 'is_deleted', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email',''),
            password=validated_data['password']
        )

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='profile.role.name', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ['id','role_name','username','email']


class AdminUserCreateSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='profile.role.name', read_only=True, required=False, allow_null=True)
    created_at = serializers.DateTimeField(source='profile.created_at', read_only=True)
    updated_at = serializers.DateTimeField(source='profile.updated_at', read_only=True)
    is_deleted = serializers.BooleanField(source='profile.is_deleted', read_only=True)
    is_active = serializers.BooleanField( read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role_name', 'created_at', 'updated_at', 'is_deleted', 'is_active']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_staff=True,
            is_superuser=True,
        )

        admin_role, _ = Role.objects.get_or_create(
            name='Admin',
            defaults={
                'description': 'System Administrator',
            }
        )
        user.profile.role = admin_role
        user.profile.save()
        return user
