from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BenhNhanViewSet

router = DefaultRouter()
router.register(r'benh-nhan', BenhNhanViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
