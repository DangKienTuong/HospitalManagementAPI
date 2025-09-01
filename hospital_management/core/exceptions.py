"""
Custom exception handling for the Hospital Management System.
Provides structured error responses and centralized exception management.
"""

from typing import Dict, Any, Optional, List
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from django.http import Http404
import logging
import traceback

logger = logging.getLogger(__name__)


class BaseApplicationException(APIException):
    """
    Base exception class for application-specific exceptions.
    All custom exceptions should inherit from this class.
    """
    
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'An error occurred'
    default_code = 'error'
    
    def __init__(self, detail: Any = None, code: str = None, 
                 context: Optional[Dict[str, Any]] = None):
        """
        Initialize exception with additional context.
        
        Args:
            detail: Error detail message
            code: Error code for client identification
            context: Additional context information
        """
        super().__init__(detail or self.default_detail, code or self.default_code)
        self.context = context or {}


# Business Logic Exceptions
class BusinessLogicException(BaseApplicationException):
    """Exception for business rule violations."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Business rule violation'
    default_code = 'business_error'


class ResourceNotFoundException(BaseApplicationException):
    """Exception for resource not found."""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found'
    default_code = 'not_found'


class DuplicateResourceException(BaseApplicationException):
    """Exception for duplicate resource creation."""
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Resource already exists'
    default_code = 'duplicate'


class InvalidOperationException(BaseApplicationException):
    """Exception for invalid operations."""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid operation'
    default_code = 'invalid_operation'


# Authentication & Authorization Exceptions
class AuthenticationException(BaseApplicationException):
    """Exception for authentication failures."""
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Authentication failed'
    default_code = 'authentication_failed'


class AuthorizationException(BaseApplicationException):
    """Exception for authorization failures."""
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Permission denied'
    default_code = 'permission_denied'


class TokenExpiredException(AuthenticationException):
    """Exception for expired tokens."""
    default_detail = 'Token has expired'
    default_code = 'token_expired'


class InvalidTokenException(AuthenticationException):
    """Exception for invalid tokens."""
    default_detail = 'Invalid token'
    default_code = 'invalid_token'


# Validation Exceptions
class ValidationException(BaseApplicationException):
    """Exception for validation errors."""
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Validation failed'
    default_code = 'validation_error'
    
    def __init__(self, errors: Dict[str, List[str]], code: str = None):
        """
        Initialize validation exception with field errors.
        
        Args:
            errors: Dictionary of field errors
            code: Error code
        """
        super().__init__(detail=errors, code=code)
        self.field_errors = errors


class InvalidInputException(ValidationException):
    """Exception for invalid input data."""
    default_detail = 'Invalid input data'
    default_code = 'invalid_input'


# External Service Exceptions
class ExternalServiceException(BaseApplicationException):
    """Exception for external service failures."""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'External service unavailable'
    default_code = 'external_service_error'


class PaymentGatewayException(ExternalServiceException):
    """Exception for payment gateway failures."""
    default_detail = 'Payment gateway error'
    default_code = 'payment_gateway_error'


class EmailServiceException(ExternalServiceException):
    """Exception for email service failures."""
    default_detail = 'Email service error'
    default_code = 'email_service_error'


class SMSServiceException(ExternalServiceException):
    """Exception for SMS service failures."""
    default_detail = 'SMS service error'
    default_code = 'sms_service_error'


# Database Exceptions
class DatabaseException(BaseApplicationException):
    """Exception for database operations."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = 'Database error'
    default_code = 'database_error'


class TransactionException(DatabaseException):
    """Exception for transaction failures."""
    default_detail = 'Transaction failed'
    default_code = 'transaction_error'


# Rate Limiting Exception
class RateLimitExceededException(BaseApplicationException):
    """Exception for rate limit exceeded."""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'Rate limit exceeded'
    default_code = 'rate_limit_exceeded'


