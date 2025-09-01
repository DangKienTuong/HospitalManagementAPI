from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from .models import NguoiDung


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'so_dien_thoai'
    so_dien_thoai = serializers.CharField(help_text="Phone number for login")
    mat_khau = serializers.CharField(help_text="Password", style={'input_type': 'password'})
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove default fields to avoid conflicts
        if 'username' in self.fields:
            del self.fields['username']
        if 'password' in self.fields:
            del self.fields['password']

    def validate(self, attrs):
        so_dien_thoai = attrs.get('so_dien_thoai')
        mat_khau = attrs.get('mat_khau')

        if so_dien_thoai and mat_khau:
            user = authenticate(
                request=self.context.get('request'),
                username=so_dien_thoai,
                password=mat_khau
            )
            
            if not user:
                raise serializers.ValidationError('Số điện thoại hoặc mật khẩu không đúng.')
            
            if not user.is_active:
                raise serializers.ValidationError('Tài khoản đã bị vô hiệu hóa.')
            
            # Add custom claims to token
            refresh = self.get_token(user)
            refresh['vai_tro'] = user.vai_tro
            refresh['so_dien_thoai'] = user.so_dien_thoai
            
            return {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'ma_nguoi_dung': user.ma_nguoi_dung,
                    'so_dien_thoai': user.so_dien_thoai,
                    'vai_tro': user.vai_tro,
                    'trang_thai': user.trang_thai,
                }
            }
        else:
            raise serializers.ValidationError('Vui lòng nhập đủ thông tin.')


class NguoiDungRegistrationSerializer(serializers.ModelSerializer):
    mat_khau = serializers.CharField(write_only=True, min_length=8)
    xac_nhan_mat_khau = serializers.CharField(write_only=True)
    
    class Meta:
        model = NguoiDung
        fields = ['so_dien_thoai', 'mat_khau', 'xac_nhan_mat_khau', 'vai_tro']
        
    def validate(self, attrs):
        if attrs['mat_khau'] != attrs['xac_nhan_mat_khau']:
            raise serializers.ValidationError("Mật khẩu xác nhận không khớp.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('xac_nhan_mat_khau')
        mat_khau = validated_data.pop('mat_khau')
        user = NguoiDung.objects.create_user(
            so_dien_thoai=validated_data['so_dien_thoai'],
            password=mat_khau,
            vai_tro=validated_data['vai_tro']
        )
        return user


class NguoiDungSerializer(serializers.ModelSerializer):
    class Meta:
        model = NguoiDung
        fields = ['ma_nguoi_dung', 'so_dien_thoai', 'vai_tro', 'ngay_tao', 'trang_thai']
        read_only_fields = ['ma_nguoi_dung', 'ngay_tao']


class ChangePasswordSerializer(serializers.Serializer):
    mat_khau_cu = serializers.CharField()
    mat_khau_moi = serializers.CharField(min_length=8)
    xac_nhan_mat_khau_moi = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['mat_khau_moi'] != attrs['xac_nhan_mat_khau_moi']:
            raise serializers.ValidationError("Mật khẩu mới không khớp.")
        return attrs
