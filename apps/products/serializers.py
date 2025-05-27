from rest_framework import serializers
from .models import Product, ProductPicture, ProductAttribute
from apps.categories.models import Category
from apps.attributes.models import CategoryAttribute
from django.conf import settings
from PIL import Image
import os

class ProductPictureSerializer(serializers.ModelSerializer):
    pic = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = ProductPicture
        fields = ['id', 'pics_big', 'pics_mid', 'pics_sma', 'pic']
        read_only_fields = ['id', 'pics_big', 'pics_mid', 'pics_sma']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['pic'] = representation.pop('pics_big')
        representation.pop('pics_mid')
        representation.pop('pics_sma')
        representation['product'] = instance.product.id
        return representation

    def to_internal_value(self, data):
        
        if not isinstance(data, dict):
            raise serializers.ValidationError({"pic": "Invalid data format."})

        pic_path = data.get('pic')
        if not pic_path:
            raise serializers.ValidationError({"pic": "This field is required when provided."})

        filename = os.path.basename(pic_path)
        full_path = os.path.join(settings.MEDIA_ROOT, pic_path)

        if not os.path.exists(full_path):
            raise serializers.ValidationError({"pic": f"File {pic_path} does not exist."})

        try:
            img = Image.open(full_path)
            big_path = os.path.join(settings.MEDIA_ROOT, 'uploads/goodspics', f"big_{filename}")
            mid_path = os.path.join(settings.MEDIA_ROOT, 'uploads/goodspics', f"mid_{filename}")
            sma_path = os.path.join(settings.MEDIA_ROOT, 'uploads/goodspics', f"sma_{filename}")
            os.makedirs(os.path.dirname(big_path), exist_ok=True)

            img.resize((800, 800), Image.LANCZOS).save(big_path)
            img.resize((400, 400), Image.LANCZOS).save(mid_path)
            img.resize((100, 100), Image.LANCZOS).save(sma_path)

            data = {
                'pics_big': os.path.join('uploads/goodspics', f"big_{filename}"),
                'pics_mid': os.path.join('uploads/goodspics', f"mid_{filename}"),
                'pics_sma': os.path.join('uploads/goodspics', f"sma_{filename}")
            }
        except Exception as e:
            raise serializers.ValidationError({"pic": f"Failed to process image: {str(e)}"})

        return data

    def create(self, validated_data):
        product = self.context.get('product')
        if not product:
            raise serializers.ValidationError({"product": "Product is required."})

        pics_big = validated_data.pop('pics_big')
        pics_mid = validated_data.pop('pics_mid')
        pics_sma = validated_data.pop('pics_sma')
        instance = ProductPicture.objects.create(
            product=product,
            pics_big=pics_big,
            pics_mid=pics_mid,
            pics_sma=pics_sma,
            **validated_data
        )
        return instance

class ProductAttributeSerializer(serializers.ModelSerializer):
    attr_id = serializers.PrimaryKeyRelatedField(
        queryset=CategoryAttribute.objects.all(), source='attribute'
    )
    attr_value = serializers.CharField()
    attr_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    attr_name = serializers.CharField(source='attribute.attr_name', read_only=True)
    attr_sel = serializers.CharField(source='attribute.attr_sel', read_only=True)
    attr_write = serializers.CharField(source='attribute.attr_write', read_only=True)
    attr_vals = serializers.CharField(source='attribute.attr_vals', read_only=True)

    class Meta:
        model = ProductAttribute
        fields = ['product', 'attr_id', 'attr_value', 'attr_price', 'attr_name', 'attr_sel', 'attr_write', 'attr_vals']
        read_only_fields = ['product']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = instance.product.id
        return representation

    def validate(self, data):
        product = self.context.get('product')
        attribute = data.get('attribute')
        if product and not product.categories.filter(id=attribute.cat_id.id).exists():
            raise serializers.ValidationError({
                "attr_id": f"Attribute {attribute} does not belong to product's categories."
            })
        return data

