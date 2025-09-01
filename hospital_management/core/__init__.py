"""
Core module for Hospital Management System.
Contains base classes, interfaces, utilities, and architectural components.
"""

from .base import *
from .exceptions import *
from .interfaces import *
from .mixins import *
from .decorators import *
from .dependency_injection import DependencyContainer, get_service, register_services
from .validators import *
from .pagination import *
from .logging_config import logging_service, get_logger, setup_logging_config
from .api_docs import *

# Initialize core services
__all__ = [
    # Base components
    'BaseModel', 'BaseRepository', 'BaseService', 'BaseViewSet',
    
    # Exceptions
    'ValidationError', 'AuthenticationError', 'AuthorizationError',
    'ResourceNotFoundError', 'BusinessLogicError', 'ExternalServiceError',
    
    # Interfaces
    'RepositoryInterface', 'ServiceInterface', 'CacheInterface',
    
    # Mixins
    'TimestampMixin', 'SoftDeleteMixin', 'AuditTrailMixin',
    'CacheableMixin', 'BulkOperationMixin', 'SearchableMixin',
    'LoggingMixin', 'CustomPaginationMixin',
    
    # Decorators
    'timing_decorator', 'retry_decorator', 'cache_result',
    'transactional', 'validate_request', 'audit_log',
    'rate_limit', 'permission_required',
    
    # Dependency Injection
    'DependencyContainer', 'get_service', 'register_services',
    
    # Validators
    'PasswordValidator', 'PhoneNumberValidator', 'IdentityCardValidator',
    'HealthInsuranceValidator', 'MedicalDataValidator', 'BusinessRuleValidator',
    'DataConsistencyValidator', 'InputSanitizerValidator', 'JSONSchemaValidator',
    
    # Pagination
    'CustomPageNumberPagination', 'OptimizedLimitOffsetPagination',
    'CursorBasedPagination', 'SmartPagination', 'SearchResultsPagination',
    'DashboardPagination', 'InfinitePagination', 'PerformancePagination',
    'get_pagination_class',
    
    # Logging
    'logging_service', 'get_logger', 'setup_logging_config',
    
    # API Documentation
    'AuthenticationSchemas', 'PatientSchemas', 'MedicalSchemas',
    'AppointmentSchemas', 'get_custom_schema_class', 'API_INFO',
    'SWAGGER_SETTINGS', 'COMMON_RESPONSES',
]
