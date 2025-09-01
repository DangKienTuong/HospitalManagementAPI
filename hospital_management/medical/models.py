from django.db import models
from authentication.models import NguoiDung


class CoSoYTe(models.Model):
    LOAI_HINH_CHOICES = [
        ('Bệnh viện công', 'Bệnh viện công'),
        ('Bệnh viện tư', 'Bệnh viện tư'),
        ('Phòng khám', 'Phòng khám'),
        ('Trung tâm y tế', 'Trung tâm y tế'),
    ]
    
    ma_co_so = models.AutoField(primary_key=True, db_column='Ma_co_so')
    ten_co_so = models.CharField(max_length=200, db_column='Ten_co_so')
    loai_hinh = models.CharField(max_length=50, choices=LOAI_HINH_CHOICES, db_column='Loai_hinh')
    dia_chi = models.TextField(db_column='Dia_chi')
    so_dien_thoai = models.CharField(max_length=15, db_column='So_dien_thoai')
    email = models.EmailField(max_length=100, null=True, blank=True, db_column='Email')
    
    class Meta:
        db_table = 'Co_so_y_te'
        verbose_name = 'Co so y te'
        verbose_name_plural = 'Co so y te'
    
    def __str__(self):
        return self.ten_co_so


class ChuyenKhoa(models.Model):
    ma_chuyen_khoa = models.AutoField(primary_key=True, db_column='Ma_chuyen_khoa')
    ma_co_so = models.ForeignKey(
        CoSoYTe,
        on_delete=models.CASCADE,
        db_column='Ma_co_so',
        related_name='chuyen_khoa'
    )
    ten_chuyen_khoa = models.CharField(max_length=100, db_column='Ten_chuyen_khoa')
    mo_ta = models.TextField(null=True, blank=True, db_column='Mo_ta')
    
    class Meta:
        db_table = 'Chuyen_khoa'
        verbose_name = 'Chuyen khoa'
        verbose_name_plural = 'Chuyen khoa'
        unique_together = [['ma_co_so', 'ten_chuyen_khoa']]
    
    def __str__(self):
        return f"{self.ten_chuyen_khoa} - {self.ma_co_so.ten_co_so}"


class BacSi(models.Model):
    GIOI_TINH_CHOICES = [
        ('Nam', 'Nam'),
        ('Nữ', 'Nữ'),
    ]
    
    HOC_VI_CHOICES = [
        ('Bác sĩ', 'Bác sĩ'),
        ('Thạc sĩ', 'Thạc sĩ'),
        ('Tiến sĩ', 'Tiến sĩ'),
        ('Phó giáo sư', 'Phó giáo sư'),
        ('Giáo sư', 'Giáo sư'),
    ]
    
    ma_bac_si = models.AutoField(primary_key=True, db_column='Ma_bac_si')
    ma_nguoi_dung = models.OneToOneField(
        NguoiDung,
        on_delete=models.CASCADE,
        db_column='Ma_nguoi_dung',
        related_name='bac_si'
    )
    ma_co_so = models.ForeignKey(
        CoSoYTe,
        on_delete=models.CASCADE,
        db_column='Ma_co_so',
        related_name='bac_si'
    )
    ma_chuyen_khoa = models.ForeignKey(
        ChuyenKhoa,
        on_delete=models.SET_NULL,
        null=True,
        db_column='Ma_chuyen_khoa',
        related_name='bac_si'
    )
    ho_ten = models.CharField(max_length=100, db_column='Ho_ten')
    gioi_tinh = models.CharField(max_length=10, choices=GIOI_TINH_CHOICES, db_column='Gioi_tinh')
    hoc_vi = models.CharField(max_length=20, choices=HOC_VI_CHOICES, db_column='Hoc_vi')
    kinh_nghiem = models.IntegerField(db_column='Kinh_nghiem')
    gioi_thieu = models.TextField(null=True, blank=True, db_column='Gioi_thieu')
    
    class Meta:
        db_table = 'Bac_si'
        verbose_name = 'Bac si'
        verbose_name_plural = 'Bac si'
    
    def __str__(self):
        return f"{self.hoc_vi} {self.ho_ten}"


class DichVu(models.Model):
    LOAI_DICH_VU_CHOICES = [
        ('Khám bệnh', 'Khám bệnh'),
        ('Xét nghiệm', 'Xét nghiệm'),
        ('Chẩn đoán hình ảnh', 'Chẩn đoán hình ảnh'),
        ('Thủ thuật', 'Thủ thuật'),
        ('Tư vấn từ xa', 'Tư vấn từ xa'),
    ]
    
    ma_dich_vu = models.AutoField(primary_key=True, db_column='Ma_dich_vu')
    ma_co_so = models.ForeignKey(
        CoSoYTe,
        on_delete=models.CASCADE,
        db_column='Ma_co_so',
        related_name='dich_vu'
    )
    ma_chuyen_khoa = models.ForeignKey(
        ChuyenKhoa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='Ma_chuyen_khoa',
        related_name='dich_vu'
    )
    ten_dich_vu = models.CharField(max_length=200, db_column='Ten_dich_vu')
    loai_dich_vu = models.CharField(max_length=50, choices=LOAI_DICH_VU_CHOICES, db_column='Loai_dich_vu')
    gia_tien = models.DecimalField(max_digits=10, decimal_places=0, db_column='Gia_tien')
    thoi_gian_kham = models.IntegerField(db_column='Thoi_gian_kham')
    mo_ta = models.TextField(null=True, blank=True, db_column='Mo_ta')
    
    class Meta:
        db_table = 'Dich_vu'
        verbose_name = 'Dich vu'
        verbose_name_plural = 'Dich vu'
    
    def __str__(self):
        return f"{self.ten_dich_vu} - {self.ma_co_so.ten_co_so}"
