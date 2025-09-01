from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Sum, Count
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)
from .models import ThanhToan
from .serializers import (
    ThanhToanSerializer, ThanhToanCreateSerializer, ThanhToanUpdateStatusSerializer
)
from authentication.permissions import IsAdminUser, IsDoctorOrAdmin


class ThanhToanViewSet(viewsets.ModelViewSet):
    queryset = ThanhToan.objects.select_related(
        'ma_lich_hen__ma_benh_nhan', 'ma_lich_hen__ma_bac_si', 'ma_lich_hen__ma_dich_vu'
    ).all()
    serializer_class = ThanhToanSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['trang_thai', 'phuong_thuc', 'ma_lich_hen__ma_bac_si']
    search_fields = ['ma_lich_hen__ma_benh_nhan__ho_ten', 'ma_lich_hen__ma_bac_si__ho_ten', 'ma_thanh_toan']
    ordering_fields = ['thoi_gian_thanh_toan', 'so_tien']
    ordering = ['-thoi_gian_thanh_toan']

    def handle_exception(self, exc):
        """Custom exception handling for payment operations"""
        if isinstance(exc, ValidationError):
            logger.error(f"Validation error in payments API: {str(exc)}")
            return Response(
                {'error': 'Invalid data provided', 'details': str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, IntegrityError):
            logger.error(f"Database integrity error in payments API: {str(exc)}")
            return Response(
                {'error': 'Payment processing conflict or data integrity violation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)

    def list(self, request, *args, **kwargs):
        """List payments with enhanced error handling"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            if not queryset.exists():
                logger.info("No payments found for the given filters")
                return Response(
                    {'count': 0, 'results': [], 'message': 'No payments found'},
                    status=status.HTTP_200_OK
                )
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"Retrieved {len(serializer.data)} payments")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Unexpected error in payments list: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        """Create payment with enhanced validation"""
        try:
            if not request.data:
                return Response(
                    {'error': 'Request body is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                logger.info(f"Created payment: {serializer.data.get('ma_thanh_toan')}")
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data, 
                    status=status.HTTP_201_CREATED, 
                    headers=headers
                )
            else:
                logger.warning(f"Payment creation failed: {serializer.errors}")
                return Response(
                    {'error': 'Invalid data provided', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except IntegrityError as e:
            logger.error(f"Database integrity error creating payment: {str(e)}")
            return Response(
                {'error': 'Payment already exists or data conflict'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error creating payment: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """Retrieve payment with enhanced error handling"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"Retrieved payment: {instance.ma_thanh_toan}")
            return Response(serializer.data)
            
        except ThanhToan.DoesNotExist:
            logger.warning(f"Payment not found with ID: {kwargs.get('pk')}")
            return Response(
                {'error': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error retrieving payment: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsDoctorOrAdmin]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ThanhToanCreateSerializer
        elif self.action == 'update_status':
            return ThanhToanUpdateStatusSerializer
        return ThanhToanSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        if user.vai_tro == 'Bệnh nhân':
            # Bệnh nhân chỉ xem được thanh toán của mình
            from users.models import BenhNhan
            try:
                benh_nhan = BenhNhan.objects.get(ma_nguoi_dung=user)
                queryset = queryset.filter(ma_lich_hen__ma_benh_nhan=benh_nhan)
            except BenhNhan.DoesNotExist:
                queryset = queryset.none()
        elif user.vai_tro == 'Bác sĩ':
            # Bác sĩ xem được thanh toán của bệnh nhân mình khám
            from medical.models import BacSi
            try:
                bac_si = BacSi.objects.get(ma_nguoi_dung=user)
                queryset = queryset.filter(ma_lich_hen__ma_bac_si=bac_si)
            except BacSi.DoesNotExist:
                queryset = queryset.none()
        # Admin xem được tất cả
        
        return queryset
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Cập nhật trạng thái thanh toán"""
        thanh_toan = self.get_object()
        serializer = self.get_serializer(thanh_toan, data=request.data, partial=True)
        
        if serializer.is_valid():
            if serializer.validated_data.get('trang_thai') == 'Da thanh toan':
                serializer.save(thoi_gian_thanh_toan=timezone.now())
            else:
                serializer.save()
            return Response(ThanhToanSerializer(thanh_toan).data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Xử lý thanh toán"""
        thanh_toan = self.get_object()
        
        if thanh_toan.trang_thai != 'Chua thanh toan':
            return Response(
                {'error': 'Thanh toán đã được xử lý'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Giả lập xử lý thanh toán thành công
        thanh_toan.trang_thai = 'Da thanh toan'
        thanh_toan.thoi_gian_thanh_toan = timezone.now()
        thanh_toan.ma_giao_dich = request.data.get('ma_giao_dich', f"TXN_{int(timezone.now().timestamp())}")
        thanh_toan.save()
        
        serializer = self.get_serializer(thanh_toan)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Thống kê thanh toán"""
        if request.user.vai_tro != 'Quan tri vien':
            return Response(
                {'error': 'Chỉ admin mới có thể xem thống kê'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        stats = {
            'tong_so_thanh_toan': self.queryset.count(),
            'da_thanh_toan': self.queryset.filter(trang_thai='Da thanh toan').count(),
            'chua_thanh_toan': self.queryset.filter(trang_thai='Chua thanh toan').count(),
            'da_hoan_tien': self.queryset.filter(trang_thai='Da hoan tien').count(),
            'tong_doanh_thu': self.queryset.filter(
                trang_thai='Da thanh toan'
            ).aggregate(total=Sum('so_tien'))['total'] or 0,
            'theo_phuong_thuc': {}
        }
        
        # Thống kê theo phương thức thanh toán
        for choice in ThanhToan.PHUONG_THUC_CHOICES:
            method = choice[0]
            count = self.queryset.filter(
                phuong_thuc=method, trang_thai='Da thanh toan'
            ).count()
            stats['theo_phuong_thuc'][method] = count
        
        return Response(stats)
