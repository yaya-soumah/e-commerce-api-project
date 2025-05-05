from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Category
from rest_framework.permissions import IsAdminUser
from .serializers import CategorySerializer
from apps.core.pagination import StandardResultsSetPagination

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_deleted=False).order_by('id')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if self.action in ['reactivate','permanent']:
            return Category.objects.filter(is_deleted=True).order_by('id')
        elif self.action == 'deleted':
            return Category.objects.filter(is_deleted=True).order_by('id')
        queryset = super().get_queryset()
        level = self.request.query_params.get('level')
        if self.action == 'list':
            if level and level.isdigit():
                level = int(level)
                if 1 <= level <= 3:
                    queryset = queryset.filter(level=level)
                else:
                    queryset = queryset.filter(level=1) # Default to level 1
            else:
                queryset = queryset.filter(level=1) 
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['depth'] = 0
        return context
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Mark category and all descendants as deleted
        def mark_deleted(category):
            category.is_deleted = True
            category.save()
            for child in category.children.all():
                mark_deleted(child)
        mark_deleted(instance)
        
        return Response({}, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['patch'], url_path='reactivate')
    def reactivate(self,request, pk=None):
        instance = self.get_object()

        def reactivate_category(category):
            serializer = self.get_serializer(category, data={'is_deleted':False}, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            for child in category.children.all():
                reactivate_category(child)
        reactivate_category(instance)   
           
        return Response(self.get_serializer(instance).data)
    
    @action(detail=False, methods=['get'], url_path='deleted')
    def deleted(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset,many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['delete'], url_path='permanent')
    def permanent(self,request, pk=None):
        instance = self.get_object()
        if not instance.is_deleted:
            return Response({"deatil": "Only soft-deleted categories can be permanently deleted."}, status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'], url_path='permanent/bulk')
    def permanent_bulk(self,request, pk=None):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({"detail": "No IDs provided."}, status=status.HTTP_400_BAD_REQUEST)
        categories = Category.objects.filter(id__in=ids, is_deleted=True)
        if not categories.exists():
            return Response({"detail":"No soft-deleted categories found for provided IDs."})
        if len(categories) != len(ids):
            return Response({"detail":"Some Ids do not correspond to soft-deleted categories."}, status=status.HTTP_400_BAD_REQUEST)
        categories.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
       