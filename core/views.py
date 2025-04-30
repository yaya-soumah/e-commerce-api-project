from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from .serializers import LoginSerializer
from rest_framework.authtoken.models import Token
import logging

logger = logging.getLogger(__name__)

class LoginView(APIView):
    permission_classes = [AllowAny]
    # authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(request=request, username=username, password=password)
            logger.debug(f"Authenticated user: {user}")
            if user is not None:
                token, _ = Token.objects.get_or_create(user=user)
                response_data = {
                    'id': user.id,
                    'role_name':user.profile.role.name if user.profile.role else None,
                    'username': user.username,
                    'email': user.email,
                    'token': f"Bearer {token.key}"
                }
                return Response(response_data, status=status.HTTP_200_OK)
            return Response({'error':'Invalid credentials'},status=status.HTTP_401_UNAUTHORIZED)
        logger.debug(f"Serializer errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
