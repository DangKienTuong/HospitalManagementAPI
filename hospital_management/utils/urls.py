from django.urls import path
from .views import (
    ExportBenhNhanView, ExportLichHenView
)

urlpatterns = [
    # Export endpoints
    path('export/benh-nhan/', ExportBenhNhanView.as_view(), name='export_benh_nhan'),
    path('export/lich-hen/', ExportLichHenView.as_view(), name='export_lich_hen'),
]
