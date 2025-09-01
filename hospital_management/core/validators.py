"""
Custom validators for Hospital Management System.
Provides comprehensive validation for data integrity and business rules.
"""

import re
from typing import Any, Dict, List, Optional
from datetime import datetime, date, time, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


# Phone Number Validators
class VietnamesePhoneValidator(BaseValidator):
    """
    Validator for Vietnamese phone numbers.
    Supports formats: 0xxxxxxxxx, 84xxxxxxxxx, +84xxxxxxxxx
    """
    
    message = 'Enter a valid Vietnamese phone number.'
    code = 'invalid_phone'
    
    def __call__(self, value):
        pattern = r'^(0|84|\+84)([3|5|7|8|9])+([0-9]{8})$'
        if not re.match(pattern, str(value)):
            raise ValidationError(self.message, code=self.code)


class InternationalPhoneValidator(BaseValidator):
    """Validator for international phone numbers."""
    
    message = 'Enter a valid international phone number.'
    code = 'invalid_phone'
    
    def __call__(self, value):
        pattern = r'^\+?[1-9]\d{1,14}$'  # E.164 format
        if not re.match(pattern, str(value)):
            raise ValidationError(self.message, code=self.code)


# ID Document Validators
class VietnameseIDValidator(BaseValidator):
    """
    Validator for Vietnamese ID cards (CMND/CCCD).
    Validates 9 or 12 digit formats.
    """
    
    message = 'Enter a valid Vietnamese ID number (9 or 12 digits).'
    code = 'invalid_id'
    
    def __call__(self, value):
        if value:
            pattern = r'^([0-9]{9}|[0-9]{12})$'
            if not re.match(pattern, str(value)):
                raise ValidationError(self.message, code=self.code)


class HealthInsuranceNumberValidator(BaseValidator):
    """Validator for Vietnamese health insurance numbers."""
    
    message = 'Enter a valid health insurance number.'
    code = 'invalid_insurance'
    
    def __call__(self, value):
        if value:
            # Vietnamese health insurance format
            pattern = r'^[A-Z]{2}[0-9]{1}[0-9]{2}[0-9]{10}$'
            if not re.match(pattern, str(value).upper()):
                raise ValidationError(self.message, code=self.code)


# Date and Time Validators
class FutureDateValidator(BaseValidator):
    """Validator to ensure date is in the future."""
    
    message = 'Date must be in the future.'
    code = 'not_future'
    
    def __call__(self, value):
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%d').date()
        
        if value <= timezone.now().date():
            raise ValidationError(self.message, code=self.code)


class PastDateValidator(BaseValidator):
    """Validator to ensure date is in the past."""
    
    message = 'Date must be in the past.'
    code = 'not_past'
    
    def __call__(self, value):
        if isinstance(value, str):
            value = datetime.strptime(value, '%Y-%m-%d').date()
        
        if value >= timezone.now().date():
            raise ValidationError(self.message, code=self.code)


class AgeValidator(BaseValidator):
    """Validator for age based on birth date."""
    
    def __init__(self, min_age: int = 0, max_age: int = 150):
        self.min_age = min_age
        self.max_age = max_age
        self.message = f'Age must be between {min_age} and {max_age} years.'
        self.code = 'invalid_age'
    
    def __call__(self, birth_date):
        if isinstance(birth_date, str):
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        
        today = timezone.now().date()
        age = today.year - birth_date.year - (
            (today.month, today.day) < (birth_date.month, birth_date.day)
        )
        
        if age < self.min_age or age > self.max_age:
            raise ValidationError(self.message, code=self.code)


class WorkingHoursValidator(BaseValidator):
    """Validator for working hours."""
    
    message = 'Time must be within working hours (6:00 AM - 10:00 PM).'
    code = 'outside_working_hours'
    
    def __call__(self, value):
        if isinstance(value, str):
            value = datetime.strptime(value, '%H:%M:%S').time()
        
        min_time = time(6, 0)  # 6:00 AM
        max_time = time(22, 0)  # 10:00 PM
        
        if value < min_time or value > max_time:
            raise ValidationError(self.message, code=self.code)


