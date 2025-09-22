from rest_framework import serializers
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError
from datetime import datetime, time, timedelta
from .models import LichLamViec, LichHen, PhienTuVanTuXa
from users.models import BenhNhan
from medical.models import BacSi, DichVu
from core.repositories.appointment_repository import AppointmentRepository
from core.validators import AppointmentTimeValidator


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
    ma_benh_nhan = serializers.PrimaryKeyRelatedField(
        queryset=BenhNhan.objects.all(),
        required=False,
        help_text="ID của bệnh nhân (bắt buộc nếu user là Admin)"
    )
    
    class Meta:
        model = LichHen
        fields = ['ma_benh_nhan', 'ma_bac_si', 'ma_dich_vu', 'ma_lich', 'ghi_chu']
    
    def validate(self, attrs):
        # Kiểm tra lịch làm việc còn chỗ trống
        lich_lam_viec = attrs['ma_lich']
        if lich_lam_viec.con_cho_trong <= 0:
            raise serializers.ValidationError("Lịch làm việc đã hết chỗ trống")
        
        # Kiểm tra bác sĩ và lịch làm việc khớp nhau
        if lich_lam_viec.ma_bac_si != attrs['ma_bac_si']:
            raise serializers.ValidationError("Bác sĩ không khớp với lịch làm việc")
        
        user = self.context['request'].user
        
        # Xác định bệnh nhân cho validation
        if user.vai_tro == 'Admin':
            if 'ma_benh_nhan' not in attrs:
                raise serializers.ValidationError("Admin phải chỉ định bệnh nhân cho lịch hẹn")
            benh_nhan = attrs['ma_benh_nhan']
            try:
                BenhNhan.objects.get(pk=benh_nhan.pk)
            except (BenhNhan.DoesNotExist, AttributeError):
                raise serializers.ValidationError("Bệnh nhân không tồn tại")
        else:
            try:
                benh_nhan = BenhNhan.objects.get(ma_nguoi_dung=user)
            except BenhNhan.DoesNotExist:
                raise serializers.ValidationError("Không tìm thấy thông tin bệnh nhân")
        
        # ===== CONFLICT DETECTION VALIDATION =====
        
        # 1. Validate appointment time using business rules
        appointment_datetime = timezone.make_aware(
            datetime.combine(lich_lam_viec.ngay_lam_viec, lich_lam_viec.gio_bat_dau)
        )
        
        try:
            appointment_validator = AppointmentTimeValidator()
            appointment_validator.validate(appointment_datetime)
        except DjangoValidationError as e:
            raise serializers.ValidationError(f"Thời gian đặt lịch không hợp lệ: {e.message}")
        
        # 2. Check if doctor has conflicting appointments (time slot availability)
        appointment_repo = AppointmentRepository()
        is_available = appointment_repo.check_time_slot_availability(
            doctor_id=attrs['ma_bac_si'].pk,
            appointment_date=lich_lam_viec.ngay_lam_viec,
            appointment_time=lich_lam_viec.gio_bat_dau
        )
        
        if not is_available:
            raise serializers.ValidationError(
                f"Bác sĩ {attrs['ma_bac_si'].ho_ten} đã có lịch hẹn vào thời gian này"
            )
        
        # 3. Check if patient has conflicting appointments
        patient_conflicts = LichHen.objects.filter(
            ma_benh_nhan=benh_nhan,
            ngay_kham=lich_lam_viec.ngay_lam_viec,
            gio_kham=lich_lam_viec.gio_bat_dau,
            trang_thai__in=['Cho xac nhan', 'Da xac nhan']
        ).exists()
        
        if patient_conflicts:
            raise serializers.ValidationError(
                "Bệnh nhân đã có lịch hẹn vào thời gian này"
            )
        
        # 4. Check if patient has another appointment within 30 minutes
        time_buffer = timedelta(minutes=30)
        appointment_start = appointment_datetime
        appointment_end = appointment_start + time_buffer
        
        nearby_appointments = LichHen.objects.filter(
            ma_benh_nhan=benh_nhan,
            ngay_kham=lich_lam_viec.ngay_lam_viec,
            trang_thai__in=['Cho xac nhan', 'Da xac nhan']
        )
        
        for appt in nearby_appointments:
            existing_datetime = timezone.make_aware(
                datetime.combine(appt.ngay_kham, appt.gio_kham)
            )
            
            # Check if appointments are too close to each other
            time_diff = abs((existing_datetime - appointment_start).total_seconds())
            if time_diff < time_buffer.total_seconds():
                raise serializers.ValidationError(
                    f"Bệnh nhân đã có lịch hẹn vào {appt.gio_kham.strftime('%H:%M')}. "
                    f"Các lịch hẹn phải cách nhau ít nhất 30 phút."
                )
        
        # 5. Additional validation: Check if patient has too many appointments per day
        daily_appointments = LichHen.objects.filter(
            ma_benh_nhan=benh_nhan,
            ngay_kham=lich_lam_viec.ngay_lam_viec,
            trang_thai__in=['Cho xac nhan', 'Da xac nhan']
        ).count()
        
        if daily_appointments >= 3:  # Maximum 3 appointments per day
            raise serializers.ValidationError(
                "Bệnh nhân đã đạt giới hạn tối đa 3 lịch hẹn trong ngày"
            )
        
        return attrs
    
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Xác định bệnh nhân cho lịch hẹn
        if user.vai_tro == 'Admin':
            # Admin có thể tạo lịch hẹn cho bất kỳ bệnh nhân nào
            if 'ma_benh_nhan' not in validated_data:
                raise serializers.ValidationError("Admin phải chỉ định bệnh nhân cho lịch hẹn")
            benh_nhan = validated_data['ma_benh_nhan']
            # Remove ma_benh_nhan from validated_data to avoid duplicate field error
            validated_data.pop('ma_benh_nhan', None)
        else:
            # Bệnh nhân chỉ có thể tạo lịch hẹn cho chính mình
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
