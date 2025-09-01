"""
Custom middleware for cross-cutting concerns.
"""

import time
import json
import logging
import uuid
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.db import connection
from rest_framework import status
from .exceptions import (
    BusinessLogicException,
    ValidationException,
    AuthorizationException,
    ResourceNotFoundException,
    ConcurrencyException,
    ExternalServiceException
)


class RequestLoggingMiddleware(MiddlewareMixin):
    """Middleware for logging HTTP requests and responses."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('core.middleware')
    
    def process_request(self, request):
        """Log incoming request."""
        request.id = str(uuid.uuid4())
        request.start_time = time.time()
        
        # Log request details
        self.logger.info(
            f"Request started",
            extra={
                'request_id': request.id,
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if request.user.is_authenticated else 'Anonymous',
                'ip': self.get_client_ip(request),
            }
        )
        
        return None
    
    def process_response(self, request, response):
        """Log response details."""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            self.logger.info(
                f"Request completed",
                extra={
                    'request_id': getattr(request, 'id', 'unknown'),
                    'status_code': response.status_code,
                    'duration': f"{duration:.3f}s",
                    'user': str(request.user) if request.user.is_authenticated else 'Anonymous',
                }
            )
        
        # Add request ID to response headers
        if hasattr(request, 'id'):
            response['X-Request-ID'] = request.id
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ExceptionHandlingMiddleware(MiddlewareMixin):
    """Middleware for centralized exception handling."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('core.exceptions')
    
    def process_exception(self, request, exception):
        """Handle exceptions and return appropriate responses."""
        request_id = getattr(request, 'id', 'unknown')
        
        # Log the exception
        self.logger.error(
            f"Exception occurred",
            extra={
                'request_id': request_id,
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'path': request.path,
                'method': request.method,
                'user': str(request.user) if request.user.is_authenticated else 'Anonymous',
            },
            exc_info=True
        )
        
        # Map custom exceptions to HTTP responses
        if isinstance(exception, ValidationException):
            return JsonResponse({
                'error': 'Validation Error',
                'message': str(exception),
                'request_id': request_id,
            }, status=status.HTTP_400_BAD_REQUEST)
        
        elif isinstance(exception, AuthorizationException):
            return JsonResponse({
                'error': 'Authorization Error',
                'message': str(exception),
                'request_id': request_id,
            }, status=status.HTTP_403_FORBIDDEN)
        
        elif isinstance(exception, ResourceNotFoundException):
            return JsonResponse({
                'error': 'Resource Not Found',
                'message': str(exception),
                'request_id': request_id,
            }, status=status.HTTP_404_NOT_FOUND)
        
        elif isinstance(exception, BusinessLogicException):
            return JsonResponse({
                'error': 'Business Logic Error',
                'message': str(exception),
                'request_id': request_id,
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        elif isinstance(exception, ConcurrencyException):
            return JsonResponse({
                'error': 'Concurrency Error',
                'message': str(exception),
                'request_id': request_id,
            }, status=status.HTTP_409_CONFLICT)
        
        elif isinstance(exception, ExternalServiceException):
            return JsonResponse({
                'error': 'External Service Error',
                'message': str(exception),
                'request_id': request_id,
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # For other exceptions, return generic error in production
        from django.conf import settings
        if not settings.DEBUG:
            return JsonResponse({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred',
                'request_id': request_id,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # In debug mode, let Django handle the exception
        return None


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Middleware for monitoring application performance."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('core.performance')
    
    def process_request(self, request):
        """Start performance monitoring."""
        request._db_queries_start = len(connection.queries)
        return None
    
    def process_response(self, request, response):
        """Log performance metrics."""
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Count database queries
            db_queries = 0
            if hasattr(request, '_db_queries_start'):
                db_queries = len(connection.queries) - request._db_queries_start
            
            # Log if request is slow
            if duration > 1.0:  # Log requests taking more than 1 second
                self.logger.warning(
                    f"Slow request detected",
                    extra={
                        'request_id': getattr(request, 'id', 'unknown'),
                        'path': request.path,
                        'duration': f"{duration:.3f}s",
                        'db_queries': db_queries,
                        'method': request.method,
                    }
                )
            
            # Add performance headers
            response['X-Response-Time'] = f"{duration:.3f}"
            response['X-DB-Queries'] = str(db_queries)
        
        return response


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Middleware to add security headers to responses."""
    
    def process_response(self, request, response):
        """Add security headers."""
        # Content Security Policy
        response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline';"
        
        # Additional security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Remove server header
        if 'Server' in response:
            del response['Server']
        
        return response


class RequestContextMiddleware(MiddlewareMixin):
    """Middleware to add request context for logging and tracing."""
    
    def process_request(self, request):
        """Add context to request."""
        # Add user context
        if request.user.is_authenticated:
            request.context = {
                'user_id': request.user.ma_nguoi_dung,
                'user_role': request.user.vai_tro,
                'session_id': request.session.session_key,
            }
        else:
            request.context = {
                'user_id': None,
                'user_role': 'anonymous',
                'session_id': request.session.session_key,
            }
        
        # Add request metadata
        request.context.update({
            'ip_address': self.get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'request_id': getattr(request, 'id', str(uuid.uuid4())),
        })
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class MaintenanceModeMiddleware(MiddlewareMixin):
    """Middleware to handle maintenance mode."""
    
    def process_request(self, request):
        """Check if system is in maintenance mode."""
        from django.conf import settings
        
        if getattr(settings, 'MAINTENANCE_MODE', False):
            # Allow admin access
            if request.path.startswith('/admin/'):
                return None
            
            # Allow health check endpoints
            if request.path in ['/health/', '/api/health/']:
                return None
            
            return JsonResponse({
                'error': 'Maintenance Mode',
                'message': 'System is currently under maintenance. Please try again later.',
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return None
