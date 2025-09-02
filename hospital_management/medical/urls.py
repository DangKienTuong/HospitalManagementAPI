from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CoSoYTeViewSet, ChuyenKhoaViewSet, BacSiViewSet, DichVuViewSet

router = DefaultRouter()
router.register(r'co-so-y-te', CoSoYTeViewSet)
router.register(r'chuyen-khoa', ChuyenKhoaViewSet)
router.register(r'bac-si', BacSiViewSet)
router.register(r'dich-vu', DichVuViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
