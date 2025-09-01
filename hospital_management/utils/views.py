from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.openapi import OpenApiTypes
from authentication.permissions import IsAdminUser

try:
    from .import_data import DataImporter
except ImportError:
    DataImporter = None

try:
    from .export_data import DataExporter  
except ImportError:
    DataExporter = None


@extend_schema_view(
    post=extend_schema(
        operation_id='utils_import_patients',
        tags=['Utils'],
        summary='Import patients data',
        description='Import patient data from Excel or CSV file',
        responses={200: {'type': 'object', 'properties': {'message': {'type': 'string'}, 'results': {'type': 'object'}}}}
    )
)
class ImportBenhNhanView(APIView):
    """API để nhập dữ liệu bệnh nhân từ file"""
    permission_classes = [IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):
        if DataImporter is None:
            return Response(
                {'error': 'Import functionality not available'}, 
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
            
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'Vui lòng chọn file để upload'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_type = 'csv' if file.name.endswith('.csv') else 'xlsx'
        
        try:
            results = DataImporter.import_benh_nhan(file, file_type)
            return Response({
                'message': 'Nhập dữ liệu hoàn tất',
                'results': results
            })
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Import error occurred'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    post=extend_schema(
        operation_id='utils_import_facilities',
        tags=['Utils'],
        summary='Import medical facilities data',
        description='Import medical facilities data from Excel or CSV file'
    )
)
class ImportCoSoYTeView(APIView):
    """API để nhập dữ liệu cơ sở y tế từ file"""
    permission_classes = [IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):
        if DataImporter is None:
            return Response(
                {'error': 'Import functionality not available'}, 
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
            
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'Vui lòng chọn file để upload'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_type = 'csv' if file.name.endswith('.csv') else 'xlsx'
        
        try:
            results = DataImporter.import_co_so_y_te(file, file_type)
            return Response({
                'message': 'Nhập dữ liệu hoàn tất',
                'results': results
            })
        except Exception as e:
            return Response(
                {'error': 'Import error occurred'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ImportBacSiView(APIView):
    """API để nhập dữ liệu bác sĩ từ file"""
    permission_classes = [IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'Vui lòng chọn file để upload'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_type = 'csv' if file.name.endswith('.csv') else 'xlsx'
        
        try:
            results = DataImporter.import_bac_si(file, file_type)
            return Response({
                'message': 'Nhập dữ liệu hoàn tất',
                'results': results
            })
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


class ImportDichVuView(APIView):
    """API để nhập dữ liệu dịch vụ từ file"""
    permission_classes = [IsAdminUser]
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response(
                {'error': 'Vui lòng chọn file để upload'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_type = 'csv' if file.name.endswith('.csv') else 'xlsx'
        
        try:
            results = DataImporter.import_dich_vu(file, file_type)
            return Response({
                'message': 'Nhập dữ liệu hoàn tất',
                'results': results
            })
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )


@extend_schema_view(
    get=extend_schema(
        operation_id='utils_export_patients',
        tags=['Utils'],
        summary='Export patients data',
        description='Export patient data to Excel or CSV file'
    )
)
class ExportBenhNhanView(APIView):
    """API để xuất dữ liệu bệnh nhân"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        if DataExporter is None:
            return Response(
                {'error': 'Export functionality not available'}, 
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
            
        file_format = request.GET.get('format', 'excel')  # excel hoặc csv
        
        try:
            if file_format.lower() == 'csv':
                response = DataExporter.export_benh_nhan_csv()
            else:
                response = DataExporter.export_benh_nhan_excel()
            
            return response
        except Exception as e:
            return Response(
                {'error': 'Export error occurred'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExportLichHenView(APIView):
    """API để xuất báo cáo lịch hẹn"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        file_format = request.GET.get('format', 'excel')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        try:
            if file_format.lower() == 'pdf':
                response = DataExporter.export_lich_hen_pdf(start_date, end_date)
            else:
                response = DataExporter.export_lich_hen_excel(start_date, end_date)
            
            return response
        except Exception as e:
            return Response(
                {'error': f'Lỗi khi xuất báo cáo: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExportThongKeView(APIView):
    """API để xuất báo cáo thống kê"""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        report_type = request.GET.get('type', 'doanh_thu')  # doanh_thu, lich_hen, benh_nhan
        file_format = request.GET.get('format', 'excel')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        try:
            if report_type == 'doanh_thu':
                response = DataExporter.export_bao_cao_doanh_thu(start_date, end_date, file_format)
            elif report_type == 'lich_hen':
                response = DataExporter.export_bao_cao_lich_hen(start_date, end_date, file_format)
            elif report_type == 'benh_nhan':
                response = DataExporter.export_bao_cao_benh_nhan(start_date, end_date, file_format)
            else:
                return Response(
                    {'error': 'Loại báo cáo không hợp lệ'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return response
        except Exception as e:
            return Response(
                {'error': f'Lỗi khi xuất báo cáo: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