# Password Validators
class CustomPasswordValidator:
    """
    Enhanced password validator with specific requirements.
    """
    
    def __init__(self):
        self.min_length = 8
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digits = True
        self.require_special = True
        self.special_chars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    
    def validate(self, password, user=None):
        errors = []
        
        if len(password) < self.min_length:
            errors.append(
                ValidationError(
                    f'Password must be at least {self.min_length} characters long.',
                    code='password_too_short'
                )
            )
        
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append(
                ValidationError(
                    'Password must contain at least one uppercase letter.',
                    code='password_no_upper'
                )
            )
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append(
                ValidationError(
                    'Password must contain at least one lowercase letter.',
                    code='password_no_lower'
                )
            )
        
        if self.require_digits and not re.search(r'\d', password):
            errors.append(
                ValidationError(
                    'Password must contain at least one digit.',
                    code='password_no_digit'
                )
            )
        
        if self.require_special and not any(c in self.special_chars for c in password):
            errors.append(
                ValidationError(
                    f'Password must contain at least one special character ({self.special_chars}).',
                    code='password_no_special'
                )
            )
        
        # Check for common passwords
        common_passwords = ['password', '123456', 'password123', 'admin', 'hospital']
        if password.lower() in common_passwords:
            errors.append(
                ValidationError(
                    'This password is too common.',
                    code='password_too_common'
                )
            )
        
        # Check if password contains user information
        if user:
            user_attrs = [
                getattr(user, 'so_dien_thoai', ''),
                getattr(user, 'email', '').split('@')[0] if hasattr(user, 'email') else '',
            ]
            for attr in user_attrs:
                if attr and attr.lower() in password.lower():
                    errors.append(
                        ValidationError(
                            'Password cannot contain your personal information.',
                            code='password_user_attribute'
                        )
                    )
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        return (
            f"Your password must contain at least {self.min_length} characters, "
            "including uppercase and lowercase letters, digits, and special characters."
        )


# Business Rule Validators
class AppointmentTimeValidator:
    """
    Validator for appointment times.
    Ensures appointments are within business rules.
    """
    
    def __init__(self, min_advance_hours: int = 2, max_advance_days: int = 30):
        self.min_advance_hours = min_advance_hours
        self.max_advance_days = max_advance_days
    
    def validate(self, appointment_datetime: datetime):
        now = timezone.now()
        
        # Check minimum advance booking
        min_time = now + timedelta(hours=self.min_advance_hours)
        if appointment_datetime < min_time:
            raise ValidationError(
                f'Appointments must be booked at least {self.min_advance_hours} hours in advance.',
                code='appointment_too_soon'
            )
        
        # Check maximum advance booking
        max_time = now + timedelta(days=self.max_advance_days)
        if appointment_datetime > max_time:
            raise ValidationError(
                f'Appointments cannot be booked more than {self.max_advance_days} days in advance.',
                code='appointment_too_far'
            )
        
        # Check if date is not in the past
        if appointment_datetime.date() < now.date():
            raise ValidationError(
                'Cannot book appointments in the past.',
                code='appointment_past'
            )
        
        # Check working hours
        appointment_time = appointment_datetime.time()
        if appointment_time < time(8, 0) or appointment_time > time(20, 0):
            raise ValidationError(
                'Appointments must be between 8:00 AM and 8:00 PM.',
                code='appointment_outside_hours'
            )
        
        # Check if not on Sunday (optional)
        if appointment_datetime.weekday() == 6:  # Sunday
            raise ValidationError(
                'Appointments are not available on Sundays.',
                code='appointment_sunday'
            )


class PaymentAmountValidator:
    """Validator for payment amounts."""
    
    def __init__(self, min_amount: Decimal = Decimal('0'), 
                 max_amount: Decimal = Decimal('1000000000')):
        self.min_amount = min_amount
        self.max_amount = max_amount
    
    def validate(self, amount):
        if isinstance(amount, (int, float)):
            amount = Decimal(str(amount))
        
        if amount <= self.min_amount:
            raise ValidationError(
                f'Amount must be greater than {self.min_amount}.',
                code='amount_too_low'
            )
        
        if amount > self.max_amount:
            raise ValidationError(
                f'Amount cannot exceed {self.max_amount}.',
                code='amount_too_high'
            )


