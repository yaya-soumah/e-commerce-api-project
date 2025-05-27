from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from .models import Order, ShippingTracking
from .serializers import OrderSerializer, ChangeShippingAddressSerializer, UpdateTrackingSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create','update','partial_update','change_address']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(user=self.request.user)
    
    def perform_create(self,serializer):
        serializer.save(user=self.request.user)
    
    def perform_destroy(self, instance):
        instance.delete()
    
    @action(detail=True, methods=['patch'], serializer_class=ChangeShippingAddressSerializer)
    def change_address(self,request, pk=None):
        order = self.get_object()
        serializer = self.get_serializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data={
                "data":serializer.data,
                "message":"Shipping address updated successfully"
            }, status=status.HTTP_200_OK)
        return Response(data={
            "data":{},
            "message":"Failed to update shipping address"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser], serializer_class=UpdateTrackingSerializer)
    def update_tracking(self, request, pk=None):
        order = self.get_object()
        tracking, created = ShippingTracking.objects.get_or_create(order=order)
        serializer = UpdateTrackingSerializer(tracking,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={
                "data":serializer.data,
                "message":"Tracking updated successfully"
            }, status=status.HTTP_200_OK)
        return Response(data={
                "data":{},
                "message":"Failed to update Tracking"
            }, status=status.HTTP_400_BAD_REQUEST)
