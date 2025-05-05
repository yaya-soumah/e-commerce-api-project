from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from .models import Role
from .serializers import RoleSerializer

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by('id')
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None

    def destroy(self, request, *args, **kwargs):
        instance =  self.get_object()
        instance.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)