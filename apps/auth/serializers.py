from rest_framework import serializers
from apps.users.models import User

class LoginSerializer(serializers.ModelSerializer):
    # Input fields
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    # Output fields
    id = serializers.IntegerField(read_only=True)
    role_name=serializers.CharField(source='profile.role.name', read_only=True, allow_null=True)
    email=serializers.EmailField(read_only=True)
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username','password','email','role_name','token']
    
    def get_token(self, obj):
        from rest_framework_simplejwt.tokens import RefreshToken
        
        refresh = RefreshToken.for_user(obj)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    
    def to_representation(self, instance):
        
        data = super().to_representation(instance)
        token = data.pop('token')
        refresh = token['refresh']
        access = token['access']
        return {
            'user':data,
            'access': access,
            'refresh':refresh
        }
        
