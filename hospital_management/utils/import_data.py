import pandas as pd
import io
from django.db import transaction
from django.core.exceptions import ValidationError
from rest_framework import serializers
from authentication.models import NguoiDung
from users.models import BenhNhan
from medical.models import CoSoYTe, ChuyenKhoa, BacSi, DichVu
from appointments.models import LichLamViec
from datetime import datetime


class DataImporter:
    """Lớp xử lý nhập dữ liệu từ file CSV/Excel"""
    
    @staticmethod
    def read_file(file, file_type='csv'):
        """Đọc file CSV hoặc Excel"""
        try:
            if file_type.lower() == 'csv':
                df = pd.read_csv(io.StringIO(file.read().decode('utf-8')))
            elif file_type.lower() in ['xlsx', 'xls']:
                df = pd.read_excel(file)
            else:
                raise ValueError("Chỉ hỗ trợ file CSV và Excel")
            
            return df
        except Exception as e:
            raise ValueError(f"Lỗi khi đọc file: {str(e)}")
    
    @staticmethod
    def validate_required_columns(df, required_columns):
        """Kiểm tra các cột bắt buộc"""
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Thiếu các cột bắt buộc: {', '.join(missing_columns)}")
    
    @staticmethod
    def import_benh_nhan(file, file_type='csv'):
        """Nhập dữ liệu bệnh nhân từ file"""
        required_columns = [
            'ho_ten', 'ngay_sinh', 'gioi_tinh', 'so_dien_thoai', 
            'dia_chi', 'mat_khau'
        ]
        
        try:
            df = DataImporter.read_file(file, file_type)
            DataImporter.validate_required_columns(df, required_columns)
            
            results = {
                'success': 0,
                'failed': 0,
                'errors': []
            }
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # Kiểm tra số điện thoại đã tồn tại chưa
                        if NguoiDung.objects.filter(so_dien_thoai=row['so_dien_thoai']).exists():
                            results['errors'].append(f"Dòng {index+1}: Số điện thoại {row['so_dien_thoai']} đã tồn tại")
                            results['failed'] += 1
                            continue
                        
                        # Tạo tài khoản người dùng
                        user = NguoiDung.objects.create_user(
                            so_dien_thoai=row['so_dien_thoai'],
                            password=row['mat_khau'],
                            vai_tro='Benh nhan'
                        )
                        
                        # Tạo bệnh nhân
                        BenhNhan.objects.create(
                            ma_nguoi_dung=user,
                            ho_ten=row['ho_ten'],
                            ngay_sinh=pd.to_datetime(row['ngay_sinh']).date(),
                            gioi_tinh=row['gioi_tinh'],
                            cmnd_cccd=row.get('cmnd_cccd', ''),
                            so_bhyt=row.get('so_bhyt', ''),
                            so_dien_thoai=row['so_dien_thoai'],
                            email=row.get('email', ''),
                            dia_chi=row['dia_chi']
                        )
                        
                        results['success'] += 1
                        
                    except Exception as e:
                        results['errors'].append(f"Dòng {index+1}: {str(e)}")
                        results['failed'] += 1
            
            return results
            
        except Exception as e:
            raise ValueError(f"Lỗi khi nhập dữ liệu: {str(e)}")
    
    @staticmethod
    def import_co_so_y_te(file, file_type='csv'):
        """Nhập dữ liệu cơ sở y tế từ file"""
        required_columns = ['ten_co_so', 'loai_hinh', 'dia_chi', 'so_dien_thoai']
        
        try:
            df = DataImporter.read_file(file, file_type)
            DataImporter.validate_required_columns(df, required_columns)
            
            results = {
                'success': 0,
                'failed': 0,
                'errors': []
            }
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        CoSoYTe.objects.create(
                            ten_co_so=row['ten_co_so'],
                            loai_hinh=row['loai_hinh'],
                            dia_chi=row['dia_chi'],
                            so_dien_thoai=row['so_dien_thoai'],
                            email=row.get('email', '')
                        )
                        
                        results['success'] += 1
                        
                    except Exception as e:
                        results['errors'].append(f"Dòng {index+1}: {str(e)}")
                        results['failed'] += 1
            
            return results
            
        except Exception as e:
            raise ValueError(f"Lỗi khi nhập dữ liệu: {str(e)}")
    
    @staticmethod
    def import_bac_si(file, file_type='csv'):
        """Nhập dữ liệu bác sĩ từ file"""
        required_columns = [
            'ho_ten', 'gioi_tinh', 'hoc_vi', 'kinh_nghiem',
            'ma_co_so', 'so_dien_thoai', 'mat_khau'
        ]
        
        try:
            df = DataImporter.read_file(file, file_type)
            DataImporter.validate_required_columns(df, required_columns)
            
            results = {
                'success': 0,
                'failed': 0,
                'errors': []
            }
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # Kiểm tra số điện thoại đã tồn tại chưa
                        if NguoiDung.objects.filter(so_dien_thoai=row['so_dien_thoai']).exists():
                            results['errors'].append(f"Dòng {index+1}: Số điện thoại {row['so_dien_thoai']} đã tồn tại")
                            results['failed'] += 1
                            continue
                        
                        # Kiểm tra cơ sở y tế tồn tại
                        try:
                            co_so = CoSoYTe.objects.get(ma_co_so=row['ma_co_so'])
                        except CoSoYTe.DoesNotExist:
                            results['errors'].append(f"Dòng {index+1}: Không tìm thấy cơ sở y tế có mã {row['ma_co_so']}")
                            results['failed'] += 1
                            continue
                        
                        # Tạo tài khoản người dùng
                        user = NguoiDung.objects.create_user(
                            so_dien_thoai=row['so_dien_thoai'],
                            password=row['mat_khau'],
                            vai_tro='Bác sĩ'
                        )
                        
                        # Lấy chuyên khoa nếu có
                        chuyen_khoa = None
                        if pd.notna(row.get('ma_chuyen_khoa')):
                            try:
                                chuyen_khoa = ChuyenKhoa.objects.get(ma_chuyen_khoa=row['ma_chuyen_khoa'])
                            except ChuyenKhoa.DoesNotExist:
                                pass
                        
                        # Tạo bác sĩ
                        BacSi.objects.create(
                            ma_nguoi_dung=user,
                            ma_co_so=co_so,
                            ma_chuyen_khoa=chuyen_khoa,
                            ho_ten=row['ho_ten'],
                            gioi_tinh=row['gioi_tinh'],
                            hoc_vi=row['hoc_vi'],
                            kinh_nghiem=int(row['kinh_nghiem']),
                            gioi_thieu=row.get('gioi_thieu', '')
                        )
                        
                        results['success'] += 1
                        
                    except Exception as e:
                        results['errors'].append(f"Dòng {index+1}: {str(e)}")
                        results['failed'] += 1
            
            return results
            
        except Exception as e:
            raise ValueError(f"Lỗi khi nhập dữ liệu: {str(e)}")
    
    @staticmethod
    def import_dich_vu(file, file_type='csv'):
        """Nhập dữ liệu dịch vụ từ file"""
        required_columns = [
            'ten_dich_vu', 'loai_dich_vu', 'gia_tien', 
            'thoi_gian_kham', 'ma_co_so'
        ]
        
        try:
            df = DataImporter.read_file(file, file_type)
            DataImporter.validate_required_columns(df, required_columns)
            
            results = {
                'success': 0,
                'failed': 0,
                'errors': []
            }
            
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # Kiểm tra cơ sở y tế tồn tại
                        try:
                            co_so = CoSoYTe.objects.get(ma_co_so=row['ma_co_so'])
                        except CoSoYTe.DoesNotExist:
                            results['errors'].append(f"Dòng {index+1}: Không tìm thấy cơ sở y tế có mã {row['ma_co_so']}")
                            results['failed'] += 1
                            continue
                        
                        # Lấy chuyên khoa nếu có
                        chuyen_khoa = None
                        if pd.notna(row.get('ma_chuyen_khoa')):
                            try:
                                chuyen_khoa = ChuyenKhoa.objects.get(ma_chuyen_khoa=row['ma_chuyen_khoa'])
                            except ChuyenKhoa.DoesNotExist:
                                pass
                        
                        # Tạo dịch vụ
                        DichVu.objects.create(
                            ma_co_so=co_so,
                            ma_chuyen_khoa=chuyen_khoa,
                            ten_dich_vu=row['ten_dich_vu'],
                            loai_dich_vu=row['loai_dich_vu'],
                            gia_tien=float(row['gia_tien']),
                            thoi_gian_kham=int(row['thoi_gian_kham']),
                            mo_ta=row.get('mo_ta', '')
                        )
                        
                        results['success'] += 1
                        
                    except Exception as e:
                        results['errors'].append(f"Dòng {index+1}: {str(e)}")
                        results['failed'] += 1
            
            return results
            
        except Exception as e:
            raise ValueError(f"Lỗi khi nhập dữ liệu: {str(e)}")
