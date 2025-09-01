"""
Appointment domain repository implementations.
Handles data access for appointments and scheduling.
"""

from typing import Optional, List, Dict, Any
from django.db.models import Q, QuerySet, Count, F
from django.utils import timezone
from datetime import datetime, date, timedelta
from .base import BaseRepository, CachedRepository
import logging

logger = logging.getLogger(__name__)


class AppointmentRepository(CachedRepository):
    """
    Repository for LichHen (Appointment) model.
    """
    
    def __init__(self):
        from appointments.models import LichHen
        super().__init__(LichHen, cache_timeout=300)  # 5 minutes cache
    
    def find_by_patient(self, patient_id: int) -> QuerySet:
        """
        Find appointments by patient.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            QuerySet of appointments
        """
        return self.get_all(ma_benh_nhan_id=patient_id).order_by('-ngay_kham')
    
    def find_by_doctor(self, doctor_id: int) -> QuerySet:
        """
        Find appointments by doctor.
        
        Args:
            doctor_id: Doctor ID
            
        Returns:
            QuerySet of appointments
        """
        return self.get_all(ma_bac_si_id=doctor_id).order_by('ngay_kham', 'gio_kham')
    
    def find_by_date(self, appointment_date: date) -> QuerySet:
        """
        Find appointments by date.
        
        Args:
            appointment_date: Appointment date
            
        Returns:
            QuerySet of appointments
        """
        return self.get_all(ngay_kham=appointment_date).order_by('gio_kham')
    
    def find_by_status(self, status: str) -> QuerySet:
        """
        Find appointments by status.
        
        Args:
            status: Appointment status
            
        Returns:
            QuerySet of appointments
        """
        return self.get_all(trang_thai=status)
    
    def find_upcoming(self, days: int = 7) -> QuerySet:
        """
        Find upcoming appointments.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            QuerySet of upcoming appointments
        """
        end_date = timezone.now().date() + timedelta(days=days)
        return self.get_all(
            ngay_kham__gte=timezone.now().date(),
            ngay_kham__lte=end_date,
            trang_thai__in=['Cho xac nhan', 'Da xac nhan']
        ).order_by('ngay_kham', 'gio_kham')
    
    def find_overdue(self) -> QuerySet:
        """
        Find overdue appointments.
        
        Returns:
            QuerySet of overdue appointments
        """
        return self.get_all(
            ngay_kham__lt=timezone.now().date(),
            trang_thai='Cho xac nhan'
        )
    
    def get_appointment_with_details(self, appointment_id: int) -> Optional[Any]:
        """
        Get appointment with all related data.
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            Appointment instance with details
        """
        return self.get_queryset().select_related(
            'ma_benh_nhan',
            'ma_bac_si',
            'ma_dich_vu',
            'ma_lich'
        ).prefetch_related(
            'thanh_toan',
            'phien_tu_van'
        ).filter(pk=appointment_id).first()
    
    def check_time_slot_availability(self, doctor_id: int, appointment_date: date, 
                                     appointment_time: Any) -> bool:
        """
        Check if time slot is available.
        
        Args:
            doctor_id: Doctor ID
            appointment_date: Appointment date
            appointment_time: Appointment time
            
        Returns:
            True if available, False otherwise
        """
        existing = self.get_all(
            ma_bac_si_id=doctor_id,
            ngay_kham=appointment_date,
            gio_kham=appointment_time,
            trang_thai__in=['Cho xac nhan', 'Da xac nhan']
        ).exists()
        
        return not existing
    
    def get_appointment_statistics(self, start_date: date = None, 
                                  end_date: date = None) -> Dict[str, Any]:
        """
        Get appointment statistics.
        
        Args:
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            Dictionary with statistics
        """
        queryset = self.get_queryset()
        
        if start_date:
            queryset = queryset.filter(ngay_kham__gte=start_date)
        if end_date:
            queryset = queryset.filter(ngay_kham__lte=end_date)
        
        stats = queryset.aggregate(
            total=Count('ma_lich_hen'),
            pending=Count('ma_lich_hen', filter=Q(trang_thai='Cho xac nhan')),
            confirmed=Count('ma_lich_hen', filter=Q(trang_thai='Da xac nhan')),
            completed=Count('ma_lich_hen', filter=Q(trang_thai='Hoan thanh')),
            cancelled=Count('ma_lich_hen', filter=Q(trang_thai='Da huy'))
        )
        
        return {
            'total_appointments': stats['total'],
            'pending_appointments': stats['pending'],
            'confirmed_appointments': stats['confirmed'],
            'completed_appointments': stats['completed'],
            'cancelled_appointments': stats['cancelled'],
            'completion_rate': (stats['completed'] / stats['total'] * 100) 
                             if stats['total'] > 0 else 0,
            'cancellation_rate': (stats['cancelled'] / stats['total'] * 100) 
                               if stats['total'] > 0 else 0
        }


