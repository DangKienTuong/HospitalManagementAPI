from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ThanhToanViewSet

router = DefaultRouter()
router.register(r'thanh-toan', ThanhToanViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('statistics/',
         ThanhToanViewSet.as_view({'get': 'statistics'}),
         name='payment-statistics'),
]
