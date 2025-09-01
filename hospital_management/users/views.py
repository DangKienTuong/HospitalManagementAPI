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

from .models import BenhNhan
from .serializers import BenhNhanSerializer, BenhNhanCreateSerializer
from authentication.permissions import IsAdminUser, IsPatientUser, IsOwnerOrReadOnly


@extend_schema_view(
    list=extend_schema(
        operation_id='patients_list',
        tags=['Patients'],
        summary='List patients',
        description='List all patients with filtering, searching and pagination',
        responses={
            200: OpenApiResponse(
                description='List of patients',
                response=BenhNhanSerializer(many=True)
            ),
            204: OpenApiResponse(
                description='No patients found',
                response={
                    'type': 'object',
                    'properties': {
                        'count': {'type': 'integer', 'example': 0},
                        'results': {'type': 'array', 'items': {}}
                    }
                }
            ),
            401: OpenApiResponse(
                description='Unauthorized - Authentication required',
                response={
                    'type': 'object',
                    'properties': {
                        'detail': {'type': 'string', 'example': 'Authentication credentials were not provided.'}
                    }
                }
            ),
            403: OpenApiResponse(
                description='Forbidden - Insufficient permissions',
                response={
                    'type': 'object',
                    'properties': {
                        'detail': {'type': 'string', 'example': 'You do not have permission to perform this action.'}
                    }
                }
            )
        }
    ),
    create=extend_schema(
        operation_id='patients_create',
        tags=['Patients'],
        summary='Create patient',
        description='Create a new patient record'
    ),
    retrieve=extend_schema(
        operation_id='patients_retrieve',
        tags=['Patients'],
        summary='Get patient details',
        description='Get detailed information about a specific patient',
        responses={
            200: OpenApiResponse(description='Successfully retrieved patient information'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            404: OpenApiResponse(
                description='Patient not found',
                examples={
                    'application/json': {
                        'error': 'Patient not found'
                    }
                }
            ),
            500: OpenApiResponse(
                description='Internal server error',
                examples={
                    'application/json': {
                        'error': 'Internal server error'
                    }
                }
            )
        }
    ),
    update=extend_schema(
        operation_id='patients_update',
        tags=['Patients'],
        summary='Update patient',
        description='Update patient information'
    ),
    partial_update=extend_schema(
        operation_id='patients_partial_update',
        tags=['Patients'],
        summary='Partially update patient',
        description='Partially update patient information'
    ),
    destroy=extend_schema(
        operation_id='patients_delete',
        tags=['Patients'],
        summary='Delete patient',
        description='Delete a patient record'
    ),
)
class BenhNhanViewSet(viewsets.ModelViewSet):
    queryset = BenhNhan.objects.all()
    serializer_class = BenhNhanSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['gioi_tinh']
    search_fields = ['ho_ten', 'so_dien_thoai', 'cmnd_cccd', 'so_bhyt']
    ordering_fields = ['ngay_sinh', 'ma_benh_nhan']
    ordering = ['-ma_benh_nhan']

    def handle_exception(self, exc):
        """Custom exception handling for patient operations"""
        if isinstance(exc, ValidationError):
            logger.error(f"Validation error in patients API: {str(exc)}")
            return Response(
                {'error': 'Invalid data provided', 'details': str(exc)},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif isinstance(exc, IntegrityError):
            logger.error(f"Database integrity error in patients API: {str(exc)}")
            return Response(
                {'error': 'Data integrity violation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().handle_exception(exc)

    def list(self, request, *args, **kwargs):
        """List patients with enhanced error handling"""
        try:
            queryset = self.filter_queryset(self.get_queryset())
            
            if not queryset.exists():
                logger.info("No patients found for the given filters")
                return Response(
                    {'count': 0, 'results': [], 'message': 'No patients found'},
                    status=status.HTTP_200_OK
                )
            
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(queryset, many=True)
            logger.info(f"Retrieved {len(serializer.data)} patients")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Unexpected error in patient list: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        """Create patient with enhanced validation"""
        try:
            if not request.data:
                return Response(
                    {'error': 'Request body is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                self.perform_create(serializer)
                logger.info(f"Created patient: {serializer.data.get('ma_benh_nhan')}")
                headers = self.get_success_headers(serializer.data)
                return Response(
                    serializer.data, 
                    status=status.HTTP_201_CREATED, 
                    headers=headers
                )
            else:
                logger.warning(f"Patient creation failed: {serializer.errors}")
                return Response(
                    {'error': 'Invalid data provided', 'details': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except IntegrityError as e:
            logger.error(f"Database integrity error creating patient: {str(e)}")
            return Response(
                {'error': 'Patient with this information already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error creating patient: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def retrieve(self, request, *args, **kwargs):
        """Retrieve patient with enhanced error handling"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"Retrieved patient: {instance.ma_benh_nhan}")
            return Response(serializer.data)
            
        except Http404:
            logger.warning(f"Patient not found with ID: {kwargs.get('pk')}")
            return Response(
                {'error': 'Patient not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error retrieving patient: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BenhNhanCreateSerializer
        return BenhNhanSerializer
    
    def get_queryset(self):
        user = self.request.user
        if user.vai_tro == 'Bệnh nhân':
            # Bệnh nhân chỉ xem được thông tin của mình
            return self.queryset.filter(ma_nguoi_dung=user)
        elif user.vai_tro in ['Bác sĩ', 'Nhân viên']:
            # Bác sĩ và nhân viên y tế xem được tất cả bệnh nhân
            return self.queryset
        elif user.vai_tro == 'Admin':
            # Admin xem được tất cả
            return self.queryset
        return self.queryset.none()
    
    @extend_schema(
        operation_id='patients_medical_history',
        tags=['Patients'],
        summary='Get patient medical history',
        description='Get medical history of a specific patient'
    )
    @action(detail=True, methods=['get'])
    def lich_su_kham(self, request, pk=None):
        """Lấy lịch sử khám bệnh của bệnh nhân"""
        try:
            benh_nhan = self.get_object()
            lich_hen = benh_nhan.lich_hen.select_related(
                'bac_si', 'co_so_y_te'
            ).order_by('-ngay_hen')
            
            if not lich_hen.exists():
                logger.info(f"No medical history found for patient: {benh_nhan.ma_benh_nhan}")
                return Response(
                    {'message': 'No medical history found', 'results': []},
                    status=status.HTTP_200_OK
                )
            
            # Import tại đây để tránh circular import
            from appointments.serializers import LichHenSerializer
            serializer = LichHenSerializer(lich_hen, many=True)
            logger.info(f"Retrieved {len(serializer.data)} medical history records for patient: {benh_nhan.ma_benh_nhan}")
            return Response(serializer.data)
            
        except BenhNhan.DoesNotExist:
            logger.warning(f"Patient not found for medical history request: {pk}")
            return Response(
                {'error': 'Patient not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error retrieving medical history: {str(e)}")
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        operation_id='patients_profile',
        tags=['Patients'],
        summary='Get current patient profile',
        description='Get profile information for the currently authenticated patient'
    )
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Lấy thông tin profile bệnh nhân hiện tại"""
        try:
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            benh_nhan = BenhNhan.objects.get(user=request.user)
            serializer = self.get_serializer(benh_nhan)
            return Response(serializer.data)
        except BenhNhan.DoesNotExist:
            return Response(
                {'error': 'Không tìm thấy thông tin bệnh nhân'}, 
                status=status.HTTP_404_NOT_FOUND
            )
