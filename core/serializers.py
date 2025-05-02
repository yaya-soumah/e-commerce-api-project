from rest_framework import serializers
from .models import Category
from users.models import User

class LoginSerializer(serializers.ModelSerializer):
    # Input fields
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    # Output fields
    id = serializers.IntegerField(read_only=True)
    role_name=serializers.CharField(source='profile.role.name', read_only=True, allow_null=True)
    email=serializers.EmailField(read_only=True)
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username','password','email','role_name','token']
    
    def get_token(self, obj):
        from rest_framework.authtoken.models import Token
        token, _ = Token.objects.get_or_create(user=obj)
        return f"Bearer {token}"

class CategorySerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(allow_null=True, required=False)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent_id', 'level', 'is_deleted',  'children']
        read_only_fields = ['level','is_deleted']
        extra_kwargs = {
            'name':{'required':False}
        }
    
    def get_children(self, obj):
        
        children = obj.children.filter(is_deleted=False)
        return CategorySerializer(children, many=True).data
    
    def validate(self,data):  

        parent_id = data.get('parent_id', self.instance.parent_id if self.instance else None)
        name = data.get('name', self.instance.name if self.instance else None)

        # Fetch parent if parent_id is provided
        parent = None
        if parent_id is not None:
            try:
                parent = Category.objects.get(id=parent_id, is_deleted=False)
                data['parent'] = parent
            except Category.DoesNotExist:
                raise serializers.ValidationError({"parent_id":"Parent category does not exist."})
        else:
            data['parent'] = None

        level = 1 if parent is None else min(parent.level + 1, 3)
        data['level'] = level

        # Level 1 must have no parent
        if level == 1 and parent_id is not None:
            raise serializers.ValidationError({"parent_id":" Level 1 category cannot have a parent."})
        
        # Non-level 1 must have a parent
        if level > 1 and parent_id is None:
            raise serializers.ValidationError({"parent_id": "Category with level > 1 must have a parent."})
        
        # Validate parent level
        if parent and parent.level > level:
            raise serializers.ValidationError({"parent_id":"Parent level must be less than current level."})
        
        # Validate name uniqueness
        if name and Category.objects.filter(name=name).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError({"name":"Category name must be unique."})
        print(f"validate method data just before return: {str(data)}")
        return data
    
    def create(self, validated_data):
        parent = validated_data.pop('parent', None)
        validated_data.pop('parent_id', None) # Remove parent_id to avoid conflicts
        
        return Category.objects.create(parent=parent, **validated_data)
    
    def update(self, instance, validated_data):
        parent = validated_data.pop('parent', None)
        
        print(f"initial_data {str(self.initial_data)}")
        print(f"validated_data {str(validated_data)}")
        if 'parent' in self.initial_data:
            instance.parent = parent
        
        for attr, value in validated_data.items():
            if value is not None:
                setattr(instance, attr, value)
        instance.level= instance.parent.level + 1 if instance.parent else 1
        instance.save()
        return instance

        
    