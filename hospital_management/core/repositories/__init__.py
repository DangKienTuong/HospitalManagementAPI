"""
Repository layer for data access abstraction.
Implements Repository Pattern for clean separation of concerns.
"""

from .base import BaseRepository, CachedRepository, IRepository
from .user_repository import UserRepository
from .medical_repository import (
    MedicalFacilityRepository,
    DoctorRepository,
    SpecialtyRepository,
    ServiceRepository
)
from .appointment_repository import (
    AppointmentRepository,
    ScheduleRepository,
    TeleconsultationRepository
)
from .payment_repository import PaymentRepository

__all__ = [
    'BaseRepository',
    'CachedRepository',
    'IRepository',
    'UserRepository',
    'MedicalFacilityRepository',
    'DoctorRepository',
    'SpecialtyRepository',
    'ServiceRepository',
    'AppointmentRepository',
    'ScheduleRepository',
    'TeleconsultationRepository',
    'PaymentRepository',
]
