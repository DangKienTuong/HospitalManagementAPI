from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from drf_spectacular.openapi import OpenApiParameter, OpenApiTypes
from django.http import Http404, HttpResponse
from django.conf import settings
from io import BytesIO
import os
import logging
from django.db import IntegrityError
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import datetime
from rest_framework.exceptions import ValidationError
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from authentication.permissions import IsDoctorOrAdmin
from .models import ThanhToan
from .serializers import (
    ThanhToanSerializer,
    ThanhToanCreateSerializer,
    ThanhToanUpdateStatusSerializer,
)

logger = logging.getLogger(__name__)

@extend_schema_view(
    list=extend_schema(
        operation_id='payments_list',
        tags=['Payments'],
        summary='List payments',
        description='Get list of payments',
        responses={
            200: OpenApiResponse(description='Successfully retrieved payments list'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
    create=extend_schema(
        operation_id='payments_create',
        tags=['Payments'],
        summary='Create payment',
        description='Create a new payment record',
        responses={
            201: OpenApiResponse(description='Payment created successfully'),
            400: OpenApiResponse(description='Bad request - Invalid data provided'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Patient access required'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
    retrieve=extend_schema(
        operation_id='payments_retrieve',
        tags=['Payments'],
        summary='Get payment details',
        description='Get detailed information about a payment',
        responses={
            200: OpenApiResponse(description='Successfully retrieved payment'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            404: OpenApiResponse(
                description='Payment not found with specified ma_thanh_toan',
                examples={
                    'application/json': {
                        'error': 'Payment with ma_thanh_toan "123" does not exist',
                        'error_code': 'PAYMENT_NOT_FOUND'
                    }
                }
            ),
            500: OpenApiResponse(
                description='Internal server error',
                examples={
                    'application/json': {
                        'error': 'Internal server error occurred while retrieving payment',
                        'error_code': 'INTERNAL_SERVER_ERROR'
                    }
                }
            )
        }
    ),
    update=extend_schema(
        operation_id='payments_update',
        tags=['Payments'],
        summary='Update payment',
        description='Update payment information',
        responses={
            200: OpenApiResponse(description='Payment updated successfully'),
            400: OpenApiResponse(description='Bad request - Invalid data provided'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Doctor or Admin access required'),
            404: OpenApiResponse(description='Payment not found'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
    partial_update=extend_schema(
        operation_id='payments_partial_update',
        tags=['Payments'],
        summary='Partially update payment',
        description='Partially update payment information',
        responses={
            200: OpenApiResponse(description='Payment updated successfully'),
            400: OpenApiResponse(description='Bad request - Invalid data provided'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Doctor or Admin access required'),
            404: OpenApiResponse(description='Payment not found'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
    destroy=extend_schema(
        operation_id='payments_delete',
        tags=['Payments'],
        summary='Delete payment',
        description='Delete a payment record',
        responses={
            204: OpenApiResponse(description='Payment deleted successfully'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Doctor or Admin access required'),
            404: OpenApiResponse(description='Payment not found'),
            500: OpenApiResponse(description='Internal server error')
        }
    ),
)
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
        ma_thanh_toan = kwargs.get('pk')
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"Retrieved payment: {instance.ma_thanh_toan}")
            return Response(serializer.data)
            
        except Http404:
            logger.warning(f"Payment not found with ma_thanh_toan: {ma_thanh_toan}")
            return Response(
                {
                    'error': f'Payment with ma_thanh_toan "{ma_thanh_toan}" does not exist',
                    'error_code': 'PAYMENT_NOT_FOUND'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error retrieving payment: {str(e)}")
            return Response(
                {
                    'error': 'Internal server error occurred while retrieving payment',
                    'error_code': 'INTERNAL_SERVER_ERROR'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['list', 'retrieve', 'export_invoice']:
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
    
    @extend_schema(
        operation_id='payments_update_status',
        tags=['Payments'],
        summary='Update payment status',
        description='Update the status of a payment',
        responses={
            200: OpenApiResponse(description='Payment status updated successfully'),
            400: OpenApiResponse(description='Bad request - Invalid status'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Admin access required'),
            404: OpenApiResponse(description='Payment not found'),
            500: OpenApiResponse(description='Internal server error')
        }
    )
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
    
    @extend_schema(
        operation_id='payments_process',
        tags=['Payments'],
        summary='Process payment',
        description='Process a payment and update status to completed',
        responses={
            200: OpenApiResponse(description='Payment processed successfully'),
            400: OpenApiResponse(description='Bad request - Payment already completed'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Admin or Doctor access required'),
            404: OpenApiResponse(description='Payment not found'),
            500: OpenApiResponse(description='Internal server error')
        }
    )
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

    @extend_schema(
        operation_id='payments_invoice',
        tags=['Payments'],
        summary='Export payment invoice',
        description='Xuất hóa đơn thanh toán dưới dạng PDF',
        responses={
            200: OpenApiResponse(description='PDF generated successfully'),
            404: OpenApiResponse(description='Payment not found'),
            500: OpenApiResponse(description='Internal server error'),
        },
    )
    @action(detail=True, methods=['get'], url_path='invoice')
    def export_invoice(self, request, pk=None):
        """Xuất hóa đơn thanh toán thành file PDF"""
        try:
            thanh_toan = self.get_object()
            
            # Validate required relationships exist
            if not hasattr(thanh_toan, 'ma_lich_hen') or not thanh_toan.ma_lich_hen:
                logger.error(f"Payment {pk} has no associated appointment")
                return Response(
                    {'error': 'Không tìm thấy thông tin lịch hẹn cho thanh toán này'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            lich_hen = thanh_toan.ma_lich_hen
            if not all([lich_hen.ma_benh_nhan, lich_hen.ma_bac_si, lich_hen.ma_dich_vu]):
                logger.error(f"Payment {pk} has incomplete appointment data")
                return Response(
                    {'error': 'Thông tin lịch hẹn không đầy đủ để tạo hóa đơn'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            buffer = BytesIO()
            
            # Font setup with better error handling - using NotoSans for Vietnamese support
            try:
                # Try NotoSans first (better Vietnamese support)
                noto_font_path = os.path.join(
                    settings.BASE_DIR, 'utils', 'fonts', 'NotoSans-Regular.ttf'
                )
                if os.path.exists(noto_font_path):
                    if 'NotoSans' not in pdfmetrics.getRegisteredFontNames():
                        pdfmetrics.registerFont(TTFont('NotoSans', noto_font_path))
                    font_name = 'NotoSans'
                else:
                    # Fallback to DejaVuSans
                    font_path = os.path.join(
                        settings.BASE_DIR, 'utils', 'fonts', 'DejaVuSans.ttf'
                    )
                    if os.path.exists(font_path):
                        if 'DejaVu' not in pdfmetrics.getRegisteredFontNames():
                            pdfmetrics.registerFont(TTFont('DejaVu', font_path))
                        font_name = 'DejaVu'
                    else:
                        logger.error(f"Font files not found")
                        font_name = 'Helvetica'
            except Exception as font_error:
                logger.warning(f"Font registration failed: {font_error}, using fallback font")
                font_name = 'Helvetica'

            doc = SimpleDocTemplate(buffer, pagesize=A4,
                                    rightMargin=30, leftMargin=30,
                                    topMargin=30, bottomMargin=30)

            styles = getSampleStyleSheet()
            styles['Normal'].fontName = font_name
            styles['Heading1'].fontName = font_name
            styles['Heading2'].fontName = font_name
            styles.add(
                ParagraphStyle(
                    name='TitleVN',
                    fontName=font_name,
                    fontSize=16,
                    alignment=1,
                    spaceAfter=20,
                )
            )

            elements = [
                Paragraph('BỆNH VIỆN ĐA KHOA XYZ', styles['Heading2']),
                Paragraph('HÓA ĐƠN THANH TOÁN', styles['TitleVN']),
                Spacer(1, 12),
            ]

            # Safe data extraction with error handling
            try:
                benh_nhan_name = getattr(lich_hen.ma_benh_nhan, 'ho_ten', 'N/A')
                bac_si_name = getattr(lich_hen.ma_bac_si, 'ho_ten', 'N/A')
                dich_vu_name = getattr(lich_hen.ma_dich_vu, 'ten_dich_vu', 'N/A')
                ngay_kham = lich_hen.ngay_kham.strftime('%d/%m/%Y') if lich_hen.ngay_kham else 'N/A'
                gio_kham = lich_hen.gio_kham.strftime('%H:%M') if lich_hen.gio_kham else 'N/A'
                thoi_gian_tt = (thanh_toan.thoi_gian_thanh_toan.strftime('%d/%m/%Y %H:%M') 
                               if thanh_toan.thoi_gian_thanh_toan else 'Chưa thanh toán')
                
                data = [
                    ['Mã thanh toán:', str(thanh_toan.ma_thanh_toan)],
                    ['Tên bệnh nhân:', benh_nhan_name],
                    ['Bác sĩ phụ trách:', bac_si_name],
                    ['Dịch vụ:', dich_vu_name],
                    ['Ngày khám:', ngay_kham],
                    ['Giờ khám:', gio_kham],
                    ['Phương thức thanh toán:', thanh_toan.phuong_thuc or 'N/A'],
                    ['Trạng thái:', thanh_toan.trang_thai or 'N/A'],
                    ['Số tiền:', f"{thanh_toan.so_tien:,.0f} VNĐ" if thanh_toan.so_tien else '0 VNĐ'],
                    ['Thời gian thanh toán:', thoi_gian_tt],
                ]
            except Exception as data_error:
                logger.error(f"Error extracting data for invoice {pk}: {data_error}")
                return Response(
                    {'error': 'Lỗi khi trích xuất dữ liệu để tạo hóa đơn'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            table = Table(data, colWidths=[160, 340])
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 0.25, colors.gray),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 0), (-1, -1), font_name),
                ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 24))
            elements.append(Paragraph('Xin cảm ơn quý khách!', styles['Normal']))

            doc.build(elements)

            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            filename = f"hoa_don_{thanh_toan.ma_thanh_toan}.pdf"
            response['Content-Disposition'] = (
                f'attachment; filename="{filename}"'
            )
            logger.info(f"Successfully generated invoice for payment {thanh_toan.ma_thanh_toan}")
            return response

        except Http404:
            logger.warning(f"Payment not found with ID: {pk}")
            return Response(
                {'error': f'Không tìm thấy thanh toán với ID {pk}'},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"Unexpected error generating invoice for payment {pk}: {str(e)}")
            return Response(
                {'error': 'Không thể tạo hóa đơn', 'details': str(e) if settings.DEBUG else 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @extend_schema(
        operation_id='payments_statistics',
        tags=['Payments'],
        summary='Get payment statistics',
        description='Get payment statistics (Admin only)',
        parameters=[
            OpenApiParameter(
                name='start_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter statistics from this date (YYYY-MM-DD)'
            ),
            OpenApiParameter(
                name='end_date',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Filter statistics up to this date (YYYY-MM-DD)'
            ),
        ],
        responses={
            200: OpenApiResponse(description='Successfully retrieved payment statistics'),
            401: OpenApiResponse(description='Unauthorized - Authentication required'),
            403: OpenApiResponse(description='Forbidden - Admin access required'),
            500: OpenApiResponse(description='Internal server error')
        }
    )
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Thống kê thanh toán"""
        if request.user.vai_tro != 'Admin':
            return Response(
                {'error': 'Chỉ admin mới có thể xem thống kê'},
                status=status.HTTP_403_FORBIDDEN
            )

        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
            end = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = self.queryset
        if start:
            queryset = queryset.filter(thoi_gian_thanh_toan__date__gte=start)
        if end:
            queryset = queryset.filter(thoi_gian_thanh_toan__date__lte=end)

        stats = {
            'tong_so_thanh_toan': queryset.count(),
            'da_thanh_toan': queryset.filter(trang_thai='Da thanh toan').count(),
            'chua_thanh_toan': queryset.filter(trang_thai='Chua thanh toan').count(),
            'da_hoan_tien': queryset.filter(trang_thai='Da hoan tien').count(),
            'tong_doanh_thu': queryset.filter(
                trang_thai='Da thanh toan'
            ).aggregate(total=Sum('so_tien'))['total'] or 0,
            'theo_phuong_thuc': {},
            'theo_dich_vu': {},
            'theo_thang': {},
        }

        for choice in ThanhToan.PHUONG_THUC_CHOICES:
            method = choice[0]
            count = queryset.filter(
                phuong_thuc=method, trang_thai='Da thanh toan'
            ).count()
            stats['theo_phuong_thuc'][method] = count

        service_stats = queryset.filter(trang_thai='Da thanh toan').values(
            'ma_lich_hen__ma_dich_vu'
        ).annotate(total=Sum('so_tien'))
        for item in service_stats:
            key = str(item['ma_lich_hen__ma_dich_vu'])
            stats['theo_dich_vu'][key] = float(item['total'])

        month_stats = queryset.filter(trang_thai='Da thanh toan').annotate(
            thang=TruncMonth('thoi_gian_thanh_toan')
        ).values('thang').annotate(total=Sum('so_tien')).order_by('thang')
        for item in month_stats:
            key = item['thang'].strftime('%Y-%m') if item['thang'] else None
            stats['theo_thang'][key] = float(item['total']) if key else 0

        return Response(stats)