# Composite Validators
class PatientDataValidator:
    """
    Composite validator for patient data.
    Validates all patient-related fields.
    """
    
    def __init__(self):
        self.phone_validator = VietnamesePhoneValidator()
        self.id_validator = VietnameseIDValidator()
        self.insurance_validator = HealthInsuranceNumberValidator()
        self.age_validator = AgeValidator(min_age=0, max_age=120)
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate patient data.
        
        Args:
            data: Patient data dictionary
            
        Returns:
            Validated data
            
        Raises:
            ValidationError: If validation fails
        """
        errors = {}
        
        # Validate phone number
        if 'so_dien_thoai' in data:
            try:
                self.phone_validator(data['so_dien_thoai'])
            except ValidationError as e:
                errors['so_dien_thoai'] = e.messages
        
        # Validate ID number
        if 'cmnd_cccd' in data and data['cmnd_cccd']:
            try:
                self.id_validator(data['cmnd_cccd'])
            except ValidationError as e:
                errors['cmnd_cccd'] = e.messages
        
        # Validate insurance number
        if 'so_bhyt' in data and data['so_bhyt']:
            try:
                self.insurance_validator(data['so_bhyt'])
            except ValidationError as e:
                errors['so_bhyt'] = e.messages
        
        # Validate birth date
        if 'ngay_sinh' in data:
            try:
                self.age_validator(data['ngay_sinh'])
            except ValidationError as e:
                errors['ngay_sinh'] = e.messages
        
        # Validate email format
        if 'email' in data and data['email']:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                errors['email'] = ['Enter a valid email address.']
        
        # Validate gender
        if 'gioi_tinh' in data:
            valid_genders = ['Nam', 'Nữ', 'Khác']
            if data['gioi_tinh'] not in valid_genders:
                errors['gioi_tinh'] = [f'Gender must be one of: {", ".join(valid_genders)}']
        
        if errors:
            raise ValidationError(errors)
        
        return data


class DoctorScheduleValidator:
    """
    Validator for doctor schedules.
    Ensures no conflicts and valid working hours.
    """
    
    def validate(self, schedule_data: Dict[str, Any], existing_schedules: List = None):
        """
        Validate doctor schedule.
        
        Args:
            schedule_data: Schedule data to validate
            existing_schedules: List of existing schedules to check conflicts
            
        Raises:
            ValidationError: If validation fails
        """
        errors = {}
        
        # Validate date
        work_date = schedule_data.get('ngay_lam_viec')
        if isinstance(work_date, str):
            work_date = datetime.strptime(work_date, '%Y-%m-%d').date()
        
        if work_date < timezone.now().date():
            errors['ngay_lam_viec'] = ['Cannot create schedule for past dates.']
        
        # Validate time range
        start_time = schedule_data.get('gio_bat_dau')
        end_time = schedule_data.get('gio_ket_thuc')
        
        if isinstance(start_time, str):
            start_time = datetime.strptime(start_time, '%H:%M:%S').time()
        if isinstance(end_time, str):
            end_time = datetime.strptime(end_time, '%H:%M:%S').time()
        
        if start_time >= end_time:
            errors['gio_ket_thuc'] = ['End time must be after start time.']
        
        # Check working hours
        if start_time < time(6, 0) or end_time > time(22, 0):
            errors['gio_bat_dau'] = ['Schedule must be within 6:00 AM - 10:00 PM.']
        
        # Check for conflicts with existing schedules
        if existing_schedules:
            for existing in existing_schedules:
                if (existing['ngay_lam_viec'] == work_date and
                    existing['ma_bac_si'] == schedule_data.get('ma_bac_si')):
                    
                    # Check time overlap
                    existing_start = existing['gio_bat_dau']
                    existing_end = existing['gio_ket_thuc']
                    
                    if (start_time < existing_end and end_time > existing_start):
                        errors['gio_bat_dau'] = [
                            f'Schedule conflicts with existing schedule '
                            f'({existing_start} - {existing_end}).'
                        ]
        
        # Validate slot count
        slot_count = schedule_data.get('so_luong_kham', 0)
        if slot_count < 1 or slot_count > 100:
            errors['so_luong_kham'] = ['Slot count must be between 1 and 100.']
        
        if errors:
            raise ValidationError(errors)
