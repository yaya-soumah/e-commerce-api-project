from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework import serializers
from apps.core.pagination import StandardResultsSetPagination
from django.contrib.auth import authenticate
from .serializers import CategoryAttributeSerializer
from .models import Category, CategoryAttribute

class CategoryAttributeViewSet(viewsets.ModelViewSet):
    serializer_class = CategoryAttributeSerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        category_id = self.kwargs.get('category_id')
        queryset = CategoryAttribute.objects.filter(cat_id=category_id)
        sel = self.request.query_params.get('sel')
        if sel in ['only', 'many']:
            queryset = queryset.filter(attr_sel=sel)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['category_id'] = self.kwargs.get('category_id')
        return context

    def perform_create(self, serializer):
        category_id = self.kwargs.get('category_id')
        try:
            category = Category.objects.get(id=category_id, is_deleted=False)
        except Category.DoesNotExist:
            raise serializers.ValidationError({"cat_id": "Category does not exist or is deleted."})
        serializer.save(cat_id=category)