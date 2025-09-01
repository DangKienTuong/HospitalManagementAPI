from rest_framework import serializers
from .models import CoSoYTe, ChuyenKhoa, BacSi, DichVu
from authentication.models import NguoiDung


class CoSoYTeSerializer(serializers.ModelSerializer):
    so_luong_chuyen_khoa = serializers.IntegerField(source='chuyen_khoa.count', read_only=True)
    so_luong_bac_si = serializers.IntegerField(source='bac_si.count', read_only=True)
    
    class Meta:
        model = CoSoYTe
        fields = [
            'ma_co_so', 'ten_co_so', 'loai_hinh', 'dia_chi', 
            'so_dien_thoai', 'email', 'so_luong_chuyen_khoa', 'so_luong_bac_si'
        ]
        read_only_fields = ['ma_co_so']


class ChuyenKhoaSerializer(serializers.ModelSerializer):
    ten_co_so = serializers.CharField(source='ma_co_so.ten_co_so', read_only=True)
    so_luong_bac_si = serializers.IntegerField(source='bac_si.count', read_only=True)
    so_luong_dich_vu = serializers.IntegerField(source='dich_vu.count', read_only=True)
    
    class Meta:
        model = ChuyenKhoa
        fields = [
            'ma_chuyen_khoa', 'ma_co_so', 'ten_chuyen_khoa', 'mo_ta',
            'ten_co_so', 'so_luong_bac_si', 'so_luong_dich_vu'
        ]
        read_only_fields = ['ma_chuyen_khoa']


class BacSiSerializer(serializers.ModelSerializer):
    so_dien_thoai_user = serializers.CharField(source='ma_nguoi_dung.so_dien_thoai', read_only=True)
    ten_co_so = serializers.CharField(source='ma_co_so.ten_co_so', read_only=True)
    ten_chuyen_khoa = serializers.CharField(source='ma_chuyen_khoa.ten_chuyen_khoa', read_only=True)
    so_luong_lich_hen = serializers.IntegerField(source='lich_hen.count', read_only=True)
    
    class Meta:
        model = BacSi
        fields = [
            'ma_bac_si', 'ma_nguoi_dung', 'ma_co_so', 'ma_chuyen_khoa',
            'ho_ten', 'gioi_tinh', 'hoc_vi', 'kinh_nghiem', 'gioi_thieu',
            'so_dien_thoai_user', 'ten_co_so', 'ten_chuyen_khoa', 'so_luong_lich_hen'
        ]
        read_only_fields = ['ma_bac_si']


class BacSiCreateSerializer(serializers.Serializer):
    """Serializer để tạo bác sĩ cùng với tài khoản người dùng"""
    ma_co_so = serializers.IntegerField()
    ma_chuyen_khoa = serializers.IntegerField(required=False, allow_null=True)
    ho_ten = serializers.CharField(max_length=100)
    gioi_tinh = serializers.ChoiceField(choices=BacSi.GIOI_TINH_CHOICES)
    hoc_vi = serializers.ChoiceField(choices=BacSi.HOC_VI_CHOICES)
    kinh_nghiem = serializers.IntegerField()
    gioi_thieu = serializers.CharField(required=False, allow_blank=True)
    so_dien_thoai = serializers.CharField(max_length=15)
    mat_khau = serializers.CharField(write_only=True, min_length=8)
    xac_nhan_mat_khau = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['mat_khau'] != attrs['xac_nhan_mat_khau']:
            raise serializers.ValidationError("Mật khẩu xác nhận không khớp.")
        return attrs
    
    def create(self, validated_data):
        so_dien_thoai = validated_data.pop('so_dien_thoai')
        mat_khau = validated_data.pop('mat_khau')
        validated_data.pop('xac_nhan_mat_khau')
        
        # Tạo tài khoản người dùng
        user = NguoiDung.objects.create_user(
            so_dien_thoai=so_dien_thoai,
            password=mat_khau,
            vai_tro='Bác sĩ'
        )
        
        # Get the actual model instances for foreign keys
        ma_co_so = CoSoYTe.objects.get(ma_co_so=validated_data['ma_co_so'])
        ma_chuyen_khoa = None
        if validated_data.get('ma_chuyen_khoa'):
            ma_chuyen_khoa = ChuyenKhoa.objects.get(ma_chuyen_khoa=validated_data['ma_chuyen_khoa'])
        
        # Tạo hồ sơ bác sĩ
        bac_si = BacSi.objects.create(
            ma_nguoi_dung=user,
            ma_co_so=ma_co_so,
            ma_chuyen_khoa=ma_chuyen_khoa,
            ho_ten=validated_data['ho_ten'],
            gioi_tinh=validated_data['gioi_tinh'],
            hoc_vi=validated_data['hoc_vi'],
            kinh_nghiem=validated_data['kinh_nghiem'],
            gioi_thieu=validated_data.get('gioi_thieu', '')
        )
        
        return bac_si
    
    def to_representation(self, instance):
        """Convert the BacSi instance to a proper representation"""
        return BacSiSerializer(instance).data


class DichVuSerializer(serializers.ModelSerializer):
    ten_co_so = serializers.CharField(source='ma_co_so.ten_co_so', read_only=True)
    ten_chuyen_khoa = serializers.CharField(source='ma_chuyen_khoa.ten_chuyen_khoa', read_only=True)
    gia_tien_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = DichVu
        fields = [
            'ma_dich_vu', 'ma_co_so', 'ma_chuyen_khoa', 'ten_dich_vu',
            'loai_dich_vu', 'gia_tien', 'thoi_gian_kham', 'mo_ta',
            'ten_co_so', 'ten_chuyen_khoa', 'gia_tien_formatted'
        ]
        read_only_fields = ['ma_dich_vu']
    
    def get_gia_tien_formatted(self, obj):
        return f"{obj.gia_tien:,.0f} VNĐ"
