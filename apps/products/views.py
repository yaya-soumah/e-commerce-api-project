from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
import os
from django.db.models import Q
from rest_framework.decorators import action
from PIL import Image
from .models import Product, ProductPicture, ProductAttribute
from .serializers import ProductSerializer, ProductPictureSerializer, ProductAttributeSerializer, BulkProductSerializer
from apps.core.pagination import StandardResultsSetPagination

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Product.objects.filter(is_deleted=False).order_by('id')
        query = self.request.query_params.get('query')
        if query:
            queryset = queryset.filter(
                Q(goods_name__icontains=query) | Q(goods_description__icontains=query)
            )
        return queryset
    
    def destroy(self,request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['patch'], url_path='state')
    def update_state(self,request, pk=None):
        product = self.get_object()
        goods_state = request.data.get('goods_state')
        if goods_state not in [0,1,2]:
            return Response({"goods_state":"Must be 0,1, or 2"}, status=status.HTTP_400_BAD_REQUEST)
        product.goods_state = goods_state
        product.save()
        return Response({"data":{"id":product.id, "goods_state": product.goods_state},
                         "message":"State updated successfully"}, 
                         status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], url_path='pics')
    def update_pics(self, request, pk=None):
        product = self.get_object()
        serializer = ProductPictureSerializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        product.pics.all().delete()
        for pic_data in serializer.validated_data:
            ProductPicture.objects.create(product=product, **pic_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['put'], url_path='attribues')
    def update_attributes(self, request, pk=None):
        product = self.get_object()
        
        serializer = ProductAttributeSerializer(data=request.data, many=True, context={'product': product})
        serializer.is_valid(raise_exception=True)
        product.attrs.all().delete()
        for attr_data in serializer.validated_data:
            ProductAttribute.objects.create(goods_id=product, **attr_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post','put'], url_path='bulk')
    def bulk(self, request):
        if request.method == 'POST':
            serializer = BulkProductSerializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            products = serializer.save()
            return Response(ProductSerializer(products, many=True).data, status=status.HTTP_201_CREATED)
        elif request.method == 'PUT':
            goods_ids = [item.get('goods_id') for item in request.data]
            instances = Product.objects.filter(goods_id__in=goods_ids, is_deleted=False)
            if len(instances) != len(goods_ids):
                return Response({"error":"Some products not found or deleted"}, status=status.HTTP_400_BAD_REQUEST)
            serializer = BulkProductSerializer(instances, data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
    
class UploadView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"data":{},"message": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        filename = file.name
        tmp_path = os.path.join('tmp_uploads', filename)
        full_path = os.path.join(settings.MEDIA_ROOT, tmp_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Resize images
        img = Image.open(full_path)
        big_path = os.path.join(settings.MEDIA_ROOT, 'uploads/goodspics', f"big_{filename}")
        mid_path = os.path.join(settings.MEDIA_ROOT, 'uploads/goodspics', f"mid_{filename}")
        sma_path = os.path.join(settings.MEDIA_ROOT, 'uploads/goodspics', f"sma_{filename}")
        os.makedirs(os.path.dirname(big_path), exist_ok=True)

        img.resize((800,800), Image.LANCZOS).save(big_path)
        img.resize((400,400), Image.LANCZOS).save(mid_path)
        img.resize((100,100), Image.LANCZOS).save(sma_path)

        url = f"{settings.MEDIA_URL} {tmp_path}"
        return Response({"data":{"tmp_path":tmp_path, "url":url},"message":"image uploaded succesfully"}, status=status.HTTP_201_CREATED)