class ScheduleRepository(BaseRepository):
    """
    Repository for LichLamViec (Work Schedule) model.
    """
    
    def __init__(self):
        from appointments.models import LichLamViec
        super().__init__(LichLamViec)
    
    def find_by_doctor(self, doctor_id: int) -> QuerySet:
        """
        Find schedules by doctor.
        
        Args:
            doctor_id: Doctor ID
            
        Returns:
            QuerySet of schedules
        """
        return self.get_all(ma_bac_si_id=doctor_id).order_by('ngay_lam_viec', 'gio_bat_dau')
    
    def find_by_date(self, work_date: date) -> QuerySet:
        """
        Find schedules by date.
        
        Args:
            work_date: Work date
            
        Returns:
            QuerySet of schedules
        """
        return self.get_all(ngay_lam_viec=work_date).order_by('gio_bat_dau')
    
    def find_available_slots(self, doctor_id: int = None, 
                           work_date: date = None) -> QuerySet:
        """
        Find available schedule slots.
        
        Args:
            doctor_id: Filter by doctor
            work_date: Filter by date
            
        Returns:
            QuerySet of available slots
        """
        queryset = self.get_queryset().filter(
            so_luong_da_dat__lt=F('so_luong_kham')
        )
        
        if doctor_id:
            queryset = queryset.filter(ma_bac_si_id=doctor_id)
        if work_date:
            queryset = queryset.filter(ngay_lam_viec=work_date)
        
        return queryset.order_by('ngay_lam_viec', 'gio_bat_dau')
    
    def get_schedule_occupancy(self, schedule_id: int) -> Dict[str, Any]:
        """
        Get schedule occupancy information.
        
        Args:
            schedule_id: Schedule ID
            
        Returns:
            Dictionary with occupancy information
        """
        schedule = self.get_by_id(schedule_id)
        if not schedule:
            return {}
        
        return {
            'total_slots': schedule.so_luong_kham,
            'booked_slots': schedule.so_luong_da_dat,
            'available_slots': schedule.so_luong_kham - schedule.so_luong_da_dat,
            'occupancy_rate': (schedule.so_luong_da_dat / schedule.so_luong_kham * 100) 
                            if schedule.so_luong_kham > 0 else 0
        }
    
    def update_slot_count(self, schedule_id: int, increment: bool = True) -> bool:
        """
        Update booked slot count.
        
        Args:
            schedule_id: Schedule ID
            increment: True to increment, False to decrement
            
        Returns:
            True if updated successfully
        """
        try:
            schedule = self.get_by_id(schedule_id)
            if not schedule:
                return False
            
            if increment:
                if schedule.so_luong_da_dat < schedule.so_luong_kham:
                    schedule.so_luong_da_dat += 1
                else:
                    return False  # No available slots
            else:
                if schedule.so_luong_da_dat > 0:
                    schedule.so_luong_da_dat -= 1
            
            schedule.save()
            return True
            
        except Exception as e:
            logger.error(f"Error updating slot count: {str(e)}")
            return False


class TeleconsultationRepository(BaseRepository):
    """
    Repository for PhienTuVanTuXa (Teleconsultation Session) model.
    """
    
    def __init__(self):
        from appointments.models import PhienTuVanTuXa
        super().__init__(PhienTuVanTuXa)
    
    def find_by_status(self, status: str) -> QuerySet:
        """
        Find sessions by status.
        
        Args:
            status: Session status
            
        Returns:
            QuerySet of sessions
        """
        return self.get_all(trang_thai=status)
    
    def find_active_sessions(self) -> QuerySet:
        """
        Find currently active sessions.
        
        Returns:
            QuerySet of active sessions
        """
        return self.get_all(trang_thai='Dang dien ra')
    
    def find_pending_sessions(self) -> QuerySet:
        """
        Find pending sessions.
        
        Returns:
            QuerySet of pending sessions
        """
        return self.get_all(trang_thai='Chua bat dau')
    
    def get_session_with_appointment(self, session_id: int) -> Optional[Any]:
        """
        Get session with appointment details.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session instance with appointment
        """
        return self.get_queryset().select_related(
            'ma_lich_hen',
            'ma_lich_hen__ma_benh_nhan',
            'ma_lich_hen__ma_bac_si'
        ).filter(pk=session_id).first()
    
    def start_session(self, session_id: int, call_id: str = None) -> bool:
        """
        Start teleconsultation session.
        
        Args:
            session_id: Session ID
            call_id: Call identifier
            
        Returns:
            True if started successfully
        """
        try:
            session = self.get_by_id(session_id)
            if not session or session.trang_thai != 'Chua bat dau':
                return False
            
            session.trang_thai = 'Dang dien ra'
            session.thoi_gian_bat_dau = timezone.now()
            if call_id:
                session.ma_cuoc_goi = call_id
            
            session.save()
            return True
            
        except Exception as e:
            logger.error(f"Error starting session: {str(e)}")
            return False
    
    def end_session(self, session_id: int, notes: str = None) -> bool:
        """
        End teleconsultation session.
        
        Args:
            session_id: Session ID
            notes: Doctor's notes
            
        Returns:
            True if ended successfully
        """
        try:
            session = self.get_by_id(session_id)
            if not session or session.trang_thai != 'Dang dien ra':
                return False
            
            session.trang_thai = 'Da ket thuc'
            session.thoi_gian_ket_thuc = timezone.now()
            if notes:
                session.ghi_chu_bac_si = notes
            
            session.save()
            
            # Update appointment status
            if session.ma_lich_hen:
                session.ma_lich_hen.trang_thai = 'Hoan thanh'
                session.ma_lich_hen.save()
            
            return True
            
        except Exception as e:
            logger.error(f"Error ending session: {str(e)}")
            return False
