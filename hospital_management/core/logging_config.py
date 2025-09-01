"""
Comprehensive logging configuration for Hospital Management System.
Provides structured logging with multiple handlers and formatters.
"""

import os
import logging
import logging.config
from datetime import datetime
from typing import Dict, Any
import json
from pythonjsonlogger import jsonlogger


class RequestIdFilter(logging.Filter):
    """
    Filter to add request ID to log records.
    """
    
    def filter(self, record):
        # Try to get request ID from thread local storage
        import threading
        local = threading.local()
        record.request_id = getattr(local, 'request_id', 'NO_REQUEST_ID')
        return True


class UserContextFilter(logging.Filter):
    """
    Filter to add user context to log records.
    """
    
    def filter(self, record):
        import threading
        local = threading.local()
        record.user_id = getattr(local, 'user_id', None)
        record.user_role = getattr(local, 'user_role', None)
        return True


class HealthCheckFilter(logging.Filter):
    """
    Filter to exclude health check logs.
    """
    
    def filter(self, record):
        # Skip health check endpoint logs to reduce noise
        message = record.getMessage()
        return '/health/' not in message and '/api/health' not in message


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """
    Custom JSON formatter for structured logging.
    """
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add custom fields
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        
        # Add request context if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        
        # Add user context if available
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        if hasattr(record, 'user_role'):
            log_record['user_role'] = record.user_role
        
        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in log_record and not key.startswith('_'):
                log_record[key] = value


def setup_logging_config() -> Dict[str, Any]:
    """
    Setup comprehensive logging configuration.
    
    Returns:
        Logging configuration dictionary
    """
    from django.conf import settings
    
    # Get log level from settings
    log_level = getattr(settings, 'LOG_LEVEL', 'INFO')
    log_file_path = getattr(settings, 'LOG_FILE_PATH', '/var/log/hospital_management/app.log')
    
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except:
            # Fall back to current directory if can't create log dir
            log_file_path = 'app.log'
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
            'json': {
                '()': CustomJsonFormatter,
                'format': '%(timestamp)s %(level)s %(name)s %(message)s',
            },
            'detailed': {
                'format': '[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] '
                         '[%(request_id)s] %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        
        'filters': {
            'request_id': {
                '()': RequestIdFilter,
            },
            'user_context': {
                '()': UserContextFilter,
            },
            'health_check': {
                '()': HealthCheckFilter,
            },
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            },
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
                'filters': ['request_id', 'user_context', 'health_check'],
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_file_path,
                'maxBytes': 1024 * 1024 * 50,  # 50MB
                'backupCount': 5,
                'formatter': 'json',
                'filters': ['request_id', 'user_context'],
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_file_path.replace('.log', '_error.log'),
                'maxBytes': 1024 * 1024 * 50,  # 50MB
                'backupCount': 5,
                'formatter': 'detailed',
                'filters': ['request_id', 'user_context'],
            },
            'security_file': {
                'level': 'WARNING',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_file_path.replace('.log', '_security.log'),
                'maxBytes': 1024 * 1024 * 20,  # 20MB
                'backupCount': 10,
                'formatter': 'json',
            },
            'performance_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_file_path.replace('.log', '_performance.log'),
                'maxBytes': 1024 * 1024 * 50,  # 50MB
                'backupCount': 3,
                'formatter': 'json',
            },
            'audit_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': log_file_path.replace('.log', '_audit.log'),
                'maxBytes': 1024 * 1024 * 100,  # 100MB
                'backupCount': 30,  # Keep 30 days of audit logs
                'formatter': 'json',
            },
            'mail_admins': {
                'level': 'ERROR',
                'class': 'django.utils.log.AdminEmailHandler',
                'filters': ['require_debug_false'],
                'formatter': 'verbose',
            },
        },
        
        'loggers': {
            # Django loggers
            'django': {
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': False,
            },
            'django.request': {
                'handlers': ['error_file', 'mail_admins'],
                'level': 'ERROR',
                'propagate': False,
            },
            'django.security': {
                'handlers': ['security_file', 'console'],
                'level': 'WARNING',
                'propagate': False,
            },
            'django.db.backends': {
                'handlers': ['performance_file'],
                'level': 'DEBUG' if settings.DEBUG else 'INFO',
                'propagate': False,
            },
            
            # Application loggers
            'core': {
                'handlers': ['console', 'file', 'error_file'],
                'level': log_level,
                'propagate': False,
            },
            'authentication': {
                'handlers': ['console', 'file', 'security_file'],
                'level': log_level,
                'propagate': False,
            },
            'medical': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False,
            },
            'appointments': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False,
            },
            'payments': {
                'handlers': ['console', 'file', 'audit_file'],
                'level': log_level,
                'propagate': False,
            },
            
            # Audit logger
            'audit': {
                'handlers': ['audit_file', 'console'],
                'level': 'INFO',
                'propagate': False,
            },
            
            # Performance logger
            'performance': {
                'handlers': ['performance_file'],
                'level': 'INFO',
                'propagate': False,
            },
            
            # Security logger
            'security': {
                'handlers': ['security_file', 'console', 'mail_admins'],
                'level': 'WARNING',
                'propagate': False,
            },
        },
        
        'root': {
            'handlers': ['console', 'file'],
            'level': log_level,
        },
    }
    
    return config


