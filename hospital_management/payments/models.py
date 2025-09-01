from django.db import models
from django.utils import timezone
from appointments.models import LichHen


class ThanhToan(models.Model):
    PHUONG_THUC_CHOICES = [
        ('Tien mat', 'Tien mat'),
        ('Chuyen khoan', 'Chuyen khoan'),
        ('The tin dung', 'The tin dung'),
        ('Vi dien tu', 'Vi dien tu'),
    ]
    
    TRANG_THAI_CHOICES = [
        ('Chua thanh toan', 'Chua thanh toan'),
        ('Da thanh toan', 'Da thanh toan'),
        ('Da hoan tien', 'Da hoan tien'),
    ]
    
    ma_thanh_toan = models.AutoField(primary_key=True, db_column='Ma_thanh_toan')
    ma_lich_hen = models.OneToOneField(
        LichHen,
        on_delete=models.CASCADE,
        db_column='Ma_lich_hen',
        related_name='thanh_toan'
    )
    so_tien = models.DecimalField(max_digits=10, decimal_places=0, db_column='So_tien')
    phuong_thuc = models.CharField(max_length=50, choices=PHUONG_THUC_CHOICES, db_column='Phuong_thuc')
    trang_thai = models.CharField(
        max_length=20,
        choices=TRANG_THAI_CHOICES,
        default='Chua thanh toan',
        db_column='Trang_thai'
    )
    ma_giao_dich = models.CharField(max_length=100, null=True, blank=True, db_column='Ma_giao_dich')
    thoi_gian_thanh_toan = models.DateTimeField(null=True, blank=True, db_column='Thoi_gian_thanh_toan')
    
    class Meta:
        db_table = 'Thanh_toan'
        verbose_name = 'Thanh toan'
        verbose_name_plural = 'Thanh toan'
    
    def __str__(self):
        return f"Thanh toan {self.ma_thanh_toan} - {self.so_tien} VND"
    
    def save(self, *args, **kwargs):
        if self.trang_thai == 'Da thanh toan' and not self.thoi_gian_thanh_toan:
            self.thoi_gian_thanh_toan = timezone.now()
        super().save(*args, **kwargs)
