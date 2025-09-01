from rest_framework import serializers
from django.utils import timezone
from .models import ThanhToan
from appointments.models import LichHen


class ThanhToanSerializer(serializers.ModelSerializer):
    ten_benh_nhan = serializers.CharField(source='ma_lich_hen.ma_benh_nhan.ho_ten', read_only=True)
    ten_bac_si = serializers.CharField(source='ma_lich_hen.ma_bac_si.ho_ten', read_only=True)
    ten_dich_vu = serializers.CharField(source='ma_lich_hen.ma_dich_vu.ten_dich_vu', read_only=True)
    ngay_kham = serializers.DateField(source='ma_lich_hen.ngay_kham', read_only=True)
    gio_kham = serializers.TimeField(source='ma_lich_hen.gio_kham', read_only=True)
    so_tien_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = ThanhToan
        fields = [
            'ma_thanh_toan', 'ma_lich_hen', 'so_tien', 'phuong_thuc', 
            'trang_thai', 'ma_giao_dich', 'thoi_gian_thanh_toan',
            'ten_benh_nhan', 'ten_bac_si', 'ten_dich_vu', 'ngay_kham', 
            'gio_kham', 'so_tien_formatted'
        ]
        read_only_fields = ['ma_thanh_toan', 'thoi_gian_thanh_toan']
    
    def get_so_tien_formatted(self, obj):
        return f"{obj.so_tien:,.0f} VNĐ"


class ThanhToanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThanhToan
        fields = ['ma_lich_hen', 'phuong_thuc', 'ma_giao_dich']
    
    def validate_ma_lich_hen(self, value):
        # Kiểm tra lịch hẹn đã có thanh toán chưa
        if ThanhToan.objects.filter(ma_lich_hen=value).exists():
            raise serializers.ValidationError("Lịch hẹn này đã có thanh toán")
        
        # Kiểm tra lịch hẹn phải được xác nhận
        if value.trang_thai not in ['Da xac nhan', 'Hoan thanh']:
            raise serializers.ValidationError("Chỉ có thể thanh toán cho lịch hẹn đã được xác nhận")
        
        return value
    
    def create(self, validated_data):
        lich_hen = validated_data['ma_lich_hen']
        
        # Lấy số tiền từ dịch vụ
        so_tien = lich_hen.ma_dich_vu.gia_tien
        
        thanh_toan = ThanhToan.objects.create(
            so_tien=so_tien,
            **validated_data
        )
        
        return thanh_toan


class ThanhToanUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThanhToan
        fields = ['trang_thai', 'ma_giao_dich']
    
    def validate_trang_thai(self, value):
        if value not in dict(ThanhToan.TRANG_THAI_CHOICES):
            raise serializers.ValidationError("Trạng thái thanh toán không hợp lệ")
        return value
