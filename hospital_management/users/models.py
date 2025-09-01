from django.db import models
from authentication.models import NguoiDung


class BenhNhan(models.Model):
    GIOI_TINH_CHOICES = [
        ('Nam', 'Nam'),
        ('Nữ', 'Nữ'),
        ('Khác', 'Khác'),
    ]
    
    ma_benh_nhan = models.AutoField(primary_key=True, db_column='Ma_benh_nhan')
    ma_nguoi_dung = models.ForeignKey(
        NguoiDung, 
        on_delete=models.CASCADE, 
        db_column='Ma_nguoi_dung',
        related_name='benh_nhan'
    )
    ho_ten = models.CharField(max_length=100, db_column='Ho_ten')
    ngay_sinh = models.DateField(db_column='Ngay_sinh')
    gioi_tinh = models.CharField(max_length=10, choices=GIOI_TINH_CHOICES, db_column='Gioi_tinh')
    cmnd_cccd = models.CharField(max_length=20, unique=True, null=True, blank=True, db_column='CMND_CCCD')
    so_bhyt = models.CharField(max_length=20, null=True, blank=True, db_column='So_BHYT')
    so_dien_thoai = models.CharField(max_length=15, db_column='So_dien_thoai')
    email = models.EmailField(max_length=100, null=True, blank=True, db_column='Email')
    dia_chi = models.TextField(db_column='Dia_chi')
    
    class Meta:
        db_table = 'Benh_nhan'
        verbose_name = 'Benh nhan'
        verbose_name_plural = 'Benh nhan'
    
    def __str__(self):
        return f"{self.ho_ten} - {self.so_dien_thoai}"
