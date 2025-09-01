import pandas as pd
import io
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

try:
    from users.models import BenhNhan
    from medical.models import CoSoYTe, BacSi, DichVu
    from appointments.models import LichHen
    from payments.models import ThanhToan
except ImportError as e:
    print(f"Import error: {e}")
    BenhNhan = None
    CoSoYTe = None
    BacSi = None
    DichVu = None
    LichHen = None
    ThanhToan = None


class DataExporter:
    """Lớp xử lý xuất dữ liệu ra file CSV/Excel/PDF"""
    
    @staticmethod
    def make_datetime_naive(dt):
        """Convert timezone-aware datetime to naive for Excel compatibility"""
        if dt is None:
            return None
        if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
            return dt.astimezone().replace(tzinfo=None)
        return dt
    
    @staticmethod
    def export_benh_nhan_csv():
        """Xuất danh sách bệnh nhân ra file CSV"""
        try:
            if BenhNhan is None:
                raise Exception("BenhNhan model is not available")
            
            benh_nhan = BenhNhan.objects.select_related('ma_nguoi_dung').all()
            
            data = []
            for bn in benh_nhan:
                try:
                    data.append({
                        'Mã bệnh nhân': bn.ma_benh_nhan,
                        'Họ tên': bn.ho_ten,
                        'Ngày sinh': bn.ngay_sinh.strftime('%d/%m/%Y') if bn.ngay_sinh else '',
                        'Giới tính': bn.gioi_tinh,
                        'Số điện thoại': bn.so_dien_thoai,
                        'Email': bn.email or '',
                        'Địa chỉ': bn.dia_chi,
                        'CMND/CCCD': bn.cmnd_cccd or '',
                        'Số BHYT': bn.so_bhyt or '',
                        'Ngày đăng ký': bn.ma_nguoi_dung.ngay_tao.strftime('%d/%m/%Y %H:%M') if bn.ma_nguoi_dung and bn.ma_nguoi_dung.ngay_tao else '',
                        'Trạng thái': 'Hoạt động' if bn.ma_nguoi_dung and bn.ma_nguoi_dung.trang_thai else 'Vô hiệu hóa'
                    })
                except AttributeError as e:
                    # Skip records with missing data
                    print(f"Skipping record due to missing data: {e}")
                    continue
            
            if not data:
                # Return empty CSV if no data
                data = [{'Thông báo': 'Không có dữ liệu bệnh nhân'}]
            
            df = pd.DataFrame(data)
            
            # CSV export with proper Vietnamese encoding
            csv_content = df.to_csv(index=False, sep=',', quoting=1)  # Quote all fields
            
            # Use Windows-1258 encoding specifically for Vietnamese
            try:
                # Try Windows-1258 (Vietnamese codepage)
                encoded_content = csv_content.encode('windows-1258')
                content_type = 'text/csv; charset=windows-1258'
            except UnicodeEncodeError:
                try:
                    # Fallback to CP1252 (Western European)
                    encoded_content = csv_content.encode('cp1252')
                    content_type = 'text/csv; charset=cp1252'
                except UnicodeEncodeError:
                    # Final fallback: UTF-8 with BOM
                    bom = '\ufeff'.encode('utf-8')
                    encoded_content = bom + csv_content.encode('utf-8')
                    content_type = 'text/csv; charset=utf-8'
            
            response = HttpResponse(
                encoded_content,
                content_type=content_type
            )
            response['Content-Disposition'] = f'attachment; filename="danh_sach_benh_nhan_{timezone.now().strftime("%Y%m%d")}.csv"'
            
            return response
            
        except Exception as e:
            # Create error response
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="error_export_{timezone.now().strftime("%Y%m%d")}.csv"'
            
            error_data = pd.DataFrame([{'Lỗi': f'Không thể xuất dữ liệu: {str(e)}'}])
            
            output = io.BytesIO()
            csv_string = error_data.to_csv(index=False, sep=';', encoding=None)
            
            output.write('\ufeff'.encode('utf-8'))
            output.write(csv_string.encode('utf-8'))
            
            response.write(output.getvalue())
            return response
    
    @staticmethod
    def export_benh_nhan_excel():
        """Xuất danh sách bệnh nhân ra file Excel"""
        try:
            if BenhNhan is None:
                raise Exception("BenhNhan model is not available")
                
            benh_nhan = BenhNhan.objects.select_related('ma_nguoi_dung').all()
            
            data = []
            for bn in benh_nhan:
                try:
                    # Convert timezone-aware datetime to timezone-naive for Excel compatibility
                    ngay_dang_ky = DataExporter.make_datetime_naive(
                        bn.ma_nguoi_dung.ngay_tao if bn.ma_nguoi_dung else None
                    )
                    
                    data.append({
                        'Mã bệnh nhân': bn.ma_benh_nhan,
                        'Họ tên': bn.ho_ten,
                        'Ngày sinh': bn.ngay_sinh,
                        'Giới tính': bn.gioi_tinh,
                        'Số điện thoại': bn.so_dien_thoai,
                        'Email': bn.email or '',
                        'Địa chỉ': bn.dia_chi,
                        'CMND/CCCD': bn.cmnd_cccd or '',
                        'Số BHYT': bn.so_bhyt or '',
                        'Ngày đăng ký': ngay_dang_ky,
                        'Trạng thái': 'Hoạt động' if bn.ma_nguoi_dung and bn.ma_nguoi_dung.trang_thai else 'Vô hiệu hóa'
                    })
                except AttributeError as e:
                    # Skip records with missing data
                    print(f"Skipping record due to missing data: {e}")
                    continue
            
            if not data:
                # Return Excel with message if no data
                data = [{'Thông báo': 'Không có dữ liệu bệnh nhân'}]
            
            df = pd.DataFrame(data)
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Danh sách bệnh nhân', index=False)
            
            output.seek(0)
            
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="danh_sach_benh_nhan_{timezone.now().strftime("%Y%m%d")}.xlsx"'
            
            return response
            
        except Exception as e:
            # Create error Excel file
            output = io.BytesIO()
            error_data = pd.DataFrame([{'Lỗi': f'Không thể xuất dữ liệu: {str(e)}'}])
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                error_data.to_excel(writer, sheet_name='Lỗi', index=False)
            
            output.seek(0)
            
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="error_export_{timezone.now().strftime("%Y%m%d")}.xlsx"'
            
            return response
    
    @staticmethod
    def export_lich_hen_excel(start_date=None, end_date=None):
        """Xuất báo cáo lịch hẹn ra file Excel"""
        queryset = LichHen.objects.select_related(
            'ma_benh_nhan', 'ma_bac_si', 'ma_dich_vu'
        ).all()
        
        if start_date:
            queryset = queryset.filter(ngay_kham__gte=start_date)
        if end_date:
            queryset = queryset.filter(ngay_kham__lte=end_date)
        
        data = []
        for lh in queryset:
            data.append({
                'Mã lịch hẹn': lh.ma_lich_hen,
                'Bệnh nhân': lh.ma_benh_nhan.ho_ten,
                'Số điện thoại': lh.ma_benh_nhan.so_dien_thoai,
                'Bác sĩ': f"{lh.ma_bac_si.hoc_vi} {lh.ma_bac_si.ho_ten}",
                'Dịch vụ': lh.ma_dich_vu.ten_dich_vu,
                'Ngày khám': lh.ngay_kham,
                'Giờ khám': lh.gio_kham,
                'Trạng thái': lh.trang_thai,
                'Giá dịch vụ': lh.ma_dich_vu.gia_tien,
                'Ngày tạo': DataExporter.make_datetime_naive(lh.ngay_tao),
                'Ghi chú': lh.ghi_chu
            })
        
        df = pd.DataFrame(data)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Báo cáo lịch hẹn', index=False)
        
        output.seek(0)
        
        filename = f"bao_cao_lich_hen_{timezone.now().strftime('%Y%m%d')}.xlsx"
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    @staticmethod
    def export_lich_hen_pdf(start_date=None, end_date=None):
        """Xuất báo cáo lịch hẹn ra file PDF"""
        response = HttpResponse(content_type='application/pdf')
        filename = f"bao_cao_lich_hen_{timezone.now().strftime('%Y%m%d')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Create PDF document
        doc = SimpleDocTemplate(response, pagesize=A4)
        story = []
        
        # Title
        styles = getSampleStyleSheet()
        title = Paragraph("BÁO CÁO LỊCH HẸN", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Date range
        if start_date and end_date:
            date_range = Paragraph(f"Từ ngày: {start_date} đến ngày: {end_date}", styles['Normal'])
            story.append(date_range)
            story.append(Spacer(1, 10))
        
        # Data
        queryset = LichHen.objects.select_related(
            'ma_benh_nhan', 'ma_bac_si', 'ma_dich_vu'
        ).all()
        
        if start_date:
            queryset = queryset.filter(ngay_kham__gte=start_date)
        if end_date:
            queryset = queryset.filter(ngay_kham__lte=end_date)
        
        # Table data
        table_data = [['STT', 'Bệnh nhân', 'Bác sĩ', 'Dịch vụ', 'Ngày khám', 'Trạng thái']]
        
        for i, lh in enumerate(queryset[:50], 1):  # Limit to 50 records for PDF
            table_data.append([
                str(i),
                lh.ma_benh_nhan.ho_ten,
                f"{lh.ma_bac_si.hoc_vi} {lh.ma_bac_si.ho_ten}",
                lh.ma_dich_vu.ten_dich_vu,
                lh.ngay_kham.strftime('%d/%m/%Y'),
                lh.trang_thai
            ])
        
        # Create table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        doc.build(story)
        
        return response
    
    @staticmethod
    def export_bao_cao_doanh_thu(start_date=None, end_date=None, file_format='excel'):
        """Xuất báo cáo doanh thu"""
        queryset = ThanhToan.objects.select_related(
            'ma_lich_hen__ma_bac_si', 'ma_lich_hen__ma_dich_vu'
        ).filter(trang_thai='Da thanh toan')
        
        if start_date:
            queryset = queryset.filter(thoi_gian_thanh_toan__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(thoi_gian_thanh_toan__date__lte=end_date)
        
        # Tính toán thống kê
        tong_doanh_thu = queryset.aggregate(total=Sum('so_tien'))['total'] or 0
        so_luong_giao_dich = queryset.count()
        
        # Doanh thu theo ngày
        doanh_thu_theo_ngay = {}
        for tt in queryset:
            thoi_gian = DataExporter.make_datetime_naive(tt.thoi_gian_thanh_toan)
            ngay = thoi_gian.date() if thoi_gian else None
            if ngay and ngay not in doanh_thu_theo_ngay:
                doanh_thu_theo_ngay[ngay] = 0
            if ngay:
                doanh_thu_theo_ngay[ngay] += tt.so_tien
        
        # Doanh thu theo dịch vụ
        doanh_thu_theo_dv = queryset.values(
            'ma_lich_hen__ma_dich_vu__ten_dich_vu'
        ).annotate(
            tong_tien=Sum('so_tien'),
            so_luong=Count('ma_thanh_toan')
        ).order_by('-tong_tien')
        
        if file_format.lower() == 'excel':
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Sheet 1: Tổng quan
                tong_quan_data = [{
                    'Chỉ số': 'Tổng doanh thu',
                    'Giá trị': f"{tong_doanh_thu:,.0f} VNĐ"
                }, {
                    'Chỉ số': 'Số lượng giao dịch',
                    'Giá trị': so_luong_giao_dich
                }]
                pd.DataFrame(tong_quan_data).to_excel(writer, sheet_name='Tổng quan', index=False)
                
                # Sheet 2: Doanh thu theo ngày
                ngay_data = []
                for ngay, doanh_thu in sorted(doanh_thu_theo_ngay.items()):
                    ngay_data.append({
                        'Ngày': ngay,  # This is already a date object, no timezone
                        'Doanh thu': doanh_thu
                    })
                pd.DataFrame(ngay_data).to_excel(writer, sheet_name='Theo ngày', index=False)
                
                # Sheet 3: Doanh thu theo dịch vụ
                dv_data = []
                for item in doanh_thu_theo_dv:
                    dv_data.append({
                        'Dịch vụ': item['ma_lich_hen__ma_dich_vu__ten_dich_vu'],
                        'Số lượng': item['so_luong'],
                        'Doanh thu': item['tong_tien']
                    })
                pd.DataFrame(dv_data).to_excel(writer, sheet_name='Theo dịch vụ', index=False)
            
            output.seek(0)
            
            filename = f"bao_cao_doanh_thu_{timezone.now().strftime('%Y%m%d')}.xlsx"
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
    
    @staticmethod
    def export_bao_cao_lich_hen(start_date=None, end_date=None, file_format='excel'):
        """Xuất báo cáo thống kê lịch hẹn"""
        queryset = LichHen.objects.select_related('ma_bac_si', 'ma_dich_vu').all()
        
        if start_date:
            queryset = queryset.filter(ngay_kham__gte=start_date)
        if end_date:
            queryset = queryset.filter(ngay_kham__lte=end_date)
        
        # Thống kê theo trạng thái
        thong_ke_trang_thai = queryset.values('trang_thai').annotate(
            so_luong=Count('ma_lich_hen')
        ).order_by('-so_luong')
        
        # Thống kê theo bác sĩ
        thong_ke_bac_si = queryset.values(
            'ma_bac_si__ho_ten'
        ).annotate(
            so_luong=Count('ma_lich_hen')
        ).order_by('-so_luong')[:10]
        
        # Thống kê theo dịch vụ
        thong_ke_dich_vu = queryset.values(
            'ma_dich_vu__ten_dich_vu'
        ).annotate(
            so_luong=Count('ma_lich_hen')
        ).order_by('-so_luong')[:10]
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Theo trạng thái
            pd.DataFrame(list(thong_ke_trang_thai)).to_excel(
                writer, sheet_name='Theo trạng thái', index=False
            )
            
            # Sheet 2: Theo bác sĩ
            pd.DataFrame(list(thong_ke_bac_si)).to_excel(
                writer, sheet_name='Top bác sĩ', index=False
            )
            
            # Sheet 3: Theo dịch vụ
            pd.DataFrame(list(thong_ke_dich_vu)).to_excel(
                writer, sheet_name='Top dịch vụ', index=False
            )
        
        output.seek(0)
        
        filename = f"thong_ke_lich_hen_{timezone.now().strftime('%Y%m%d')}.xlsx"
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    @staticmethod
    def export_bao_cao_benh_nhan(start_date=None, end_date=None, file_format='excel'):
        """Xuất báo cáo thống kê bệnh nhân"""
        queryset = BenhNhan.objects.select_related('ma_nguoi_dung').all()
        
        if start_date:
            queryset = queryset.filter(ma_nguoi_dung__ngay_tao__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(ma_nguoi_dung__ngay_tao__date__lte=end_date)
        
        # Thống kê theo giới tính
        thong_ke_gioi_tinh = queryset.values('gioi_tinh').annotate(
            so_luong=Count('ma_benh_nhan')
        )
        
        # Thống kê theo độ tuổi
        now = timezone.now().date()
        thong_ke_tuoi = {
            'Dưới 18': queryset.filter(ngay_sinh__gt=now - timedelta(days=18*365)).count(),
            '18-30': queryset.filter(
                ngay_sinh__lte=now - timedelta(days=18*365),
                ngay_sinh__gt=now - timedelta(days=30*365)
            ).count(),
            '30-50': queryset.filter(
                ngay_sinh__lte=now - timedelta(days=30*365),
                ngay_sinh__gt=now - timedelta(days=50*365)
            ).count(),
            'Trên 50': queryset.filter(ngay_sinh__lte=now - timedelta(days=50*365)).count(),
        }
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Theo giới tính
            pd.DataFrame(list(thong_ke_gioi_tinh)).to_excel(
                writer, sheet_name='Theo giới tính', index=False
            )
            
            # Sheet 2: Theo độ tuổi
            tuoi_data = [{'Nhóm tuổi': k, 'Số lượng': v} for k, v in thong_ke_tuoi.items()]
            pd.DataFrame(tuoi_data).to_excel(
                writer, sheet_name='Theo độ tuổi', index=False
            )
        
        output.seek(0)
        
        filename = f"thong_ke_benh_nhan_{timezone.now().strftime('%Y%m%d')}.xlsx"
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
