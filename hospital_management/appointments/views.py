from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db import models
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
from .models import LichLamViec, LichHen, PhienTuVanTuXa
from .serializers import (
    LichLamViecSerializer, LichHenSerializer, LichHenCreateSerializer,
    PhienTuVanTuXaSerializer
)
from authentication.permissions import IsAdminUser, IsDoctorUser, IsPatientUser, IsDoctorOrAdmin


class LichLamViecViewSet(viewsets.ModelViewSet):
    queryset = LichLamViec.objects.select_related(
        'ma_bac_si__ma_nguoi_dung', 'ma_bac_si__ma_chuyen_khoa'
    ).all()
    serializer_class = LichLamViecSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['ma_bac_si', 'ngay_lam_viec']
    search_fields = ['ma_bac_si__ho_ten', 'ma_bac_si__ma_chuyen_khoa__ten_chuyen_khoa']
    ordering_fields = ['ngay_lam_viec', 'gio_bat_dau']
    ordering = ['ngay_lam_viec', 'gio_bat_dau']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'available']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def handle_exception(self, exc):
        """Custom exception handling for schedule operations"""
        if isinstance(exc, ValidationError):
            logger.error(f"Validation error in schedules API: {str(exc)}")
            return Response(
                {'error': 'Invalid data provided', 'details': str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, IntegrityError):
            logger.error(f"Database integrity error in schedules API: {str(exc)}")
            return Response(
                {'error': 'Schedule conflict or data integrity violation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)

    def list(self, request, *args, **kwargs):
        """List schedules with enhanced error handling"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            if not queryset.exists():
                logger.info("No schedules found for the given filters")
                return Response(
                    {'count': 0, 'results': [], 'message': 'No schedules found'},
                    status=status.HTTP_200_OK
                )
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"Retrieved {len(serializer.data)} schedules")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Unexpected error in schedules list: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    

    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        # Lọc theo bác sĩ nếu user là bác sĩ
        if user.is_authenticated and user.vai_tro == 'Bác sĩ':
            try:
                from medical.models import BacSi
                bac_si = BacSi.objects.get(ma_nguoi_dung=user)
                queryset = queryset.filter(ma_bac_si=bac_si)
            except BacSi.DoesNotExist:
                queryset = queryset.none()
        
        # Chỉ hiển thị lịch làm việc từ hôm nay trở đi (cho người dùng thường)
        if not user.is_authenticated or user.vai_tro not in ['Admin', 'Bác sĩ']:
            queryset = queryset.filter(ngay_lam_viec__gte=timezone.now().date())
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Lấy danh sách lịch làm việc còn chỗ trống"""
        queryset = self.get_queryset().filter(
            ngay_lam_viec__gte=timezone.now().date(),
            so_luong_da_dat__lt=models.F('so_luong_kham')
        )
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class LichHenViewSet(viewsets.ModelViewSet):
    queryset = LichHen.objects.select_related(
        'ma_benh_nhan', 'ma_bac_si', 'ma_dich_vu', 'ma_lich'
    ).all()
    serializer_class = LichHenSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['ma_bac_si', 'ma_benh_nhan', 'trang_thai', 'ngay_kham']
    search_fields = ['ma_benh_nhan__ho_ten', 'ma_bac_si__ho_ten']
    ordering_fields = ['ngay_kham', 'gio_kham']
    ordering = ['-ngay_kham']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def handle_exception(self, exc):
        """Custom exception handling for appointment operations"""
        if isinstance(exc, ValidationError):
            logger.error(f"Validation error in appointments API: {str(exc)}")
            return Response(
                {'error': 'Invalid data provided', 'details': str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, IntegrityError):
            logger.error(f"Database integrity error in appointments API: {str(exc)}")
            return Response(
                {'error': 'Appointment conflict or data integrity violation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)

    def list(self, request, *args, **kwargs):
        """List appointments with enhanced error handling"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            if not queryset.exists():
                logger.info("No appointments found for the given filters")
                return Response(
                    {'count': 0, 'results': [], 'message': 'No appointments found'},
                    status=status.HTTP_200_OK
                )
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"Retrieved {len(serializer.data)} appointments")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Unexpected error in appointments list: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        """Create appointment with enhanced validation"""
        try:
            if not request.data:
                return Response(
                    {'error': 'Request body is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                logger.info(f"Created appointment: {serializer.data.get('ma_lich_hen')}")
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data, 
                    status=status.HTTP_201_CREATED, 
                    headers=headers
                )
            else:
                logger.warning(f"Appointment creation failed: {serializer.errors}")
                return Response(
                    {'error': 'Invalid data provided', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except IntegrityError as e:
            logger.error(f"Database integrity error creating appointment: {str(e)}")
            return Response(
                {'error': 'Appointment conflict - time slot may already be booked'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error creating appointment: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """Retrieve appointment with enhanced error handling"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"Retrieved appointment: {instance.ma_lich_hen}")
            return Response(serializer.data)
            
        except LichHen.DoesNotExist:
            logger.warning(f"Appointment not found with ID: {kwargs.get('pk')}")
            return Response(
                {'error': 'Appointment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error retrieving appointment: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsPatientUser]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsDoctorOrAdmin]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return LichHenCreateSerializer
        return LichHenSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        if user.vai_tro == 'Bệnh nhân':
            # Bệnh nhân chỉ xem được lịch hẹn của mình
            from users.models import BenhNhan
            try:
                benh_nhan = BenhNhan.objects.get(ma_nguoi_dung=user)
                queryset = queryset.filter(ma_benh_nhan=benh_nhan)
            except BenhNhan.DoesNotExist:
                queryset = queryset.none()
        elif user.vai_tro == 'Bác sĩ':
            # Bác sĩ xem được lịch hẹn của mình
            from medical.models import BacSi
            try:
                bac_si = BacSi.objects.get(ma_nguoi_dung=user)
                queryset = queryset.filter(ma_bac_si=bac_si)
            except BacSi.DoesNotExist:
                queryset = queryset.none()
        # Admin xem được tất cả
        
        return queryset
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Cập nhật trạng thái lịch hẹn"""
        lich_hen = self.get_object()
        new_status = request.data.get('trang_thai')
        
        if new_status not in dict(LichHen.TRANG_THAI_CHOICES):
            return Response(
                {'error': 'Trạng thái không hợp lệ'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Chỉ bác sĩ hoặc admin mới có thể cập nhật trạng thái
        if request.user.vai_tro not in ['Bác sĩ', 'Admin']:
            return Response(
                {'error': 'Không có quyền cập nhật trạng thái'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        lich_hen.trang_thai = new_status
        lich_hen.save()
        
        serializer = self.get_serializer(lich_hen)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Hủy lịch hẹn"""
        lich_hen = self.get_object()
        
        if lich_hen.trang_thai == 'Da huy':
            return Response(
                {'error': 'Lịch hẹn đã được hủy trước đó'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Chỉ cho phép hủy nếu còn ít nhất 1 giờ
        now = timezone.now()
        appointment_datetime = timezone.make_aware(
            datetime.combine(lich_hen.ngay_kham, lich_hen.gio_kham)
        )
        
        if appointment_datetime - now < timedelta(hours=1):
            return Response(
                {'error': 'Chỉ có thể hủy lịch hẹn trước ít nhất 1 giờ'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lich_hen.trang_thai = 'Da huy'
        lich_hen.save()
        
        # Giảm số lượng đã đặt trong lịch làm việc
        lich_lam_viec = lich_hen.ma_lich
        lich_lam_viec.so_luong_da_dat = max(0, lich_lam_viec.so_luong_da_dat - 1)
        lich_lam_viec.save()
        
        serializer = self.get_serializer(lich_hen)
        return Response(serializer.data)


class PhienTuVanTuXaViewSet(viewsets.ModelViewSet):
    queryset = PhienTuVanTuXa.objects.select_related(
        'ma_lich_hen__ma_benh_nhan', 'ma_lich_hen__ma_bac_si'
    ).all()
    serializer_class = PhienTuVanTuXaSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['trang_thai', 'ma_lich_hen__ma_bac_si']
    search_fields = ['ma_lich_hen__ma_benh_nhan__ho_ten', 'ma_lich_hen__ma_bac_si__ho_ten']
    ordering_fields = ['thoi_gian_bat_dau', 'ma_lich_hen__ngay_kham']
    ordering = ['-thoi_gian_bat_dau']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsDoctorOrAdmin]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset
        
        if user.vai_tro == 'Bệnh nhân':
            # Bệnh nhân chỉ xem được phiên tư vấn của mình
            from users.models import BenhNhan
            try:
                benh_nhan = BenhNhan.objects.get(ma_nguoi_dung=user)
                queryset = queryset.filter(ma_lich_hen__ma_benh_nhan=benh_nhan)
            except BenhNhan.DoesNotExist:
                queryset = queryset.none()
        elif user.vai_tro == 'Bác sĩ':
            # Bác sĩ xem được phiên tư vấn của mình
            from medical.models import BacSi
            try:
                bac_si = BacSi.objects.get(ma_nguoi_dung=user)
                queryset = queryset.filter(ma_lich_hen__ma_bac_si=bac_si)
            except BacSi.DoesNotExist:
                queryset = queryset.none()
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def start_session(self, request, pk=None):
        """Bắt đầu phiên tư vấn"""
        phien = self.get_object()
        
        if phien.trang_thai != 'Chua bat dau':
            return Response(
                {'error': 'Phiên tư vấn đã bắt đầu hoặc kết thúc'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        phien.trang_thai = 'Dang dien ra'
        phien.thoi_gian_bat_dau = timezone.now()
        phien.ma_cuoc_goi = f"CALL_{phien.ma_phien}_{int(timezone.now().timestamp())}"
        phien.save()
        
        serializer = self.get_serializer(phien)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def end_session(self, request, pk=None):
        """Kết thúc phiên tư vấn"""
        phien = self.get_object()
        
        if phien.trang_thai != 'Dang dien ra':
            return Response(
                {'error': 'Phiên tư vấn chưa bắt đầu hoặc đã kết thúc'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        phien.trang_thai = 'Da ket thuc'
        phien.thoi_gian_ket_thuc = timezone.now()
        phien.ghi_chu_bac_si = request.data.get('ghi_chu_bac_si', phien.ghi_chu_bac_si)
        phien.save()
        
        # Cập nhật trạng thái lịch hẹn
        phien.ma_lich_hen.trang_thai = 'Hoan thanh'
        phien.ma_lich_hen.save()
        
        serializer = self.get_serializer(phien)
        return Response(serializer.data)
