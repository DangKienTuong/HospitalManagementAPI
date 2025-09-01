"""
API v1 URL Configuration.
Version 1 of the Hospital Management System API.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import viewsets
from authentication.views import AuthViewSet
from users.views import BenhNhanViewSet
from medical.views import (
    CoSoYTeViewSet,
    ChuyenKhoaViewSet,
    BacSiViewSet,
    DichVuViewSet
)
from appointments.views import (
    LichLamViecViewSet,
    LichHenViewSet,
    PhienTuVanTuXaViewSet
)
from payments.views import ThanhToanViewSet

# Create router
router = DefaultRouter()

# Register viewsets
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users/benh-nhan', BenhNhanViewSet, basename='benh-nhan')
router.register(r'medical/co-so-y-te', CoSoYTeViewSet, basename='co-so-y-te')
router.register(r'medical/chuyen-khoa', ChuyenKhoaViewSet, basename='chuyen-khoa')
router.register(r'medical/bac-si', BacSiViewSet, basename='bac-si')
router.register(r'medical/dich-vu', DichVuViewSet, basename='dich-vu')
router.register(r'appointments/lich-lam-viec', LichLamViecViewSet, basename='lich-lam-viec')
router.register(r'appointments/lich-hen', LichHenViewSet, basename='lich-hen')
router.register(r'appointments/phien-tu-van', PhienTuVanTuXaViewSet, basename='phien-tu-van')
router.register(r'payments/thanh-toan', ThanhToanViewSet, basename='thanh-toan')

app_name = 'api_v1'

urlpatterns = [
    path('', include(router.urls)),
]
