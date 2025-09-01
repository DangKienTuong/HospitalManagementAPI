"""
User and authentication service implementations.
Handles business logic for user management.
"""

from typing import Optional, Dict, Any, List
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from .base import CachedService
from ..repositories.user_repository import UserRepository, PatientRepository
import logging
import re

logger = logging.getLogger(__name__)


class UserService(CachedService):
    """
    Service for user management with authentication logic.
    Implements business rules for user operations.
    """
    
    def __init__(self):
        super().__init__(UserRepository())
        self.patient_repository = PatientRepository()
        
    def register_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register new user with role-specific profile.
        
        Args:
            data: Registration data
            
        Returns:
            Dictionary with user and tokens
            
        Raises:
            ValidationError: If registration fails
        """
        try:
            # Validate phone number format
            if not self._validate_phone_number(data.get('so_dien_thoai')):
                raise ValidationError({'so_dien_thoai': 'Invalid phone number format'})
            
            # Check if phone number already exists
            if self.repository.find_by_phone(data['so_dien_thoai']):
                raise ValidationError({'so_dien_thoai': 'Phone number already registered'})
            
            # Hash password
            if 'password' in data:
                data['password'] = make_password(data['password'])
            
            # Set default values
            data.setdefault('is_active', True)
            data.setdefault('trang_thai', True)
            
            with transaction.atomic():
                # Create user
                user = self.repository.create(**data)
                
                # Create role-specific profile
                if data.get('vai_tro') == 'Bệnh nhân' and 'profile_data' in data:
                    self._create_patient_profile(user, data['profile_data'])
                
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                
                return {
                    'user': user,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'message': 'Registration successful'
                }
                
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            raise ValidationError({'error': 'Registration failed'})
    
    def authenticate_user(self, phone_number: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate user and generate tokens.
        
        Args:
            phone_number: User phone number
            password: User password
            
        Returns:
            Dictionary with user and tokens or None
        """
        try:
            # Authenticate user
            user = authenticate(so_dien_thoai=phone_number, password=password)
            
            if not user:
                logger.warning(f"Authentication failed for phone: {phone_number}")
                return None
            
            if not user.is_active or not user.trang_thai:
                logger.warning(f"Inactive user attempted login: {phone_number}")
                return None
            
            # Update last login
            self.repository.update_last_login(user.ma_nguoi_dung)
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Get user profile based on role
            profile = self._get_user_profile(user)
            
            return {
                'user': user,
                'profile': profile,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'role': user.vai_tro
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None
    
    def change_password(self, user_id: int, old_password: str, 
                       new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully
        """
        try:
            user = self.repository.get_by_id(user_id)
            if not user:
                return False
            
            # Verify old password
            if not user.check_password(old_password):
                logger.warning(f"Invalid old password for user {user_id}")
                return False
            
            # Validate new password
            if not self._validate_password_strength(new_password):
                raise ValidationError({'password': 'Password does not meet requirements'})
            
            # Update password
            user.set_password(new_password)
            user.save()
            
            # Invalidate cache
            self.repository.invalidate_cache('get_by_id', user_id)
            
            logger.info(f"Password changed for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Password change failed: {str(e)}")
            return False
    
    def reset_password(self, phone_number: str, new_password: str) -> bool:
        """
        Reset user password (admin operation).
        
        Args:
            phone_number: User phone number
            new_password: New password
            
        Returns:
            True if password reset successfully
        """
        try:
            user = self.repository.find_by_phone(phone_number)
            if not user:
                return False
            
            # Validate new password
            if not self._validate_password_strength(new_password):
                raise ValidationError({'password': 'Password does not meet requirements'})
            
            # Update password
            user.set_password(new_password)
            user.save()
            
            # Invalidate cache
            self.repository.invalidate_cache('find_by_phone', phone_number)
            
            logger.info(f"Password reset for phone: {phone_number}")
            return True
            
        except Exception as e:
            logger.error(f"Password reset failed: {str(e)}")
            return False
    
    def deactivate_user(self, user_id: int, reason: str = None) -> bool:
        """
        Deactivate user account.
        
        Args:
            user_id: User ID
            reason: Deactivation reason
            
        Returns:
            True if deactivated successfully
        """
        result = self.repository.deactivate_user(user_id)
        
        if result and reason:
            # Log deactivation reason
            logger.info(f"User {user_id} deactivated. Reason: {reason}")
        
        return result
    
    def get_user_permissions(self, user_id: int) -> List[str]:
        """
        Get user permissions based on role.
        
        Args:
            user_id: User ID
            
        Returns:
            List of permission strings
        """
        user = self.repository.get_user_with_profile(user_id)
        if not user:
            return []
        
        # Define role-based permissions
        permissions_map = {
            'Admin': [
                'users.view', 'users.add', 'users.change', 'users.delete',
                'medical.view', 'medical.add', 'medical.change', 'medical.delete',
                'appointments.view', 'appointments.add', 'appointments.change', 'appointments.delete',
                'payments.view', 'payments.add', 'payments.change', 'payments.delete',
                'reports.view', 'reports.generate'
            ],
            'Bác sĩ': [
                'medical.view', 'medical.change_own',
                'appointments.view', 'appointments.change_own',
                'patients.view',
                'reports.view_own'
            ],
            'Bệnh nhân': [
                'appointments.view_own', 'appointments.add',
                'payments.view_own', 'payments.add',
                'profile.view_own', 'profile.change_own'
            ],
            'Nhân viên': [
                'users.view', 'users.add',
                'medical.view',
                'appointments.view', 'appointments.add', 'appointments.change',
                'payments.view', 'payments.add'
            ]
        }
        
        return permissions_map.get(user.vai_tro, [])
    
    def _validate_phone_number(self, phone: str) -> bool:
        """Validate Vietnamese phone number format."""
        if not phone:
            return False
        pattern = r'^(0|84|\+84)([3|5|7|8|9])+([0-9]{8})$'
        return bool(re.match(pattern, phone))
    
    def _validate_password_strength(self, password: str) -> bool:
        """
        Validate password strength.
        Requirements:
        - At least 8 characters
        - Contains uppercase and lowercase
        - Contains number
        - Contains special character
        """
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
        return True
    
    def _create_patient_profile(self, user, profile_data: Dict[str, Any]):
        """Create patient profile for user."""
        profile_data['ma_nguoi_dung'] = user
        profile_data.setdefault('so_dien_thoai', user.so_dien_thoai)
        return self.patient_repository.create(**profile_data)
    
    def _get_user_profile(self, user):
        """Get user profile based on role."""
        if user.vai_tro == 'Bệnh nhân':
            return self.patient_repository.get_all(ma_nguoi_dung=user).first()
        elif user.vai_tro == 'Bác sĩ':
            from medical.models import BacSi
            return BacSi.objects.filter(ma_nguoi_dung=user).first()
        return None


class PatientService(CachedService):
    """
    Service for patient management.
    Implements business logic for patient operations.
    """
    
    def __init__(self):
        super().__init__(PatientRepository())
        
    def create_patient(self, data: Dict[str, Any]) -> Any:
        """
        Create new patient with validation.
        
        Args:
            data: Patient data
            
        Returns:
            Created patient
        """
        # Validate ID number uniqueness
        if 'cmnd_cccd' in data and data['cmnd_cccd']:
            if self.repository.find_by_id_number(data['cmnd_cccd']):
                raise ValidationError({'cmnd_cccd': 'ID number already exists'})
        
        # Validate insurance number uniqueness
        if 'so_bhyt' in data and data['so_bhyt']:
            if self.repository.find_by_insurance_number(data['so_bhyt']):
                raise ValidationError({'so_bhyt': 'Insurance number already exists'})
        
        return super().create(data)
    
    def get_patient_history(self, patient_id: int) -> Dict[str, Any]:
        """
        Get patient's medical history.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Dictionary with patient history
        """
        patient = self.repository.get_patient_with_history(patient_id)
        if not patient:
            return {}
        
        appointments = patient.lich_hen.all()
        
        return {
            'patient': patient,
            'total_appointments': appointments.count(),
            'completed_appointments': appointments.filter(trang_thai='Hoan thanh').count(),
            'cancelled_appointments': appointments.filter(trang_thai='Da huy').count(),
            'upcoming_appointments': appointments.filter(trang_thai='Da xac nhan').count(),
            'appointments': appointments.order_by('-ngay_kham')[:10]  # Last 10 appointments
        }
    
    def search_patients(self, query: str, page: int = 1, 
                       page_size: int = 20) -> Dict[str, Any]:
        """
        Search patients with pagination.
        
        Args:
            query: Search query
            page: Page number
            page_size: Items per page
            
        Returns:
            Paginated search results
        """
        queryset = self.repository.search_patients(query)
        return self.repository.paginate(queryset, page, page_size)
