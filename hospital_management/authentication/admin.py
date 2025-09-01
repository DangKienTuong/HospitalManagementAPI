from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import NguoiDung


@admin.register(NguoiDung)
class NguoiDungAdmin(UserAdmin):
    list_display = ['so_dien_thoai', 'vai_tro', 'trang_thai', 'ngay_tao']
    list_filter = ['vai_tro', 'trang_thai', 'ngay_tao']
    search_fields = ['so_dien_thoai', 'vai_tro']
    ordering = ['-ngay_tao']
    
    fieldsets = (
        (None, {'fields': ('so_dien_thoai', 'password')}),
        ('Thông tin cá nhân', {'fields': ('vai_tro', 'trang_thai')}),
        ('Quyền hạn', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Ngày tháng quan trọng', {'fields': ('last_login', 'ngay_tao')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('so_dien_thoai', 'vai_tro', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ['ngay_tao']
