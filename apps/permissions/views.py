from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import Permission
from .serializers import PermissionSerializer

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all().order_by('id')
    serializer_class = PermissionSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None 

    def get_queryset(self):
        if self.action == 'list':
            return Permission.objects.filter(level=1).order_by('id')            
        return Permission.objects.all().order_by('id')
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        view_type = self.request.query_params.get('view','list')
        context['view_type'] = view_type
        context['depth'] = 0
        return context        
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    # @action(detail=False, methods=['get'], url_path='list')