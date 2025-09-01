from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class NguoiDungManager(BaseUserManager):
    def create_user(self, so_dien_thoai, password=None, **extra_fields):
        if not so_dien_thoai:
            raise ValueError('Số điện thoại là bắt buộc')

        user = self.model(so_dien_thoai=so_dien_thoai, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, so_dien_thoai, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('vai_tro', 'Admin')
        extra_fields.setdefault('trang_thai', True)
        
        return self.create_user(so_dien_thoai, password, **extra_fields)


class NguoiDung(AbstractBaseUser, PermissionsMixin):
    VAI_TRO_CHOICES = [
        ('Admin', 'Quản trị viên'),
        ('Bác sĩ', 'Bác sĩ'),
        ('Bệnh nhân', 'Bệnh nhân'),
        ('Nhân viên', 'Nhân viên y tế'),
    ]
    
    ma_nguoi_dung = models.AutoField(primary_key=True, db_column='Ma_nguoi_dung')
    so_dien_thoai = models.CharField(max_length=15, unique=True, db_column='So_dien_thoai')
    password = models.CharField(max_length=128, db_column='Mat_khau')  # Django's password field
    vai_tro = models.CharField(max_length=20, choices=VAI_TRO_CHOICES, db_column='Vai_tro')
    ngay_tao = models.DateTimeField(default=timezone.now, db_column='Ngay_tao')
    trang_thai = models.BooleanField(default=True, db_column='Trang_thai')
    
    # Django required fields
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    objects = NguoiDungManager()
    
    USERNAME_FIELD = 'so_dien_thoai'
    REQUIRED_FIELDS = ['vai_tro']
    
    class Meta:
        db_table = 'Nguoi_dung'
        verbose_name = 'Nguoi dung'
        verbose_name_plural = 'Nguoi dung'
    
    def __str__(self):
        return f"{self.so_dien_thoai} - {self.vai_tro}"