class ProductSerializer(serializers.ModelSerializer):
    goods_cat = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_deleted=False), many=True, source='categories'
    )
    pics = ProductPictureSerializer(many=True, required=False)
    attrs = ProductAttributeSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'id', 'goods_name', 'goods_cat', 'goods_price', 'goods_quantity',
            'goods_weight', 'goods_state', 'goods_description', 'created_at',
            'updated_at', 'hot_quantity', 'is_promote', 'goods_big_logo',
            'goods_small_logo', 'is_deleted', 'pics', 'attrs'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def to_internal_value(self, data):
        validated_data = super().to_internal_value(data)

        # Store original pics data for create/update
        pics_data = data.get('pics', [])
        validated_data['pics'] = pics_data  # Keep original [{'pic': ...}]

        return validated_data

    def validate(self, value):
        goods_cat = value.get('categories', [])
        attrs = value.get('attrs', [])
        product = self.context.get('product')

        goods_cat_ids = [cat.id for cat in goods_cat] if goods_cat else []
        for attr in attrs:
            attribute = attr.get('attribute')
            if attribute:
                cat_id = attribute.cat_id.id
                if not product and cat_id not in goods_cat_ids:
                    raise serializers.ValidationError({
                        "attrs": f"Attribute {attribute} does not belong to provided categories {goods_cat_ids}."
                    })
                elif product and not product.categories.filter(id=cat_id).exists():
                    raise serializers.ValidationError({
                        "attrs": f"Attribute {attribute} does not belong to product's categories."
                    })

        return value

    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        pics = validated_data.pop('pics', [])
        attrs = validated_data.pop('attrs', [])

        product = Product.objects.create(**validated_data)
        product.categories.set(categories)

        for pic_data in pics:
            pic_serializer = ProductPictureSerializer(data=pic_data, context={'product': product})
            if pic_serializer.is_valid():
                pic_serializer.save()
            else:
                raise serializers.ValidationError(pic_serializer.errors)

        for attr_data in attrs:
            ProductAttribute.objects.create(product=product, **attr_data)

        return product

    def update(self, instance, validated_data):
        categories = validated_data.pop('categories', None)
        pics = validated_data.pop('pics', None)
        attrs = validated_data.pop('attrs', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if categories is not None:
            instance.categories.set(categories)

        if pics is not None:
            instance.pics.all().delete()
            for pic_data in pics:
                pic_serializer = ProductPictureSerializer(data=pic_data, context={'product': instance})
                if pic_serializer.is_valid():
                    pic_serializer.save()
                else:
                    raise serializers.ValidationError(pic_serializer.errors)

        if attrs is not None:
            instance.attrs.all().delete()
            for attr_data in attrs:
                ProductAttribute.objects.create(product=instance, **attr_data)

        return instance

class BulkProductSerializer(serializers.ModelSerializer):
    goods_cat = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.filter(is_deleted=False), many=True, source='categories'
    )
    pics = ProductPictureSerializer(many=True, required=False)
    attrs = ProductAttributeSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            'id', 'goods_name', 'goods_cat', 'goods_price', 'goods_quantity',
            'goods_weight', 'goods_state', 'goods_description', 'pics', 'attrs'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_deleted']

    def to_internal_value(self, data):
        validated_data = super().to_internal_value(data)

        # Store original pics data for create/update
        pics_data = data.get('pics', [])
        validated_data['pics'] = pics_data  # Keep original [{'pic': ...}]

        return validated_data

    def validate(self, value):
        goods_cat = value.get('categories', [])
        attrs = value.get('attrs', [])
        product = self.context.get('product')

        goods_cat_ids = [cat.id for cat in goods_cat] if goods_cat else []
        for attr in attrs:
            attribute = attr.get('attribute')
            if attribute:
                cat_id = attribute.cat_id.id
                if not product and cat_id not in goods_cat_ids:
                    raise serializers.ValidationError({
                        "attrs": f"Attribute {attribute} does not belong to provided categories {goods_cat_ids}."
                    })
                elif product and not product.categories.filter(id=cat_id).exists():
                    raise serializers.ValidationError({
                        "attrs": f"Attribute {attribute} does not belong to product's categories."
                    })

        return value

    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        pics = validated_data.pop('pics', [])
        attrs = validated_data.pop('attrs', [])

        product = Product.objects.create(**validated_data)
        product.categories.set(categories)

        for pic_data in pics:
            pic_serializer = ProductPictureSerializer(data=pic_data, context={'product': product})
            if pic_serializer.is_valid():
                pic_serializer.save()
            else:
                raise serializers.ValidationError(pic_serializer.errors)

        for attr_data in attrs:
            ProductAttribute.objects.create(product=product, **attr_data)

        return product

    def update(self, instance, validated_data):
        categories = validated_data.pop('categories', None)
        pics = validated_data.pop('pics', None)
        attrs = validated_data.pop('attrs', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if categories is not None:
            instance.categories.set(categories)

        if pics is not None:
            instance.pics.all().delete()
            for pic_data in pics:
                pic_serializer = ProductPictureSerializer(data=pic_data, context={'product': instance})
                if pic_serializer.is_valid():
                    pic_serializer.save()
                else:
                    raise serializers.ValidationError(pic_serializer.errors)

        if attrs is not None:
            instance.attrs.all().delete()
            for attr_data in attrs:
                ProductAttribute.objects.create(product=instance, **attr_data)

        return instance