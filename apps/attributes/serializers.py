from rest_framework import serializers
from .models import CategoryAttribute
from apps.categories.models import Category

class CategoryAttributeSerializer(serializers.ModelSerializer):
    cat_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.filter(is_deleted=False))
    attr_vals = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = CategoryAttribute
        fields = ['id', 'attr_name', 'cat_id', 'attr_sel', 'attr_write', 'attr_vals']
        extra_kwargs = {
            'attr_sel':{'required':False},
            'attr_write':{'required':False}     

        }

    def validate(self, data):
        
        attr_sel = data.get('attr_sel','only')
        attr_write = data.get('attr_write','manual')
        attr_vals = data.get('attr_vals')
        attr_name = data.get('attr_name')
        cat_id = data.get('cat_id').id
        

        # Validate unique attr_name per category
        if attr_name and CategoryAttribute.objects.filter(
            attr_name=attr_name, cat_id=cat_id
        ).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError({"attr_name":"Attribute name must be unique for this category."})
        
        # Validate attr_sel
        if attr_sel not in ['only','many']:
            raise serializers.ValidationError({"attr_sel":"Must be 'only' or 'many'."})
        
        # Validate attr_write
        if attr_write not in ['manual','list']:
            raise serializers.ValidationError({"attr_write":"Must be 'manual' or 'list'."})
        
        # Validate attr_vals
        if attr_write == 'list' and not attr_vals:
            raise serializers.ValidationError({"attr_vals": "Must provide values for 'list' write type."})
        
        if attr_write == 'manual' and attr_vals:
            raise serializers.ValidationError({"attr_vals": "Cannot provide values for 'manual' write type."})

        
        data['attr_sel'] = attr_sel
        data['attr_write'] = attr_write

        return data


        
    