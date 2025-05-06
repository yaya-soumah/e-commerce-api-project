from rest_framework import serializers
from .models import User, UserProfile
from apps.roles.models import Role

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
        # Ensure UserProfile is created
        UserProfile.objects.get_or_create(user=user)
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

class UserAssingRoleSerializer(serializers.Serializer):
    role_id =  serializers.IntegerField(required=False)
    role_name = serializers.CharField(required=False)
        
    def validate(self, data):
        role_id = data.get('role_id')
        role_name = data.get('role_name')
        
        if not role_id and not role_name:
            raise serializers.ValidationError({"role":"Either role_id or role_name must be provided."})
        if role_id and role_name:
            raise serializers.ValidationError({"role":"Provide either role_id or role_name, not both."})
        if role_id:
            if not Role.objects.filter(id=role_id).exists():
                raise serializers.ValidationError({"role":"Role does not exist."})
        elif role_name:
            if not Role.objects.filter(name=role_name).exists():
                raise serializers.ValidationError({"role":"Role does not exist."})
                
        return data
    
    def update(self, instance, validated_data):
        
        role_id = validated_data.get('role_id')
        role_name = validated_data.get('role_name')
        
        if role_id:
            role = Role.objects.get(id=role_id)
        else:
            role = Role.objects.get(name=role_name)
        
        profile, created = UserProfile.objects.get_or_create(user=instance)
        profile.role = role
        profile.save()
        return instance
    
    def to_representation(self, instance):
        return {
            'id': instance.id,
            'username': instance.username,
            'email': instance.email,
            'role': instance.profile.role.name if instance.profile and instance.profile.role else None
        }