class LoggerMixin:
    """
    Mixin to add logger to classes.
    """
    
    @property
    def logger(self):
        """Get logger for class."""
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(
                f"{self.__class__.__module__}.{self.__class__.__name__}"
            )
        return self._logger


class AuditLogger:
    """
    Specialized logger for audit trails.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('audit')
    
    def log_action(self, action: str, user_id: int, details: Dict[str, Any]):
        """
        Log an audit action.
        
        Args:
            action: Action performed
            user_id: User who performed action
            details: Additional details
        """
        self.logger.info(
            f"AUDIT: {action}",
            extra={
                'action': action,
                'user_id': user_id,
                'details': details,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    
    def log_login(self, user_id: int, ip_address: str, success: bool):
        """Log login attempt."""
        self.log_action(
            'LOGIN' if success else 'LOGIN_FAILED',
            user_id,
            {'ip_address': ip_address, 'success': success}
        )
    
    def log_data_access(self, user_id: int, resource: str, action: str):
        """Log data access."""
        self.log_action(
            f'DATA_ACCESS_{action.upper()}',
            user_id,
            {'resource': resource, 'action': action}
        )
    
    def log_payment(self, user_id: int, payment_id: int, amount: float, status: str):
        """Log payment transaction."""
        self.log_action(
            'PAYMENT',
            user_id,
            {
                'payment_id': payment_id,
                'amount': amount,
                'status': status
            }
        )


class PerformanceLogger:
    """
    Specialized logger for performance monitoring.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('performance')
    
    def log_request(self, method: str, path: str, duration: float, 
                   status_code: int):
        """
        Log API request performance.
        
        Args:
            method: HTTP method
            path: Request path
            duration: Request duration in ms
            status_code: Response status code
        """
        self.logger.info(
            f"REQUEST: {method} {path}",
            extra={
                'method': method,
                'path': path,
                'duration_ms': duration,
                'status_code': status_code
            }
        )
    
    def log_database_query(self, query: str, duration: float):
        """
        Log database query performance.
        
        Args:
            query: SQL query
            duration: Query duration in ms
        """
        self.logger.info(
            "DB_QUERY",
            extra={
                'query': query[:500],  # Truncate long queries
                'duration_ms': duration
            }
        )
    
    def log_cache_operation(self, operation: str, key: str, hit: bool, 
                           duration: float):
        """
        Log cache operation.
        
        Args:
            operation: Cache operation (get, set, delete)
            key: Cache key
            hit: Cache hit/miss
            duration: Operation duration in ms
        """
        self.logger.info(
            f"CACHE_{operation.upper()}",
            extra={
                'operation': operation,
                'key': key,
                'hit': hit,
                'duration_ms': duration
            }
        )


class SecurityLogger:
    """
    Specialized logger for security events.
    """
    
    def __init__(self):
        self.logger = logging.getLogger('security')
    
    def log_authentication_failure(self, username: str, ip_address: str, 
                                   reason: str):
        """Log authentication failure."""
        self.logger.warning(
            f"AUTH_FAILURE: {username}",
            extra={
                'username': username,
                'ip_address': ip_address,
                'reason': reason
            }
        )
    
    def log_authorization_failure(self, user_id: int, resource: str, 
                                  action: str):
        """Log authorization failure."""
        self.logger.warning(
            f"AUTHZ_FAILURE: User {user_id} denied {action} on {resource}",
            extra={
                'user_id': user_id,
                'resource': resource,
                'action': action
            }
        )
    
    def log_suspicious_activity(self, user_id: Optional[int], ip_address: str, 
                               activity: str):
        """Log suspicious activity."""
        self.logger.warning(
            f"SUSPICIOUS: {activity}",
            extra={
                'user_id': user_id,
                'ip_address': ip_address,
                'activity': activity
            }
        )
    
    def log_rate_limit_exceeded(self, ip_address: str, endpoint: str):
        """Log rate limit exceeded."""
        self.logger.warning(
            f"RATE_LIMIT: {endpoint}",
            extra={
                'ip_address': ip_address,
                'endpoint': endpoint
            }
        )


# Create global logger instances
audit_logger = AuditLogger()
performance_logger = PerformanceLogger()
security_logger = SecurityLogger()
