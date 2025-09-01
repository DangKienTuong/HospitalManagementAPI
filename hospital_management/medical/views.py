from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from drf_spectacular.openapi import OpenApiParameter, OpenApiTypes
import logging

logger = logging.getLogger(__name__)

from .models import CoSoYTe, ChuyenKhoa, BacSi, DichVu
from .serializers import (
    CoSoYTeSerializer, ChuyenKhoaSerializer, BacSiSerializer, 
    BacSiCreateSerializer, DichVuSerializer
)
from authentication.permissions import IsAdminUser, IsDoctorOrAdmin


@extend_schema_view(
    list=extend_schema(
        operation_id='medical_facilities_list',
        tags=['Medical Facilities'],
        summary='List medical facilities',
        description='Get list of medical facilities'
    ),
    create=extend_schema(
        operation_id='medical_facilities_create',
        tags=['Medical Facilities'],
        summary='Create medical facility',
        description='Create a new medical facility'
    ),
    retrieve=extend_schema(
        operation_id='medical_facilities_retrieve',
        tags=['Medical Facilities'],
        summary='Get medical facility details',
        description='Get detailed information about a medical facility'
    ),
    update=extend_schema(
        operation_id='medical_facilities_update',
        tags=['Medical Facilities'],
        summary='Update medical facility',
        description='Update medical facility information'
    ),
    destroy=extend_schema(
        operation_id='medical_facilities_delete',
        tags=['Medical Facilities'],
        summary='Delete medical facility',
        description='Delete a medical facility'
    ),
)
class CoSoYTeViewSet(viewsets.ModelViewSet):
    queryset = CoSoYTe.objects.all()
    serializer_class = CoSoYTeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['loai_hinh']
    search_fields = ['ten_co_so', 'dia_chi']
    ordering_fields = ['ten_co_so']
    ordering = ['ten_co_so']

    def handle_exception(self, exc):
        """Custom exception handling for medical facility operations"""
        if isinstance(exc, ValidationError):
            logger.error(f"Validation error in medical facilities API: {str(exc)}")
            return Response(
                {'error': 'Invalid data provided', 'details': str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, IntegrityError):
            logger.error(f"Database integrity error in medical facilities API: {str(exc)}")
            return Response(
                {'error': 'Data integrity violation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)

    def list(self, request, *args, **kwargs):
        """List medical facilities with enhanced error handling"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            if not queryset.exists():
                logger.info("No medical facilities found for the given filters")
                return Response(
                    {'count': 0, 'results': [], 'message': 'No medical facilities found'},
                    status=status.HTTP_200_OK
                )
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"Retrieved {len(serializer.data)} medical facilities")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Unexpected error in medical facilities list: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """Retrieve medical facility with enhanced error handling"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"Retrieved medical facility: {instance.ten}")
            return Response(serializer.data)
            
        except CoSoYTe.DoesNotExist:
            logger.warning(f"Medical facility not found with ID: {kwargs.get('pk')}")
            return Response(
                {'error': 'Medical facility not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error retrieving medical facility: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def chuyen_khoa(self, request, pk=None):
        """Lấy danh sách chuyên khoa của cơ sở y tế"""
        co_so = self.get_object()
        chuyen_khoa = co_so.chuyen_khoa.all()
        serializer = ChuyenKhoaSerializer(chuyen_khoa, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def bac_si(self, request, pk=None):
        """Lấy danh sách bác sĩ của cơ sở y tế"""
        co_so = self.get_object()
        bac_si = co_so.bac_si.select_related('ma_nguoi_dung', 'ma_chuyen_khoa').all()
        serializer = BacSiSerializer(bac_si, many=True)
        return Response(serializer.data)


class ChuyenKhoaViewSet(viewsets.ModelViewSet):
    queryset = ChuyenKhoa.objects.select_related('ma_co_so').prefetch_related('bac_si', 'dich_vu').all()
    serializer_class = ChuyenKhoaSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['ma_co_so']
    search_fields = ['ten_chuyen_khoa', 'mo_ta']
    ordering_fields = ['ten_chuyen_khoa', 'ma_co_so__ten_co_so']
    ordering = ['ten_chuyen_khoa']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def bac_si(self, request, pk=None):
        """Lấy danh sách bác sĩ của chuyên khoa"""
        chuyen_khoa = self.get_object()
        bac_si = chuyen_khoa.bac_si.select_related('ma_nguoi_dung').all()
        serializer = BacSiSerializer(bac_si, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def dich_vu(self, request, pk=None):
        """Lấy danh sách dịch vụ của chuyên khoa"""
        chuyen_khoa = self.get_object()
        dich_vu = chuyen_khoa.dich_vu.all()
        serializer = DichVuSerializer(dich_vu, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        operation_id='doctors_list',
        tags=['Doctors'],
        summary='List doctors',
        description='Get list of doctors with filtering capabilities'
    ),
    create=extend_schema(
        operation_id='doctors_create',
        tags=['Doctors'],
        summary='Create doctor',
        description='Create a new doctor profile'
    ),
    retrieve=extend_schema(
        operation_id='doctors_retrieve',
        tags=['Doctors'],
        summary='Get doctor details',
        description='Get detailed information about a doctor'
    ),
    update=extend_schema(
        operation_id='doctors_update',
        tags=['Doctors'],
        summary='Update doctor',
        description='Update doctor information'
    ),
    destroy=extend_schema(
        operation_id='doctors_delete',
        tags=['Doctors'],
        summary='Delete doctor',
        description='Delete a doctor profile'
    ),
)
class BacSiViewSet(viewsets.ModelViewSet):
    queryset = BacSi.objects.select_related(
        'ma_nguoi_dung', 'ma_co_so', 'ma_chuyen_khoa'
    ).prefetch_related('lich_hen').all()
    serializer_class = BacSiSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['ma_co_so', 'ma_chuyen_khoa', 'gioi_tinh', 'hoc_vi']
    search_fields = ['ho_ten', 'gioi_thieu', 'ma_nguoi_dung__so_dien_thoai']
    ordering_fields = ['ho_ten', 'kinh_nghiem', 'hoc_vi']
    ordering = ['ho_ten']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsDoctorOrAdmin]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BacSiCreateSerializer
        return BacSiSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated and user.vai_tro == 'Bác sĩ':
            # Bác sĩ chỉ xem được thông tin của mình và bác sĩ khác (cho mục đích tham khảo)
            return self.queryset
        return self.queryset

    def handle_exception(self, exc):
        """Custom exception handling for doctor operations"""
        if isinstance(exc, ValidationError):
            logger.error(f"Validation error in doctors API: {str(exc)}")
            return Response(
                {'error': 'Invalid data provided', 'details': str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, IntegrityError):
            logger.error(f"Database integrity error in doctors API: {str(exc)}")
            return Response(
                {'error': 'Data integrity violation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)

    def list(self, request, *args, **kwargs):
        """List doctors with enhanced error handling"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            if not queryset.exists():
                logger.info("No doctors found for the given filters")
                return Response(
                    {'count': 0, 'results': [], 'message': 'No doctors found'},
                    status=status.HTTP_200_OK
                )
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"Retrieved {len(serializer.data)} doctors")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Unexpected error in doctors list: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """Retrieve doctor with enhanced error handling"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"Retrieved doctor: {instance.ma_bac_si}")
            return Response(serializer.data)
            
        except BacSi.DoesNotExist:
            logger.warning(f"Doctor not found with ID: {kwargs.get('pk')}")
            return Response(
                {'error': 'Doctor not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error retrieving doctor: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def lich_lam_viec(self, request, pk=None):
        """Lấy lịch làm việc của bác sĩ"""
        bac_si = self.get_object()
        lich_lam_viec = bac_si.lich_lam_viec.order_by('ngay_lam_viec', 'gio_bat_dau')
        
        # Import tại đây để tránh circular import
        from appointments.serializers import LichLamViecSerializer
        serializer = LichLamViecSerializer(lich_lam_viec, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Lấy thông tin profile bác sĩ hiện tại"""
        if request.user.vai_tro != 'Bác sĩ':
            return Response(
                {'error': 'Chỉ bác sĩ mới có thể truy cập endpoint này'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            bac_si = BacSi.objects.get(ma_nguoi_dung=request.user)
            serializer = self.get_serializer(bac_si)
            return Response(serializer.data)
        except BacSi.DoesNotExist:
            return Response(
                {'error': 'Không tìm thấy thông tin bác sĩ'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class DichVuViewSet(viewsets.ModelViewSet):
    queryset = DichVu.objects.select_related('ma_co_so', 'ma_chuyen_khoa').all()
    serializer_class = DichVuSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['ma_co_so', 'ma_chuyen_khoa', 'loai_dich_vu']
    search_fields = ['ten_dich_vu', 'mo_ta']
    ordering_fields = ['ten_dich_vu', 'gia_tien', 'thoi_gian_kham']
    ordering = ['ten_dich_vu']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def tu_van_tu_xa(self, request):
        """Lấy danh sách dịch vụ tư vấn từ xa"""
        dich_vu = self.queryset.filter(loai_dich_vu='Tu van tu xa')
        serializer = self.get_serializer(dich_vu, many=True)
        return Response(serializer.data)
