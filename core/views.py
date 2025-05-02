from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser
from django.contrib.auth import authenticate
from .serializers import LoginSerializer, CategorySerializer
from .models import Category

class StandardResultsSetPagination(PageNumberPagination):
    page_size_query_param = 'pagesize'
    page_query_param = 'pagenum'

class LoginViewSet(viewsets.GenericViewSet):
    serializer_class = LoginSerializer  
    # authentication_classes = []
    permission_classes = [AllowAny]
    
    @action(detail=True, methods=['post'] )
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(request=request, username=username, password=password)            
        if user is not None:                
            response_serializer = LoginSerializer(user)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response({'error':'Invalid credentials'},status=status.HTTP_401_UNAUTHORIZED)
        
    

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_deleted=False).order_by('id')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
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



