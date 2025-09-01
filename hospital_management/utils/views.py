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
            
        file_format = request.GET.get('format', 'excel')  # Default to Excel for Vietnamese compatibility
        
        try:
            if file_format.lower() == 'csv':
                response = DataExporter.export_benh_nhan_csv()
            elif file_format.lower() == 'excel':
                response = DataExporter.export_benh_nhan_excel()
            else:
                # Default to Excel for best Vietnamese character support
                response = DataExporter.export_benh_nhan_excel()
            
            return response
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Export error: {error_details}")
            return Response(
                {'error': f'Export error occurred: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@extend_schema_view(
    get=extend_schema(
        operation_id='utils_export_appointments',
        tags=['Utils'],
        summary='Export appointments data',
        description='Export appointment data to Excel or PDF file'
    )
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
