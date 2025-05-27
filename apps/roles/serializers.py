from rest_framework import serializers
from .models import Role
from apps.permissions.models import Permission
from apps.permissions.serializers import PermissionSerializer

class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        queryset=Permission.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Role
        fields = ['id','name','description','permissions']

    def to_representation(self, instance):
        # Include full permission details in response
        representation = super().to_representation(instance)
        representation['permissions'] = PermissionSerializer(
            instance.permissions.all(),
            many=True,
            context={'view_type':'list', 'depth':0}
        ).data
        return representation