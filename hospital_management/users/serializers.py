from rest_framework import serializers
from .models import BenhNhan
from authentication.models import NguoiDung


class BenhNhanSerializer(serializers.ModelSerializer):
    so_dien_thoai_user = serializers.CharField(source='ma_nguoi_dung.so_dien_thoai', read_only=True)
    vai_tro = serializers.CharField(source='ma_nguoi_dung.vai_tro', read_only=True)
    
    class Meta:
        model = BenhNhan
        fields = [
            'ma_benh_nhan', 'ma_nguoi_dung', 'ho_ten', 'ngay_sinh', 
            'gioi_tinh', 'cmnd_cccd', 'so_bhyt', 'so_dien_thoai', 
            'email', 'dia_chi', 'so_dien_thoai_user', 'vai_tro'
        ]
        read_only_fields = ['ma_benh_nhan']

    def validate_cmnd_cccd(self, value):
        if value and len(value) not in [9, 12]:
            raise serializers.ValidationError("CMND phải có 9 số hoặc CCCD phải có 12 số")
        return value

    def validate_so_bhyt(self, value):
        if value and len(value) != 15:
            raise serializers.ValidationError("Số BHYT phải có 15 ký tự")
        return value


class BenhNhanCreateSerializer(serializers.Serializer):
    """Serializer để tạo bệnh nhân cùng với tài khoản người dùng"""
    ho_ten = serializers.CharField(max_length=100)
    ngay_sinh = serializers.DateField()
    gioi_tinh = serializers.ChoiceField(choices=BenhNhan.GIOI_TINH_CHOICES)
    cmnd_cccd = serializers.CharField(max_length=20, required=False, allow_blank=True)
    so_bhyt = serializers.CharField(max_length=20, required=False, allow_blank=True)
    so_dien_thoai = serializers.CharField(max_length=15)
    email = serializers.EmailField(required=False, allow_blank=True)
    dia_chi = serializers.CharField()
    mat_khau = serializers.CharField(write_only=True, min_length=8)
    xac_nhan_mat_khau = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['mat_khau'] != attrs['xac_nhan_mat_khau']:
            raise serializers.ValidationError("Mật khẩu xác nhận không khớp.")
        return attrs
    
    def create(self, validated_data):
        mat_khau = validated_data.pop('mat_khau')
        validated_data.pop('xac_nhan_mat_khau')
        
        # Tạo tài khoản người dùng
        user = NguoiDung.objects.create_user(
            so_dien_thoai=validated_data['so_dien_thoai'],
            password=mat_khau,
            vai_tro='Benh nhan'
        )
        
        # Tạo hồ sơ bệnh nhân
        benh_nhan = BenhNhan.objects.create(
            ma_nguoi_dung=user,
            **validated_data
        )
        
        return benh_nhan
    
    def to_representation(self, instance):
        """Convert the BenhNhan instance to a proper representation"""
        return BenhNhanSerializer(instance).data
