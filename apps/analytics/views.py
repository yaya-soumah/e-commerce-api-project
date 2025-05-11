from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .serializers import SalesReportSerializer, ProductPopularitySerializer, PaymentStatusSerializer
from django.utils import timezone
from datetime import timedelta

class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    def get_date_range(self, request):
        # Default end_date to today’s date
        default_end_date = timezone.now().date()
        end_date_str = request.query_params.get('end_date', str(default_end_date))
        
        # Parse end_date
        try:
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return None, None, {'error': 'Invalid end_date format. Use YYYY-MM-DD.'}

        # Default start_date to 30 days before end_date
        default_start_date = end_date - timedelta(days=30)
        start_date_str = request.query_params.get('start_date', str(default_start_date))
        
        # Parse start_date
        try:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            return None, None, {'error': 'Invalid start_date format. Use YYYY-MM-DD.'}

        # Validate date range
        if start_date > end_date:
            return None, None, {'error': 'start_date cannot be after end_date.'}

        return start_date, end_date, None

    @action(detail=False, methods=['get'])
    def sales(self, request):
        start_date, end_date, error = self.get_date_range(request)
        if error:
            return Response({
                'data': None,
                'message': "An error has occured."
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = SalesReportSerializer(data=[])
        queryset = serializer.get_queryset(start_date, end_date)
        data = [serializer.to_representation(item) for item in queryset]
        return Response({
            'status': 'success',
            'data': data,
            'message': 'Sales report generated successfully',
            'errors': None,
            'meta': {'start_date': str(start_date), 'end_date': str(end_date)}
        })

    @action(detail=False, methods=['get'])
    def products(self, request):
        start_date, end_date, error = self.get_date_range(request)
        if error:
            return Response({
                'status': 'error',
                'data': [],
                'message': error['error'],
                'errors': error,
                'meta': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductPopularitySerializer(data=[])
        queryset = serializer.get_queryset(start_date, end_date)
        data = [serializer.to_representation(item) for item in queryset]
        return Response({
            'status': 'success',
            'data': data,
            'message': 'Product popularity report generated successfully',
            'errors': None,
            'meta': {'start_date': str(start_date), 'end_date': str(end_date)}
        })

    @action(detail=False, methods=['get'])
    def payment_status(self, request):
        start_date, end_date, error = self.get_date_range(request)
        if error:
            return Response({
                'status': 'error',
                'data': [],
                'message': error['error'],
                'errors': error,
                'meta': {}
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = PaymentStatusSerializer(data=[])
        queryset = serializer.get_queryset(start_date, end_date)
        data = [serializer.to_representation(item) for item in queryset]
        return Response({
            'status': 'success',
            'data': data,
            'message': 'Payment status report generated successfully',
            'errors': None,
            'meta': {'start_date': str(start_date), 'end_date': str(end_date)}
        })