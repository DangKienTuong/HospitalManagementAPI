"""
Medical domain repository implementations.
Handles data access for medical facilities, doctors, and services.
"""

from typing import Optional, List, Dict, Any
from django.db.models import Q, QuerySet, Count, Avg
from .base import BaseRepository, CachedRepository
import logging

logger = logging.getLogger(__name__)


class MedicalFacilityRepository(CachedRepository):
    """
    Repository for CoSoYTe (Medical Facility) model.
    """
    
    def __init__(self):
        from medical.models import CoSoYTe
        super().__init__(CoSoYTe, cache_timeout=3600)  # 1 hour cache
    
    def find_by_type(self, facility_type: str) -> QuerySet:
        """
        Find facilities by type.
        
        Args:
            facility_type: Type of facility
            
        Returns:
            QuerySet of facilities
        """
        return self.get_all(loai_hinh=facility_type)
    
    def search_facilities(self, query: str) -> QuerySet:
        """
        Search facilities by name, address, or phone.
        
        Args:
            query: Search query
            
        Returns:
            QuerySet of matching facilities
        """
        q = Q(ten_co_so__icontains=query) | \
            Q(dia_chi__icontains=query) | \
            Q(so_dien_thoai__icontains=query) | \
            Q(email__icontains=query)
        
        return self.find(specification=q)
    
    def get_facility_with_details(self, facility_id: int) -> Optional[Any]:
        """
        Get facility with all related data.
        
        Args:
            facility_id: Facility ID
            
        Returns:
            Facility instance with prefetched data
        """
        return self.get_queryset().prefetch_related(
            'chuyen_khoa',
            'bac_si',
            'dich_vu'
        ).filter(pk=facility_id).first()
    
    def get_facilities_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about medical facilities.
        
        Returns:
            Dictionary with facility statistics
        """
        from medical.models import CoSoYTe
        
        try:
            stats = CoSoYTe.objects.aggregate(
                total=Count('ma_co_so'),
                by_type=Count('loai_hinh', distinct=True)
            )
            
            type_breakdown = CoSoYTe.objects.values('loai_hinh').annotate(
                count=Count('ma_co_so')
            )
            
            return {
                'total_facilities': stats['total'],
                'facility_types': stats['by_type'],
                'by_type': {item['loai_hinh']: item['count'] for item in type_breakdown}
            }
        except Exception as e:
            logger.error(f"Error getting facility statistics: {str(e)}")
            return {'total_facilities': 0, 'facility_types': 0, 'by_type': {}}


class DoctorRepository(CachedRepository):
    """
    Repository for BacSi (Doctor) model.
    """
    
    def __init__(self):
        from medical.models import BacSi
        super().__init__(BacSi, cache_timeout=1800)  # 30 minutes cache
    
    def find_by_specialty(self, specialty_id: int) -> QuerySet:
        """
        Find doctors by specialty.
        
        Args:
            specialty_id: Specialty ID
            
        Returns:
            QuerySet of doctors
        """
        return self.get_all(ma_chuyen_khoa_id=specialty_id)
    
    def find_by_facility(self, facility_id: int) -> QuerySet:
        """
        Find doctors by medical facility.
        
        Args:
            facility_id: Facility ID
            
        Returns:
            QuerySet of doctors
        """
        return self.get_all(ma_co_so_id=facility_id)
    
    def find_by_degree(self, degree: str) -> QuerySet:
        """
        Find doctors by academic degree.
        
        Args:
            degree: Academic degree
            
        Returns:
            QuerySet of doctors
        """
        return self.get_all(hoc_vi=degree)
    
    def search_doctors(self, query: str) -> QuerySet:
        """
        Search doctors by name or introduction.
        
        Args:
            query: Search query
            
        Returns:
            QuerySet of matching doctors
        """
        q = Q(ho_ten__icontains=query) | \
            Q(gioi_thieu__icontains=query) | \
            Q(ma_nguoi_dung__so_dien_thoai__icontains=query)
        
        return self.find(specification=q).select_related(
            'ma_nguoi_dung', 'ma_co_so', 'ma_chuyen_khoa'
        )
    
    def get_doctor_with_schedule(self, doctor_id: int) -> Optional[Any]:
        """
        Get doctor with work schedule.
        
        Args:
            doctor_id: Doctor ID
            
        Returns:
            Doctor instance with schedule
        """
        from django.utils import timezone
        from datetime import timedelta
        
        return self.get_queryset().prefetch_related(
            'lich_lam_viec'
        ).filter(
            pk=doctor_id,
            lich_lam_viec__ngay_lam_viec__gte=timezone.now().date()
        ).first()
    
    def get_available_doctors(self, date=None, specialty_id=None, facility_id=None) -> QuerySet:
        """
        Get doctors available for appointment.
        
        Args:
            date: Date to check availability
            specialty_id: Filter by specialty
            facility_id: Filter by facility
            
        Returns:
            QuerySet of available doctors
        """
        from django.utils import timezone
        
        if date is None:
            date = timezone.now().date()
        
        queryset = self.get_queryset().filter(
            lich_lam_viec__ngay_lam_viec=date,
            lich_lam_viec__so_luong_da_dat__lt=models.F('lich_lam_viec__so_luong_kham')
        ).distinct()
        
        if specialty_id:
            queryset = queryset.filter(ma_chuyen_khoa_id=specialty_id)
        if facility_id:
            queryset = queryset.filter(ma_co_so_id=facility_id)
        
        return queryset
    
    def get_doctor_statistics(self, doctor_id: int) -> Dict[str, Any]:
        """
        Get statistics for a specific doctor.
        
        Args:
            doctor_id: Doctor ID
            
        Returns:
            Dictionary with doctor statistics
        """
        from appointments.models import LichHen
        
        try:
            doctor = self.get_by_id(doctor_id)
            if not doctor:
                return {}
            
            stats = LichHen.objects.filter(ma_bac_si_id=doctor_id).aggregate(
                total_appointments=Count('ma_lich_hen'),
                completed=Count('ma_lich_hen', filter=Q(trang_thai='Hoan thanh')),
                cancelled=Count('ma_lich_hen', filter=Q(trang_thai='Da huy'))
            )
            
            return {
                'doctor_name': doctor.ho_ten,
                'experience_years': doctor.kinh_nghiem,
                'total_appointments': stats['total_appointments'],
                'completed_appointments': stats['completed'],
                'cancelled_appointments': stats['cancelled'],
                'completion_rate': (stats['completed'] / stats['total_appointments'] * 100) 
                                  if stats['total_appointments'] > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error getting doctor statistics: {str(e)}")
            return {}


class SpecialtyRepository(BaseRepository):
    """
    Repository for ChuyenKhoa (Specialty) model.
    """
    
    def __init__(self):
        from medical.models import ChuyenKhoa
        super().__init__(ChuyenKhoa)
    
    def find_by_facility(self, facility_id: int) -> QuerySet:
        """
        Find specialties by medical facility.
        
        Args:
            facility_id: Facility ID
            
        Returns:
            QuerySet of specialties
        """
        return self.get_all(ma_co_so_id=facility_id)
    
    def search_specialties(self, query: str) -> QuerySet:
        """
        Search specialties by name or description.
        
        Args:
            query: Search query
            
        Returns:
            QuerySet of matching specialties
        """
        q = Q(ten_chuyen_khoa__icontains=query) | Q(mo_ta__icontains=query)
        return self.find(specification=q)
    
    def get_specialty_with_doctors(self, specialty_id: int) -> Optional[Any]:
        """
        Get specialty with associated doctors.
        
        Args:
            specialty_id: Specialty ID
            
        Returns:
            Specialty instance with doctors
        """
        return self.get_queryset().prefetch_related(
            'bac_si',
            'bac_si__ma_nguoi_dung'
        ).filter(pk=specialty_id).first()


class ServiceRepository(CachedRepository):
    """
    Repository for DichVu (Medical Service) model.
    """
    
    def __init__(self):
        from medical.models import DichVu
        super().__init__(DichVu, cache_timeout=3600)  # 1 hour cache
    
    def find_by_type(self, service_type: str) -> QuerySet:
        """
        Find services by type.
        
        Args:
            service_type: Type of service
            
        Returns:
            QuerySet of services
        """
        return self.get_all(loai_dich_vu=service_type)
    
    def find_by_facility(self, facility_id: int) -> QuerySet:
        """
        Find services by medical facility.
        
        Args:
            facility_id: Facility ID
            
        Returns:
            QuerySet of services
        """
        return self.get_all(ma_co_so_id=facility_id)
    
    def find_by_specialty(self, specialty_id: int) -> QuerySet:
        """
        Find services by specialty.
        
        Args:
            specialty_id: Specialty ID
            
        Returns:
            QuerySet of services
        """
        return self.get_all(ma_chuyen_khoa_id=specialty_id)
    
    def find_teleconsultation_services(self) -> QuerySet:
        """
        Find all teleconsultation services.
        
        Returns:
            QuerySet of teleconsultation services
        """
        return self.find_by_type('Tư vấn từ xa')
    
    def search_services(self, query: str) -> QuerySet:
        """
        Search services by name or description.
        
        Args:
            query: Search query
            
        Returns:
            QuerySet of matching services
        """
        q = Q(ten_dich_vu__icontains=query) | Q(mo_ta__icontains=query)
        return self.find(specification=q)
    
    def get_services_by_price_range(self, min_price: float = None, 
                                    max_price: float = None) -> QuerySet:
        """
        Get services within price range.
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
            
        Returns:
            QuerySet of services
        """
        queryset = self.get_queryset()
        
        if min_price is not None:
            queryset = queryset.filter(gia_tien__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(gia_tien__lte=max_price)
        
        return queryset.order_by('gia_tien')
