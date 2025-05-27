from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import serializers
from apps.core.pagination import StandardResultsSetPagination
from apps.categories.models import Category
from .serializers import CategoryAttributeSerializer
from .models import CategoryAttribute

class CategoryAttributeViewSet(viewsets.ModelViewSet):
    serializer_class = CategoryAttributeSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        cat_id = self.kwargs.get('cat_id')
        try:
            Category.objects.get(id=cat_id, is_deleted=False)
        except Category.DoesNotExist:
            raise serializers.ValidationError({"cat_id":"Category does not exists or is deleted."})
        
        queryset = CategoryAttribute.objects.filter(cat_id=cat_id).order_by('id')
        sel = self.request.query_params.get('sel')
        if sel in ['only', 'many']:
            queryset = queryset.filter(attr_sel=sel).order_by('id')
        return queryset
    
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['cat_id'] = self.kwargs.get('cat_id')
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data=serializer.data
        return Response({
            "data":data,
            "message":"Attribute created successfully"
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        cat_id = self.kwargs.get('cat_id')
        
        request.data['cat_id'] = cat_id
        
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)