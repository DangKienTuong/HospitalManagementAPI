from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LichLamViecViewSet,
    LichHenViewSet,
    PhienTuVanTuXaViewSet,
)

router = DefaultRouter()
router.register(r'lich-lam-viec', LichLamViecViewSet)
router.register(r'lich-hen', LichHenViewSet)
router.register(r'phien-tu-van', PhienTuVanTuXaViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('lich-hen/statistics/',
         LichHenViewSet.as_view({'get': 'statistics'}),
         name='appointment-statistics'),
]
