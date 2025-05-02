from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from .models import UserProfile, Role, User, Permission
from .serializers import (UserListSerializer, 
                          UserCreateSerializer, 
                          UserDetailSerializer, 
                          AdminUserCreateSerializer, 
                          PermissionSerializer, 
                          RoleSerializer,
                          UserAssingRoleSerializer
                          )
from django.db.models import Q

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(profile__is_deleted=False)
    permission_classes = [IsAdminUser]

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

    def list(self,request):
        query = request.query_params.get('query','')
        pagenum = request.query_params.get('pagenum',1)
        pagesize = request.query_params.get('pagesize',10)

        try:
            pagenum = int(pagenum)
            pagesize = int(pagesize)
            if pagenum < 1 or pagesize < 1:
                raise ValueError
        except ValueError:
            return Response({'error': 'Invalid pagenum or pagesize'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.queryset
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) | Q(email__icontains=query)
            )
        paginator = self.paginator
        paginator.page_size = pagesize
        try:
            page = paginator.paginate_queryset(queryset, request)
        except Exception:
            return Response({'error': 'Invalid page number'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(page, many=True)
        return paginator.get_paginated_response({
            'totalpages': paginator.page.paginator.num_pages,
            'pagenum': pagenum,
            'users': serializer.data,})

    # soft delete instead of hard delete
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.profile.is_deleted = True
        instance.profile.save()
        return Response({},status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['patch'], url_path='assign-role')
    def assign_role(self, request, pk=None):
        user = self.get_object()
        serializer = UserAssingRoleSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_user = serializer.save()
        
        return Response(serializer.to_representation(updated_user), status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'], url_path='admin')
    def create_admin(self, request):
        serializer = AdminUserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
        context['view_type'] = 'tree'
        context['depth'] = 0
        return context        
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)
    
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all().order_by('id')
    serializer_class = RoleSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None

    def destroy(self, request, *args, **kwargs):
        instance =  self.get_object()
        instance.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)