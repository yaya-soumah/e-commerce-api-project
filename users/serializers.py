from rest_framework import serializers
from .models import UserProfile, Role, Permission, User

class PermissionSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), allow_null=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Permission
        fields = ['id','name','level','parent','children', 'created_at', 'updated_at']

    def get_children(self, obj):
        # Only include children in the tree view
        if self.context.get('view_type') == 'tree':
            depth = self.context.get('depth',0)
            if depth >=4:
                return []
            
            children = obj.children.all() if hasattr(obj, 'children') else []
            
            return PermissionSerializer(
                children, 
                many=True, 
                context={**self.context, 'depth': depth + 1}
                ).data
        return []


class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Role
        fields = ['id','name','description','permissions']

    def to_representation(self, instance):
        # Include full permission details in response
        representation = super().to_representation(instance)
        representation['permissions'] = PermissionSerializer(
            instance.permissions.all(),
            many=True,
            context={'view_type':'list', 'depth':0}
        ).data
        return representation

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