def custom_exception_handler(exc, context):
    """
    Custom exception handler for REST framework.
    Provides consistent error response format.
    
    Args:
        exc: Exception instance
        context: Context dictionary
        
    Returns:
        Response object with error details
    """
    # Get the standard error response
    response = exception_handler(exc, context)
    
    # Get request information
    request = context.get('request')
    view = context.get('view')
    
    # Log the exception
    if request:
        logger.error(
            f"Exception in {view.__class__.__name__ if view else 'Unknown'}: "
            f"{request.method} {request.path}",
            exc_info=exc,
            extra={
                'request_id': getattr(request, 'id', None),
                'user': getattr(request, 'user', None),
                'data': getattr(request, 'data', None),
            }
        )
    
    # Handle Django exceptions
    if isinstance(exc, Http404):
        exc = ResourceNotFoundException('Resource not found')
    elif isinstance(exc, DjangoValidationError):
        exc = ValidationException(exc.message_dict if hasattr(exc, 'message_dict') else {'detail': str(exc)})
    elif isinstance(exc, IntegrityError):
        exc = DuplicateResourceException('Data integrity violation')
    
    # Format response for custom exceptions
    if isinstance(exc, BaseApplicationException):
        error_response = {
            'success': False,
            'error': {
                'code': exc.default_code,
                'message': str(exc.detail),
                'type': exc.__class__.__name__,
            }
        }
        
        # Add field errors for validation exceptions
        if isinstance(exc, ValidationException) and hasattr(exc, 'field_errors'):
            error_response['error']['fields'] = exc.field_errors
        
        # Add context if available
        if exc.context:
            error_response['error']['context'] = exc.context
        
        # Add request ID for tracking
        if request and hasattr(request, 'id'):
            error_response['error']['request_id'] = request.id
        
        # Add debug information in development
        from django.conf import settings
        if settings.DEBUG:
            error_response['error']['debug'] = {
                'traceback': traceback.format_exc(),
                'view': view.__class__.__name__ if view else None,
                'path': request.path if request else None,
                'method': request.method if request else None,
            }
        
        if response:
            response.data = error_response
        else:
            from rest_framework.response import Response
            response = Response(error_response, status=exc.status_code)
    
    # Handle standard DRF exceptions
    elif response is not None:
        error_response = {
            'success': False,
            'error': {
                'code': getattr(exc, 'default_code', 'error'),
                'message': response.data.get('detail', str(exc)) if isinstance(response.data, dict) else str(response.data),
                'type': exc.__class__.__name__,
            }
        }
        
        if request and hasattr(request, 'id'):
            error_response['error']['request_id'] = request.id
        
        response.data = error_response
    
    # Handle unexpected exceptions
    else:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        
        from rest_framework.response import Response
        error_response = {
            'success': False,
            'error': {
                'code': 'internal_error',
                'message': 'An unexpected error occurred',
                'type': 'InternalServerError',
            }
        }
        
        if request and hasattr(request, 'id'):
            error_response['error']['request_id'] = request.id
        
        from django.conf import settings
        if settings.DEBUG:
            error_response['error']['debug'] = {
                'exception': str(exc),
                'traceback': traceback.format_exc(),
            }
        
        response = Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response


class ExceptionMiddleware:
    """
    Middleware for handling exceptions at the application level.
    Provides centralized exception logging and monitoring.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
        except Exception as e:
            logger.error(
                f"Unhandled exception in middleware: {e}",
                exc_info=True,
                extra={
                    'request_path': request.path,
                    'request_method': request.method,
                    'user': getattr(request, 'user', None),
                }
            )
            
            # Send to monitoring service (e.g., Sentry)
            self._send_to_monitoring(e, request)
            
            # Return error response
            from django.http import JsonResponse
            return JsonResponse({
                'success': False,
                'error': {
                    'code': 'internal_error',
                    'message': 'An unexpected error occurred',
                    'request_id': getattr(request, 'id', None),
                }
            }, status=500)
        
        return response
    
    def _send_to_monitoring(self, exception, request):
        """Send exception to monitoring service."""
        try:
            # Integrate with Sentry or other monitoring service
            from django.conf import settings
            if hasattr(settings, 'SENTRY_DSN') and settings.SENTRY_DSN:
                import sentry_sdk
                sentry_sdk.capture_exception(exception)
        except Exception:
            pass  # Don't let monitoring failures break the application
