from django.urls import path
from .views import (
    ImportBenhNhanView, ImportCoSoYTeView, ImportBacSiView, ImportDichVuView,
    ExportBenhNhanView, ExportLichHenView, ExportThongKeView
)

urlpatterns = [
    # Import endpoints
    path('import/benh-nhan/', ImportBenhNhanView.as_view(), name='import_benh_nhan'),
    path('import/co-so-y-te/', ImportCoSoYTeView.as_view(), name='import_co_so_y_te'),
    path('import/bac-si/', ImportBacSiView.as_view(), name='import_bac_si'),
    path('import/dich-vu/', ImportDichVuView.as_view(), name='import_dich_vu'),
    
    # Export endpoints
    path('export/benh-nhan/', ExportBenhNhanView.as_view(), name='export_benh_nhan'),
    path('export/lich-hen/', ExportLichHenView.as_view(), name='export_lich_hen'),
    path('export/thong-ke/', ExportThongKeView.as_view(), name='export_thong_ke'),
]
