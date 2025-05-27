from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .serializers import SalesReportSerializer, \
ProductPopularitySerializer, \
    PaymentStatusSerializer, ProductCategoryReportSerializer
from django.utils import timezone
from datetime import timedelta, datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.dateparse import parse_date

import logging

logger = logging.getLogger(__name__)

class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    def parse_date(self, date_str):
        """Returns (datetime or None, was_supplied: bool, is_invalid: bool)"""
        if date_str is None:
            return None, False, False

        try:
            parsed = parse_date(date_str)            
        except ValueError:
            return None, True, True  # Provided but invalid
        
        if parsed:
            dt = datetime.combine(parsed, datetime.min.time())
            return timezone.make_aware(dt), True, False
        return None, True, True  # Provided but invalid

    def get_date_range(self, request):
        now = timezone.now()
        default_start = now - timedelta(days=30)
        default_end = now

        raw_start = request.query_params.get('start_date')
        raw_end = request.query_params.get('end_date')

        start_date, start_supplied, start_invalid = self.parse_date(raw_start)
        end_date, end_supplied, end_invalid = self.parse_date(raw_end)

        if not start_supplied:
            start_date = default_start

        if not end_supplied:
            end_date = default_end

        if start_invalid:
            return None, None, {'error': 'Invalid start_date format'}
        if end_invalid:
            return None, None, {'error': 'Invalid end_date format'}
        
        if start_date > end_date:
            return None, None, {'error': 'start_date cannot be after end_date.'}

        return start_date, end_date, None

    @action(detail=False, methods=['get'])
    def sales(self, request):
        start_date, end_date, error = self.get_date_range(request)
        if error:
            return Response({
                'status': 'error',
                'data': [],
                'message': error['error'],
                'errors': error,
                'meta': {}
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
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ]
    )
    @action(detail=False,methods=['get'], url_path='categories')
    def categories(self,request):
        start_date, end_date, error = self.get_date_range(request)
        
        if error:
            return Response({
                'status': 'error',
                'data': [],
                'message': error['error'],
                'errors': error,
                'meta': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ProductCategoryReportSerializer(data=[])
        data = serializer.get_queryset(
            start_date=start_date, end_date=end_date
        )

        return Response({
            'status': 'success',
            'data': data,
            'message': 'Category report retrieved successfully',
            'errors': None,
            'meta': {'start_date': str(start_date), 'end_date': str(end_date)}
        })

