from django.db import models
from django.utils import timezone
from users.models import BenhNhan
from medical.models import BacSi, DichVu


class LichLamViec(models.Model):
    ma_lich = models.AutoField(primary_key=True, db_column='Ma_lich')
    ma_bac_si = models.ForeignKey(
        BacSi,
        on_delete=models.CASCADE,
        db_column='Ma_bac_si',
        related_name='lich_lam_viec'
    )
    ngay_lam_viec = models.DateField(db_column='Ngay_lam_viec')
    gio_bat_dau = models.TimeField(db_column='Gio_bat_dau')
    gio_ket_thuc = models.TimeField(db_column='Gio_ket_thuc')
    so_luong_kham = models.IntegerField(default=20, db_column='So_luong_kham')
    so_luong_da_dat = models.IntegerField(default=0, db_column='So_luong_da_dat')
    
    class Meta:
        db_table = 'Lich_lam_viec'
        verbose_name = 'Lich lam viec'
        verbose_name_plural = 'Lich lam viec'
        unique_together = [['ma_bac_si', 'ngay_lam_viec', 'gio_bat_dau']]
    
    def __str__(self):
        return f"{self.ma_bac_si.ho_ten} - {self.ngay_lam_viec} {self.gio_bat_dau}"
    
    @property
    def con_cho_trong(self):
        return self.so_luong_kham - self.so_luong_da_dat


class LichHen(models.Model):
    TRANG_THAI_CHOICES = [
        ('Cho xac nhan', 'Cho xac nhan'),
        ('Da xac nhan', 'Da xac nhan'),
        ('Hoan thanh', 'Hoan thanh'),
        ('Da huy', 'Da huy'),
    ]
    
    ma_lich_hen = models.AutoField(primary_key=True, db_column='Ma_lich_hen')
    ma_benh_nhan = models.ForeignKey(
        BenhNhan,
        on_delete=models.CASCADE,
        db_column='Ma_benh_nhan',
        related_name='lich_hen'
    )
    ma_bac_si = models.ForeignKey(
        BacSi,
        on_delete=models.CASCADE,
        db_column='Ma_bac_si',
        related_name='lich_hen'
    )
    ma_dich_vu = models.ForeignKey(
        DichVu,
        on_delete=models.CASCADE,
        db_column='Ma_dich_vu',
        related_name='lich_hen'
    )
    ma_lich = models.ForeignKey(
        LichLamViec,
        on_delete=models.CASCADE,
        db_column='Ma_lich',
        related_name='lich_hen'
    )
    ngay_kham = models.DateField(db_column='Ngay_kham')
    gio_kham = models.TimeField(db_column='Gio_kham')
    so_thu_tu = models.IntegerField(db_column='So_thu_tu')
    trang_thai = models.CharField(
        max_length=20, 
        choices=TRANG_THAI_CHOICES, 
        default='Cho xac nhan',
        db_column='Trang_thai'
    )
    ghi_chu = models.TextField(null=True, blank=True, db_column='Ghi_chu')
    ngay_tao = models.DateTimeField(default=timezone.now, db_column='Ngay_tao')
    
    class Meta:
        db_table = 'Lich_hen'
        verbose_name = 'Lich hen'
        verbose_name_plural = 'Lich hen'
    
    def __str__(self):
        return f"{self.ma_benh_nhan.ho_ten} - {self.ma_bac_si.ho_ten} - {self.ngay_kham}"


class PhienTuVanTuXa(models.Model):
    TRANG_THAI_CHOICES = [
        ('Chua bat dau', 'Chua bat dau'),
        ('Dang dien ra', 'Dang dien ra'),
        ('Da ket thuc', 'Da ket thuc'),
        ('Da huy', 'Da huy'),
    ]
    
    ma_phien = models.AutoField(primary_key=True, db_column='Ma_phien')
    ma_lich_hen = models.OneToOneField(
        LichHen,
        on_delete=models.CASCADE,
        db_column='Ma_lich_hen',
        related_name='phien_tu_van'
    )
    ma_cuoc_goi = models.CharField(max_length=100, unique=True, null=True, blank=True, db_column='Ma_cuoc_goi')
    thoi_gian_bat_dau = models.DateTimeField(null=True, blank=True, db_column='Thoi_gian_bat_dau')
    thoi_gian_ket_thuc = models.DateTimeField(null=True, blank=True, db_column='Thoi_gian_ket_thuc')
    trang_thai = models.CharField(
        max_length=20,
        choices=TRANG_THAI_CHOICES,
        default='Chua bat dau',
        db_column='Trang_thai'
    )
    ghi_chu_bac_si = models.TextField(null=True, blank=True, db_column='Ghi_chu_bac_si')
    
    class Meta:
        db_table = 'Phien_tu_van_tu_xa'
        verbose_name = 'Phien tu van tu xa'
        verbose_name_plural = 'Phien tu van tu xa'
    
    def __str__(self):
        return f"Phien {self.ma_phien} - {self.ma_lich_hen.ma_benh_nhan.ho_ten}"
