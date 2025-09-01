from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Quyền cho Admin"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.vai_tro == 'Admin'
        )


class IsDoctorUser(permissions.BasePermission):
    """Quyền cho Bác sĩ"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.vai_tro == 'Bác sĩ'
        )


class IsPatientUser(permissions.BasePermission):
    """Quyền cho Bệnh nhân"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.vai_tro == 'Bệnh nhân'
        )


class IsStaffUser(permissions.BasePermission):
    """Quyền cho Nhân viên y tế"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.vai_tro == 'Nhân viên'
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Chỉ cho phép chủ sở hữu chỉnh sửa, những người khác chỉ đọc"""
    
    def has_object_permission(self, request, view, obj):
        # Quyền đọc cho tất cả requests
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Quyền ghi chỉ cho chủ sở hữu
        return obj.ma_nguoi_dung == request.user


class IsDoctorOrAdmin(permissions.BasePermission):
    """Cho phép bác sĩ hoặc admin truy cập"""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.vai_tro in ['Bác sĩ', 'Admin']
        )
