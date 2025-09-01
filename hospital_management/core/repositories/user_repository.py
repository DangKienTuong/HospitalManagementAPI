"""
User-related repository implementations.
Handles data access for authentication and user management.
"""

from typing import Optional, List, Dict, Any
from django.db.models import Q, QuerySet
from django.contrib.auth import get_user_model
from .base import CachedRepository
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class UserRepository(CachedRepository):
    """
    Repository for User/NguoiDung model.
    Implements user-specific data access patterns.
    """
    
    def __init__(self):
        super().__init__(User, cache_timeout=600)  # 10 minutes cache
    
    def find_by_phone(self, phone_number: str) -> Optional[User]:
        """
        Find user by phone number.
        
        Args:
            phone_number: Phone number to search
            
        Returns:
            User instance or None
        """
        cache_key = self._get_cache_key('find_by_phone', phone_number)
        
        # Check cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        try:
            user = self.model.objects.filter(so_dien_thoai=phone_number).first()
            if user:
                self.cache.set(cache_key, user, self.cache_timeout)
            return user
        except Exception as e:
            logger.error(f"Error finding user by phone: {str(e)}")
            return None
    
    def find_by_role(self, role: str) -> QuerySet:
        """
        Find users by role.
        
        Args:
            role: User role (Admin, Bác sĩ, Bệnh nhân, Nhân viên)
            
        Returns:
            QuerySet of users with specified role
        """
        return self.get_all(vai_tro=role)
    
    def find_active_users(self) -> QuerySet:
        """
        Get all active users.
        
        Returns:
            QuerySet of active users
        """
        return self.get_all(trang_thai=True, is_active=True)
    
    def search_users(self, query: str) -> QuerySet:
        """
        Search users by phone number or related patient/doctor name.
        
        Args:
            query: Search query
            
        Returns:
            QuerySet of matching users
        """
        q = Q(so_dien_thoai__icontains=query)
        
        # Search in related models based on role
        q |= Q(benh_nhan__ho_ten__icontains=query)
        q |= Q(bac_si__ho_ten__icontains=query)
        
        return self.find(specification=q)
    
    def get_user_with_profile(self, user_id: int) -> Optional[User]:
        """
        Get user with related profile data.
        
        Args:
            user_id: User ID
            
        Returns:
            User instance with prefetched profile data
        """
        try:
            return self.model.objects.select_related(
                'benh_nhan', 'bac_si'
            ).prefetch_related(
                'groups', 'user_permissions'
            ).get(pk=user_id)
        except self.model.DoesNotExist:
            return None
    
    def update_last_login(self, user_id: int) -> bool:
        """
        Update user's last login timestamp.
        
        Args:
            user_id: User ID
            
        Returns:
            True if updated successfully
        """
        from django.utils import timezone
        
        try:
            user = self.get_by_id(user_id)
            if user:
                user.last_login = timezone.now()
                user.save(update_fields=['last_login'])
                self.invalidate_cache('get_by_id', user_id)
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating last login: {str(e)}")
            return False
    
    def deactivate_user(self, user_id: int) -> bool:
        """
        Deactivate user account.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deactivated successfully
        """
        try:
            user = self.get_by_id(user_id)
            if user:
                user.is_active = False
                user.trang_thai = False
                user.save(update_fields=['is_active', 'trang_thai'])
                self.invalidate_cache('get_by_id', user_id)
                logger.info(f"Deactivated user {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deactivating user: {str(e)}")
            return False
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """
        Get user statistics by role.
        
        Returns:
            Dictionary with user statistics
        """
        from django.db.models import Count
        
        try:
            stats = self.model.objects.values('vai_tro').annotate(
                count=Count('ma_nguoi_dung')
            ).order_by('vai_tro')
            
            total = self.model.objects.count()
            active = self.model.objects.filter(is_active=True).count()
            
            return {
                'total_users': total,
                'active_users': active,
                'inactive_users': total - active,
                'by_role': {item['vai_tro']: item['count'] for item in stats}
            }
        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            return {
                'total_users': 0,
                'active_users': 0,
                'inactive_users': 0,
                'by_role': {}
            }


class PatientRepository(CachedRepository):
    """
    Repository for BenhNhan (Patient) model.
    """
    
    def __init__(self):
        from users.models import BenhNhan
        super().__init__(BenhNhan, cache_timeout=300)
    
    def find_by_id_number(self, id_number: str) -> Optional[Any]:
        """
        Find patient by ID card number.
        
        Args:
            id_number: CMND/CCCD number
            
        Returns:
            Patient instance or None
        """
        return self.get_all(cmnd_cccd=id_number).first()
    
    def find_by_insurance_number(self, insurance_number: str) -> Optional[Any]:
        """
        Find patient by health insurance number.
        
        Args:
            insurance_number: BHYT number
            
        Returns:
            Patient instance or None
        """
        return self.get_all(so_bhyt=insurance_number).first()
    
    def search_patients(self, query: str) -> QuerySet:
        """
        Search patients by name, phone, email, or ID.
        
        Args:
            query: Search query
            
        Returns:
            QuerySet of matching patients
        """
        q = Q(ho_ten__icontains=query) | \
            Q(so_dien_thoai__icontains=query) | \
            Q(email__icontains=query) | \
            Q(cmnd_cccd__icontains=query) | \
            Q(so_bhyt__icontains=query)
        
        return self.find(specification=q)
    
    def get_patient_with_history(self, patient_id: int) -> Optional[Any]:
        """
        Get patient with appointment history.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Patient instance with prefetched history
        """
        return self.get_queryset().prefetch_related(
            'lich_hen',
            'lich_hen__ma_bac_si',
            'lich_hen__ma_dich_vu',
            'lich_hen__thanh_toan'
        ).filter(pk=patient_id).first()
