from rest_framework import serializers
from .models import Category
import logging

logger = logging.getLogger(__name__)

class CategorySerializer(serializers.ModelSerializer):
    parent_id = serializers.IntegerField(allow_null=True, required=False)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent_id', 'level', 'is_deleted',  'children']
        read_only_fields = ['level']
        extra_kwargs = {
            'name':{'required':False},
            'is_deleted':{'required':False}
        }
    
    def get_children(self, obj):
        is_deleted_filter = self.context.get('view').action == 'deleted' if self.context.get('view') else False
        children = obj.children.filter(is_deleted=is_deleted_filter)
        
        return CategorySerializer(children, many=True, context=self.context).data
    
    def validate(self,data):  
        
        parent_id = data.get('parent_id', self.instance.parent_id if self.instance else None)
        name = data.get('name', self.instance.name if self.instance else None)
        is_deleted = data.get('is_deleted', True)

        # Fetch parent if parent_id is provided
        parent = None
        if parent_id is not None:
            try:
                parent = Category.objects.get(id=parent_id, is_deleted=False)
                data['parent'] = parent
            except Category.DoesNotExist:
                raise serializers.ValidationError({"parent_id":"Parent category does not exist or is deleted."})
        else:
            data['parent'] = None

        level = 1 if parent is None else min(parent.level + 1, 3)
        data['level'] = level

        # Validate parent level
        if parent and parent.level >= level:
            raise serializers.ValidationError({"parent_id":"Parent level must be less than current level."})
        
        # Validate name uniqueness
        if name and not is_deleted and Category.objects.filter(name=name, is_deleted=False).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError({"name":"Category name must be unique among active categories."})
        
        # Validate reactivation
        if self.instance and 'is_deleted' in data and not data['is_deleted']:
            #check parent is not deleted
            if self.instance.parent and self.instance.parent.is_deleted:
                raise serializers.ValidationError({"parent_id":"Cannot reactivate: Parent category is deleted."})
            def check_descendants(category):
                if not category.is_deleted and Category.objects.filter(name=category.name, is_deleted=False).exclude(id=category.id).exists():
                    raise serializers.ValidationError({"name":f"Name '{category.name}' conflicts with an active category."})
                for child in category.children.all():
                    check_descendants(child)
            check_descendants(self.instance)
           
        return data
    
    def create(self, validated_data):
        
        parent = validated_data.pop('parent', None)
        validated_data.pop('parent_id', None) # Remove parent_id to avoid conflicts
        
        return Category.objects.create(parent=parent, **validated_data)
    
    def update(self, instance, validated_data):
        
        parent = validated_data.pop('parent', None)
        
        if 'parent_id' in self.initial_data:
            instance.parent = parent
        
        for attr, value in validated_data.items():
            if value is not None:
                setattr(instance, attr, value)
        instance.level= instance.parent.level + 1 if instance.parent else 1
        instance.save()

        # Update descendant levels
        def update_descendant_levels(category):
            new_level = min(category.parent.level + 1, 3) if category.parent else 1
            if category.level != new_level:
                category.level = new_level
                category.save()
            
            for child in category.children.all():
                update_descendant_levels(child)
        for child in instance.children.all():
            update_descendant_levels(child)
        return instance