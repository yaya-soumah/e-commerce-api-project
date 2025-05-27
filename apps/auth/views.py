from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from .serializers import LoginSerializer

class LoginViewSet(viewsets.GenericViewSet):
    serializer_class = LoginSerializer 
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
        
    


        





