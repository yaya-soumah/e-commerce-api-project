from rest_framework import serializers
from .models import CategoryAttribute
from apps.categories.models import Category

class CategoryAttributeSerializer(serializers.ModelSerializer):
    cat_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.filter(is_deleted=False))
    attr_vals = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = CategoryAttribute
        fields = ['id', 'attr_name', 'cat_id', 'attr_sel', 'attr_write', 'attr_vals']
        

    def validate(self, data):
        attr_sel = data.get('attr_sel')
        attr_write = data.get('attr_write')
        attr_vals = data.get('attr_vals')
        attr_name = data.get('attr_name')
        cat_id = data.get('cat_id')

        try:
            category = Category.objects.get(id=cat_id, is_delete=False)
            data['cat_id'] = category
        except Category.DoesNotExist:
            raise serializers.ValidationError({"cat_id":"Category does not exist or is delete."})

        
        return data