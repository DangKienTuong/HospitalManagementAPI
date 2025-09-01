from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, time
from .models import LichLamViec, LichHen, PhienTuVanTuXa
from users.models import BenhNhan
from medical.models import BacSi, DichVu


class LichLamViecSerializer(serializers.ModelSerializer):
    ten_bac_si = serializers.CharField(source='ma_bac_si.ho_ten', read_only=True)
    hoc_vi = serializers.CharField(source='ma_bac_si.hoc_vi', read_only=True)
    ten_chuyen_khoa = serializers.CharField(source='ma_bac_si.ma_chuyen_khoa.ten_chuyen_khoa', read_only=True)
    con_cho_trong = serializers.ReadOnlyField()
    
    class Meta:
        model = LichLamViec
        fields = [
            'ma_lich', 'ma_bac_si', 'ngay_lam_viec', 'gio_bat_dau', 
            'gio_ket_thuc', 'so_luong_kham', 'so_luong_da_dat',
            'ten_bac_si', 'hoc_vi', 'ten_chuyen_khoa', 'con_cho_trong'
        ]
        read_only_fields = ['ma_lich', 'so_luong_da_dat']
    
    def validate(self, attrs):
        if attrs['gio_bat_dau'] >= attrs['gio_ket_thuc']:
            raise serializers.ValidationError("Giờ bắt đầu phải nhỏ hơn giờ kết thúc")
        
        if attrs['ngay_lam_viec'] < timezone.now().date():
            raise serializers.ValidationError("Không thể tạo lịch làm việc trong quá khứ")
        
        return attrs


class LichHenSerializer(serializers.ModelSerializer):
    ten_benh_nhan = serializers.CharField(source='ma_benh_nhan.ho_ten', read_only=True)
    sdt_benh_nhan = serializers.CharField(source='ma_benh_nhan.so_dien_thoai', read_only=True)
    ten_bac_si = serializers.CharField(source='ma_bac_si.ho_ten', read_only=True)
    hoc_vi_bac_si = serializers.CharField(source='ma_bac_si.hoc_vi', read_only=True)
    ten_dich_vu = serializers.CharField(source='ma_dich_vu.ten_dich_vu', read_only=True)
    gia_dich_vu = serializers.DecimalField(source='ma_dich_vu.gia_tien', max_digits=10, decimal_places=0, read_only=True)
    thoi_gian_kham = serializers.IntegerField(source='ma_dich_vu.thoi_gian_kham', read_only=True)
    
    class Meta:
        model = LichHen
        fields = [
            'ma_lich_hen', 'ma_benh_nhan', 'ma_bac_si', 'ma_dich_vu', 'ma_lich',
            'ngay_kham', 'gio_kham', 'so_thu_tu', 'trang_thai', 'ghi_chu', 'ngay_tao',
            'ten_benh_nhan', 'sdt_benh_nhan', 'ten_bac_si', 'hoc_vi_bac_si', 
            'ten_dich_vu', 'gia_dich_vu', 'thoi_gian_kham'
        ]
        read_only_fields = ['ma_lich_hen', 'so_thu_tu', 'ngay_tao']


class LichHenCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LichHen
        fields = ['ma_bac_si', 'ma_dich_vu', 'ma_lich', 'ghi_chu']
    
    def validate(self, attrs):
        # Kiểm tra lịch làm việc còn chỗ trống
        lich_lam_viec = attrs['ma_lich']
        if lich_lam_viec.con_cho_trong <= 0:
            raise serializers.ValidationError("Lịch làm việc đã hết chỗ trống")
        
        # Kiểm tra bác sĩ và lịch làm việc khớp nhau
        if lich_lam_viec.ma_bac_si != attrs['ma_bac_si']:
            raise serializers.ValidationError("Bác sĩ không khớp với lịch làm việc")
        
        return attrs
    
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Lấy thông tin bệnh nhân từ user hiện tại
        try:
            benh_nhan = BenhNhan.objects.get(ma_nguoi_dung=user)
        except BenhNhan.DoesNotExist:
            raise serializers.ValidationError("Không tìm thấy thông tin bệnh nhân")
        
        lich_lam_viec = validated_data['ma_lich']
        
        # Tính số thứ tự tiếp theo
        so_thu_tu = lich_lam_viec.so_luong_da_dat + 1
        
        # Tạo lịch hẹn
        lich_hen = LichHen.objects.create(
            ma_benh_nhan=benh_nhan,
            ngay_kham=lich_lam_viec.ngay_lam_viec,
            gio_kham=lich_lam_viec.gio_bat_dau,
            so_thu_tu=so_thu_tu,
            **validated_data
        )
        
        # Cập nhật số lượng đã đặt
        lich_lam_viec.so_luong_da_dat += 1
        lich_lam_viec.save()
        
        return lich_hen


class PhienTuVanTuXaSerializer(serializers.ModelSerializer):
    ten_benh_nhan = serializers.CharField(source='ma_lich_hen.ma_benh_nhan.ho_ten', read_only=True)
    ten_bac_si = serializers.CharField(source='ma_lich_hen.ma_bac_si.ho_ten', read_only=True)
    ngay_kham = serializers.DateField(source='ma_lich_hen.ngay_kham', read_only=True)
    gio_kham = serializers.TimeField(source='ma_lich_hen.gio_kham', read_only=True)
    
    class Meta:
        model = PhienTuVanTuXa
        fields = [
            'ma_phien', 'ma_lich_hen', 'ma_cuoc_goi', 'thoi_gian_bat_dau',
            'thoi_gian_ket_thuc', 'trang_thai', 'ghi_chu_bac_si',
            'ten_benh_nhan', 'ten_bac_si', 'ngay_kham', 'gio_kham'
        ]
        read_only_fields = ['ma_phien']
    
    def validate(self, attrs):
        if 'thoi_gian_bat_dau' in attrs and 'thoi_gian_ket_thuc' in attrs:
            if attrs['thoi_gian_bat_dau'] >= attrs['thoi_gian_ket_thuc']:
                raise serializers.ValidationError("Thời gian bắt đầu phải nhỏ hơn thời gian kết thúc")
        
        return attrs
