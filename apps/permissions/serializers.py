from rest_framework import serializers
from .models import Permission

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
        # level = data.get('level', self.instance.level if self.instance else None)
        level = 1
        # Default level to 1 if parent is None and level not provided
        if parent is None:
            data['level'] = level
            # level = 1
        # If parent is provided and level not provided, default to parent.level + 1
        if parent:
            data['level'] = min(parent.level + 1, 4)
            level = data['level']

        # validate level range
        if not 1 <= level <= 4:
            raise serializers.ValidationError({"level":"Level must be between 1 and 4."})
        
        # Level 1 must have no parent
        if level == 1 and parent is not None:
            raise serializers.ValidationError({"parent":"Level 1 permissions cannot have a parent."})
        
        # Non-level 1 must have a parent
        if level > 1 and parent is None:
            raise serializers.ValidationError({"parent":"Permission with Level > 1 must have a parent."})
        
        # Validate parent level 
        if parent and parent.level >= level:
            raise serializers.ValidationError({"parent":"Parent level must be less than currrent level."})
        
        # Validate name uniqueness
        name = data.get('name', self.instance.name if self.instance else None)
        if name and Permission.objects.filter(name__iexact=name).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError({"name":"Permission name must be unique."})
                
        return data