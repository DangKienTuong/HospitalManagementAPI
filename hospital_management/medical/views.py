from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import Http404
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
        description='Get list of medical facilities',
        responses={
            200: OpenApiResponse(description='Successfully retrieved medical facilities list'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
    create=extend_schema(
        operation_id='medical_facilities_create',
        tags=['Medical Facilities'],
        summary='Create medical facility',
        description='Create a new medical facility',
        responses={
            201: OpenApiResponse(description='Medical facility created successfully'),
            400: OpenApiResponse(description='Bad request - Invalid data provided'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Admin access required'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
    retrieve=extend_schema(
        operation_id='medical_facilities_retrieve',
        tags=['Medical Facilities'],
        summary='Get medical facility details',
        description='Get detailed information about a medical facility',
        responses={
            200: OpenApiResponse(description='Successfully retrieved medical facility information'),
            404: OpenApiResponse(
                description='Medical facility not found with specified ma_co_so',
                examples={
                    'application/json': {
                        'error': 'Medical facility with ma_co_so "123" does not exist',
                        'error_code': 'FACILITY_NOT_FOUND'
                    }
                }
            ),
            500: OpenApiResponse(
                description='Internal server error',
                examples={
                    'application/json': {
                        'error': 'Internal server error occurred while retrieving medical facility',
                        'error_code': 'INTERNAL_SERVER_ERROR'
                    }
                }
            )
        }
    ),
    update=extend_schema(
        operation_id='medical_facilities_update',
        tags=['Medical Facilities'],
        summary='Update medical facility',
        description='Update medical facility information',
        responses={
            200: OpenApiResponse(description='Medical facility updated successfully'),
            400: OpenApiResponse(description='Bad request - Invalid data provided'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Admin access required'),
            404: OpenApiResponse(description='Medical facility not found'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
    destroy=extend_schema(
        operation_id='medical_facilities_delete',
        tags=['Medical Facilities'],
        summary='Delete medical facility',
        description='Delete a medical facility',
        responses={
            204: OpenApiResponse(description='Medical facility deleted successfully'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Admin access required'),
            404: OpenApiResponse(description='Medical facility not found'),
            500: OpenApiResponse(description='Internal server error')
        }
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
        ma_co_so = kwargs.get('pk')
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"Retrieved medical facility: {instance.ten}")
            return Response(serializer.data)
            
        except Http404:
            logger.warning(f"Medical facility not found with ma_co_so: {ma_co_so}")
            return Response(
                {
                    'error': f'Medical facility with ma_co_so "{ma_co_so}" does not exist',
                    'error_code': 'FACILITY_NOT_FOUND'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error retrieving medical facility: {str(e)}")
            return Response(
                {
                    'error': 'Internal server error occurred while retrieving medical facility',
                    'error_code': 'INTERNAL_SERVER_ERROR'
                },
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


@extend_schema_view(
    list=extend_schema(
        operation_id='specialties_list',
        tags=['Specialties'],
        summary='List specialties',
        description='Get list of medical specialties',
        responses={
            200: OpenApiResponse(description='Successfully retrieved specialties list'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
    create=extend_schema(
        operation_id='specialties_create',
        tags=['Specialties'],
        summary='Create specialty',
        description='Create a new medical specialty',
        responses={
            201: OpenApiResponse(description='Specialty created successfully'),
            400: OpenApiResponse(description='Bad request - Invalid data provided'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Admin access required'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
    retrieve=extend_schema(
        operation_id='specialties_retrieve',
        tags=['Specialties'],
        summary='Get specialty details',
        description='Get detailed information about a specialty',
        responses={
            200: OpenApiResponse(description='Successfully retrieved specialty information'),
            404: OpenApiResponse(
                description='Specialty not found with specified ma_chuyen_khoa',
                examples={
                    'application/json': {
                        'error': 'Specialty with ma_chuyen_khoa "123" does not exist',
                        'error_code': 'SPECIALTY_NOT_FOUND'
                    }
                }
            ),
            500: OpenApiResponse(
                description='Internal server error',
                examples={
                    'application/json': {
                        'error': 'Internal server error occurred while retrieving specialty',
                        'error_code': 'INTERNAL_SERVER_ERROR'
                    }
                }
            )
        }
    ),
    update=extend_schema(
        operation_id='specialties_update',
        tags=['Specialties'],
        summary='Update specialty',
        description='Update specialty information',
        responses={
            200: OpenApiResponse(description='Specialty updated successfully'),
            400: OpenApiResponse(description='Bad request - Invalid data provided'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Admin access required'),
            404: OpenApiResponse(description='Specialty not found'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
    destroy=extend_schema(
        operation_id='specialties_delete',
        tags=['Specialties'],
        summary='Delete specialty',
        description='Delete a specialty',
        responses={
            204: OpenApiResponse(description='Specialty deleted successfully'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Admin access required'),
            404: OpenApiResponse(description='Specialty not found'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
)
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
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve specialty with enhanced error handling"""
        ma_chuyen_khoa = kwargs.get('pk')
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"Retrieved specialty: {instance.ten_chuyen_khoa}")
            return Response(serializer.data)
            
        except Http404:
            logger.warning(f"Specialty not found with ma_chuyen_khoa: {ma_chuyen_khoa}")
            return Response(
                {
                    'error': f'Specialty with ma_chuyen_khoa "{ma_chuyen_khoa}" does not exist',
                    'error_code': 'SPECIALTY_NOT_FOUND'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error retrieving specialty: {str(e)}")
            return Response(
                {
                    'error': 'Internal server error occurred while retrieving specialty',
                    'error_code': 'INTERNAL_SERVER_ERROR'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
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
        description='Get list of doctors with filtering capabilities',
        responses={
            200: OpenApiResponse(description='Successfully retrieved doctors list'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
    create=extend_schema(
        operation_id='doctors_create',
        tags=['Doctors'],
        summary='Create doctor',
        description='Create a new doctor profile',
        responses={
            201: OpenApiResponse(description='Doctor profile created successfully'),
            400: OpenApiResponse(description='Bad request - Invalid data provided or data integrity violation'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Admin access required'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
    retrieve=extend_schema(
        operation_id='doctors_retrieve',
        tags=['Doctors'],
        summary='Get doctor details',
        description='Get detailed information about a doctor',
        responses={
            200: OpenApiResponse(description='Successfully retrieved doctor information'),
            404: OpenApiResponse(
                description='Doctor not found with specified ma_bac_si',
                examples={
                    'application/json': {
                        'error': 'Doctor with ma_bac_si "9" does not exist',
                        'error_code': 'DOCTOR_NOT_FOUND'
                    }
                }
            ),
            500: OpenApiResponse(
                description='Internal server error',
                examples={
                    'application/json': {
                        'error': 'Internal server error occurred while retrieving doctor',
                        'error_code': 'INTERNAL_SERVER_ERROR'
                    }
                }
            )
        }
    ),
    update=extend_schema(
        operation_id='doctors_update',
        tags=['Doctors'],
        summary='Update doctor',
        description='Update doctor information',
        responses={
            200: OpenApiResponse(description='Doctor information updated successfully'),
            400: OpenApiResponse(description='Bad request - Invalid data provided'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Doctor or Admin access required'),
            404: OpenApiResponse(description='Doctor not found'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
    destroy=extend_schema(
        operation_id='doctors_delete',
        tags=['Doctors'],
        summary='Delete doctor',
        description='Delete a doctor profile',
        responses={
            204: OpenApiResponse(description='Doctor profile deleted successfully'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Doctor or Admin access required'),
            404: OpenApiResponse(description='Doctor not found'),
            500: OpenApiResponse(description='Internal server error')
        }
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
        ma_bac_si = kwargs.get('pk')
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"Retrieved doctor: {instance.ma_bac_si}")
            return Response(serializer.data)
            
        except Http404:
            logger.warning(f"Doctor not found with ma_bac_si: {ma_bac_si}")
            return Response(
                {
                    'error': f'Doctor with ma_bac_si "{ma_bac_si}" does not exist',
                    'error_code': 'DOCTOR_NOT_FOUND'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error retrieving doctor: {str(e)}")
            return Response(
                {
                    'error': 'Internal server error occurred while retrieving doctor',
                    'error_code': 'INTERNAL_SERVER_ERROR'
                },
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


@extend_schema_view(
    list=extend_schema(
        operation_id='services_list',
        tags=['Medical Services'],
        summary='List medical services',
        description='Get list of medical services',
        responses={
            200: OpenApiResponse(description='Successfully retrieved services list'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
    create=extend_schema(
        operation_id='services_create',
        tags=['Medical Services'],
        summary='Create service',
        description='Create a new medical service',
        responses={
            201: OpenApiResponse(description='Service created successfully'),
            400: OpenApiResponse(description='Bad request - Invalid data provided'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Admin access required'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
    retrieve=extend_schema(
        operation_id='services_retrieve',
        tags=['Medical Services'],
        summary='Get service details',
        description='Get detailed information about a medical service',
        responses={
            200: OpenApiResponse(description='Successfully retrieved service information'),
            404: OpenApiResponse(
                description='Service not found with specified ma_dich_vu',
                examples={
                    'application/json': {
                        'error': 'Service with ma_dich_vu "123" does not exist',
                        'error_code': 'SERVICE_NOT_FOUND'
                    }
                }
            ),
            500: OpenApiResponse(
                description='Internal server error',
                examples={
                    'application/json': {
                        'error': 'Internal server error occurred while retrieving service',
                        'error_code': 'INTERNAL_SERVER_ERROR'
                    }
                }
            )
        }
    ),
    update=extend_schema(
        operation_id='services_update',
        tags=['Medical Services'],
        summary='Update service',
        description='Update service information',
        responses={
            200: OpenApiResponse(description='Service updated successfully'),
            400: OpenApiResponse(description='Bad request - Invalid data provided'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Admin access required'),
            404: OpenApiResponse(description='Service not found'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
    destroy=extend_schema(
        operation_id='services_delete',
        tags=['Medical Services'],
        summary='Delete service',
        description='Delete a service',
        responses={
            204: OpenApiResponse(description='Service deleted successfully'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Admin access required'),
            404: OpenApiResponse(description='Service not found'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
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
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve service with enhanced error handling"""
        ma_dich_vu = kwargs.get('pk')
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"Retrieved service: {instance.ten_dich_vu}")
            return Response(serializer.data)
            
        except Http404:
            logger.warning(f"Service not found with ma_dich_vu: {ma_dich_vu}")
            return Response(
                {
                    'error': f'Service with ma_dich_vu "{ma_dich_vu}" does not exist',
                    'error_code': 'SERVICE_NOT_FOUND'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error retrieving service: {str(e)}")
            return Response(
                {
                    'error': 'Internal server error occurred while retrieving service',
                    'error_code': 'INTERNAL_SERVER_ERROR'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def tu_van_tu_xa(self, request):
        """Lấy danh sách dịch vụ tư vấn từ xa"""
        dich_vu = self.queryset.filter(loai_dich_vu='Tu van tu xa')
        serializer = self.get_serializer(dich_vu, many=True)
        return Response(serializer.data)
