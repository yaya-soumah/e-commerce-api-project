from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .models import User
from .serializers import UserListSerializer, UserCreateSerializer, UserDetailSerializer, AdminUserCreateSerializer, UserAssingRoleSerializer
from django.db.models import Q
from apps.core.pagination import StandardResultsSetPagination

class UserViewSet(viewsets.ModelViewSet):    
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'create_admin':
            return AdminUserCreateSerializer
        if self.action == 'assign-role':
            return UserAssingRoleSerializer
        return UserDetailSerializer
    
    def get_queryset(self):
        queryset = User.objects.filter(profile__is_deleted=False)
        query = self.request.query_params.get('query')
        if query:
            queryset = queryset.filter(Q(username__icontains=query) | Q(email__icontains=query))
        return queryset    

    # soft delete instead of hard delete
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.profile.is_deleted = True
        instance.profile.save()
        return Response(data={"data":{},"message":"user removed successfully"},
                            status=status.HTTP_204_NO_CONTENT
                           )

    @action(detail=True, methods=['patch'], url_path='assign-role')
    def assign_role(self, request, pk=None):
        user = self.get_object()
        serializer = UserAssingRoleSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(data={"data":serializer.data,"message":"role assigned successfully"},
                            status=status.HTTP_200_OK
                           )

    @action(detail=False, methods=['post'], url_path='admin')
    def create_admin(self, request):
        serializer = AdminUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"data":serializer.data,"message":"Admin created successfully"}, status=status.HTTP_201_CREATED)