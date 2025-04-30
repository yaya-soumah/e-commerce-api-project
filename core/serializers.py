from rest_framework import serializers
from users.models import User

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
        from rest_framework.authtoken.models import Token
        token, _ = Token.objects.get_or_create(user=obj)
        return f"Bearer {token}"


    