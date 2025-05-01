from rest_framework import serializers
from .models import UserProfile, Role, Permission, User

class PermissionSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(queryset=Permission.objects.all(), allow_null=True, required=False)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Permission
        fields = ['id','name','level','parent','children', 'created_at', 'updated_at']

    def get_children(self, obj):
        
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
    
    def validate(self, data):
        parent = data.get('parent', self.instance.parent if self.instance else None)
        level = data.get('level', self.instance.level if self.instance else None)
        
        # Default level to 1 if parent is None and level not provided
        if parent is None and level is None:
            data['level'] = 1
            level = 1
        # If parent is provided and level not provided, default to parent.level + 1
        if parent and level is None:
            data['level'] = parent.level + 1
            level = data['level']

        # validate level range
        if not 1 <= level <= 4:
            raise serializers.ValidationError({"level":"Level must be between 1 and 4."})
        
        # Level 1 must have no parent
        if level == 1 and parent is not None:
            raise serializers.ValidationError({"parent":"Level 1 permissions cannot have a parent."})
        
        # Non-level 1 must have a parent
        if level > 1 and parent is None:
            raise serializers.ValidationError({"parent":"Permission with Level 1 must have a parent."})
        
        # Validate parent level 
        if parent and parent.level >= level:
            raise serializers.ValidationError({"parent":"Parent level must be less than currrent level."})
        
        # Validate name uniqueness
        name = data.get('name', self.instance.name if self.instance else None)
        if name and Permission.objects.filter(name=name).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError({"name":"Permission name must be unique."})
                
        return data


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
        print(f"Updating user {instance.username}: role_id={validated_data.get('role_id')}, role_name={validated_data.get('role_name')}")
        role_id = validated_data.get('role_id')
        role_name = validated_data.get('role_name')
        print(f"Assigning role to user {instance.username}: role_id={role_id}, role_name={role_name}")
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

