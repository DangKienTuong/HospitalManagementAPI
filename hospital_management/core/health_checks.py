"""
Health check endpoints and system metrics for Hospital Management System.
Provides comprehensive health monitoring and status reporting.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import psutil
import logging
import os

logger = logging.getLogger(__name__)


class HealthCheckService:
    """
    Service for performing health checks on various system components.
    """
    
    def __init__(self):
        self.checks = {
            'database': self.check_database,
            'cache': self.check_cache,
            'disk': self.check_disk_space,
            'memory': self.check_memory,
            'external_services': self.check_external_services,
        }
    
    def get_health_status(self, detailed: bool = False) -> Dict[str, Any]:
        """
        Get overall health status of the system.
        
        Args:
            detailed: Include detailed metrics
            
        Returns:
            Health status dictionary
        """
        start_time = timezone.now()
        health_status = {
            'status': 'healthy',
            'timestamp': start_time.isoformat(),
            'version': getattr(settings, 'APP_VERSION', '1.0.0'),
            'environment': getattr(settings, 'ENVIRONMENT', 'unknown'),
            'checks': {}
        }
        
        failed_checks = []
        warning_checks = []
        
        for check_name, check_func in self.checks.items():
            try:
                check_result = check_func()
                health_status['checks'][check_name] = check_result
                
                if check_result['status'] == 'unhealthy':
                    failed_checks.append(check_name)
                elif check_result['status'] == 'degraded':
                    warning_checks.append(check_name)
                    
            except Exception as e:
                logger.error(f"Health check {check_name} failed: {str(e)}")
                health_status['checks'][check_name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                failed_checks.append(check_name)
        
        # Determine overall status
        if failed_checks:
            health_status['status'] = 'unhealthy'
            health_status['failed_checks'] = failed_checks
        elif warning_checks:
            health_status['status'] = 'degraded'
            health_status['warning_checks'] = warning_checks
        
        # Add response time
        response_time = (timezone.now() - start_time).total_seconds() * 1000
        health_status['response_time_ms'] = response_time
        
        # Add detailed metrics if requested
        if detailed:
            health_status['metrics'] = self.get_system_metrics()
        
        return health_status
    
    def check_database(self) -> Dict[str, Any]:
        """
        Check database connectivity and performance.
        
        Returns:
            Database health status
        """
        try:
            start_time = timezone.now()
            
            # Test connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            # Calculate response time
            response_time = (timezone.now() - start_time).total_seconds() * 1000
            
            # Check connection pool
            conn_info = {
                'vendor': connection.vendor,
                'is_usable': connection.is_usable(),
                'response_time_ms': response_time
            }
            
            # Determine status based on response time
            if response_time > 1000:  # More than 1 second
                status = 'degraded'
                message = 'Database response time is high'
            else:
                status = 'healthy'
                message = 'Database is responsive'
            
            return {
                'status': status,
                'message': message,
                'details': conn_info
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'message': 'Database connection failed',
                'error': str(e)
            }
    
    def check_cache(self) -> Dict[str, Any]:
        """
        Check cache service connectivity and performance.
        
        Returns:
            Cache health status
        """
        try:
            start_time = timezone.now()
            
            # Test cache operations
            test_key = 'health_check_test'
            test_value = timezone.now().isoformat()
            
            # Set value
            cache.set(test_key, test_value, 10)
            
            # Get value
            retrieved_value = cache.get(test_key)
            
            # Delete value
            cache.delete(test_key)
            
            # Calculate response time
            response_time = (timezone.now() - start_time).total_seconds() * 1000
            
            # Verify operations
            if retrieved_value != test_value:
                return {
                    'status': 'unhealthy',
                    'message': 'Cache operations failed',
                    'error': 'Value mismatch'
                }
            
            # Check response time
            if response_time > 100:  # More than 100ms
                status = 'degraded'
                message = 'Cache response time is high'
            else:
                status = 'healthy'
                message = 'Cache is responsive'
            
            return {
                'status': status,
                'message': message,
                'response_time_ms': response_time
            }
            
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'message': 'Cache service unavailable',
                'error': str(e)
            }
    
    def check_disk_space(self) -> Dict[str, Any]:
        """
        Check available disk space.
        
        Returns:
            Disk space health status
        """
        try:
            disk_usage = psutil.disk_usage('/')
            
            # Calculate percentage used
            percent_used = disk_usage.percent
            available_gb = disk_usage.free / (1024 ** 3)
            
            # Determine status
            if percent_used > 90:
                status = 'unhealthy'
                message = 'Critical: Disk space is running out'
            elif percent_used > 80:
                status = 'degraded'
                message = 'Warning: Low disk space'
            else:
                status = 'healthy'
                message = 'Disk space is adequate'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'percent_used': percent_used,
                    'available_gb': round(available_gb, 2),
                    'total_gb': round(disk_usage.total / (1024 ** 3), 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Disk space check failed: {str(e)}")
            return {
                'status': 'unknown',
                'message': 'Could not check disk space',
                'error': str(e)
            }
    
    def check_memory(self) -> Dict[str, Any]:
        """
        Check memory usage.
        
        Returns:
            Memory health status
        """
        try:
            memory = psutil.virtual_memory()
            
            # Calculate percentage used
            percent_used = memory.percent
            available_gb = memory.available / (1024 ** 3)
            
            # Determine status
            if percent_used > 90:
                status = 'unhealthy'
                message = 'Critical: Memory usage is very high'
            elif percent_used > 80:
                status = 'degraded'
                message = 'Warning: High memory usage'
            else:
                status = 'healthy'
                message = 'Memory usage is normal'
            
            return {
                'status': status,
                'message': message,
                'details': {
                    'percent_used': percent_used,
                    'available_gb': round(available_gb, 2),
                    'total_gb': round(memory.total / (1024 ** 3), 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Memory check failed: {str(e)}")
            return {
                'status': 'unknown',
                'message': 'Could not check memory',
                'error': str(e)
            }
    
    def check_external_services(self) -> Dict[str, Any]:
        """
        Check connectivity to external services.
        
        Returns:
            External services health status
        """
        services_status = {}
        all_healthy = True
        
        # Check email service
        if getattr(settings, 'EMAIL_HOST', None):
            try:
                from django.core.mail import connection as email_connection
                email_connection.open()
                email_connection.close()
                services_status['email'] = 'healthy'
            except Exception as e:
                services_status['email'] = 'unhealthy'
                all_healthy = False
                logger.error(f"Email service check failed: {str(e)}")
        
        # Check SMS service (if configured)
        # This would depend on your SMS provider
        
        # Check payment gateway (if configured)
        # This would depend on your payment provider
        
        return {
            'status': 'healthy' if all_healthy else 'degraded',
            'services': services_status
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get detailed system metrics.
        
        Returns:
            System metrics dictionary
        """
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process metrics
            process = psutil.Process(os.getpid())
            process_memory = process.memory_info()
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count
                },
                'memory': {
                    'percent': memory.percent,
                    'used_gb': round(memory.used / (1024 ** 3), 2),
                    'available_gb': round(memory.available / (1024 ** 3), 2)
                },
                'disk': {
                    'percent': disk.percent,
                    'used_gb': round(disk.used / (1024 ** 3), 2),
                    'free_gb': round(disk.free / (1024 ** 3), 2)
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'process': {
                    'memory_mb': round(process_memory.rss / (1024 ** 2), 2),
                    'cpu_percent': process.cpu_percent(),
                    'num_threads': process.num_threads()
                }
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {str(e)}")
            return {}


# Health check views
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Basic health check endpoint.
    Returns 200 if system is operational.
    """
    health_service = HealthCheckService()
    health_status = health_service.get_health_status(detailed=False)
    
    if health_status['status'] == 'unhealthy':
        return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    elif health_status['status'] == 'degraded':
        return Response(health_status, status=status.HTTP_200_OK)
    else:
        return Response(health_status, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_detailed(request):
    """
    Detailed health check endpoint.
    Returns comprehensive system metrics.
    """
    health_service = HealthCheckService()
    health_status = health_service.get_health_status(detailed=True)
    
    if health_status['status'] == 'unhealthy':
        return Response(health_status, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    else:
        return Response(health_status, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_probe(request):
    """
    Kubernetes liveness probe endpoint.
    Returns 200 if application is alive.
    """
    return Response({
        'status': 'alive',
        'timestamp': timezone.now().isoformat()
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_probe(request):
    """
    Kubernetes readiness probe endpoint.
    Returns 200 if application is ready to serve traffic.
    """
    health_service = HealthCheckService()
    
    # Quick checks for readiness
    try:
        # Check database
        db_check = health_service.check_database()
        if db_check['status'] == 'unhealthy':
            return Response({
                'status': 'not_ready',
                'reason': 'Database unavailable'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Check cache
        cache_check = health_service.check_cache()
        if cache_check['status'] == 'unhealthy':
            return Response({
                'status': 'not_ready',
                'reason': 'Cache unavailable'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        return Response({
            'status': 'ready',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Readiness probe failed: {str(e)}")
        return Response({
            'status': 'not_ready',
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class MetricsCollector:
    """
    Collects and aggregates system metrics.
    """
    
    def __init__(self):
        self.metrics = {
            'requests': {},
            'errors': {},
            'performance': {},
            'business': {}
        }
    
    def record_request(self, method: str, path: str, status_code: int, 
                      duration_ms: float):
        """Record API request metrics."""
        key = f"{method}:{path}"
        
        if key not in self.metrics['requests']:
            self.metrics['requests'][key] = {
                'count': 0,
                'total_time': 0,
                'status_codes': {}
            }
        
        self.metrics['requests'][key]['count'] += 1
        self.metrics['requests'][key]['total_time'] += duration_ms
        
        status_key = str(status_code)
        if status_key not in self.metrics['requests'][key]['status_codes']:
            self.metrics['requests'][key]['status_codes'][status_key] = 0
        self.metrics['requests'][key]['status_codes'][status_key] += 1
    
    def record_error(self, error_type: str, error_message: str):
        """Record error metrics."""
        if error_type not in self.metrics['errors']:
            self.metrics['errors'][error_type] = {
                'count': 0,
                'messages': []
            }
        
        self.metrics['errors'][error_type]['count'] += 1
        self.metrics['errors'][error_type]['messages'].append({
            'message': error_message,
            'timestamp': timezone.now().isoformat()
        })
        
        # Keep only last 100 error messages
        if len(self.metrics['errors'][error_type]['messages']) > 100:
            self.metrics['errors'][error_type]['messages'] = \
                self.metrics['errors'][error_type]['messages'][-100:]
    
    def record_business_metric(self, metric_name: str, value: Any):
        """Record business metrics."""
        if metric_name not in self.metrics['business']:
            self.metrics['business'][metric_name] = []
        
        self.metrics['business'][metric_name].append({
            'value': value,
            'timestamp': timezone.now().isoformat()
        })
        
        # Keep only last 1000 values
        if len(self.metrics['business'][metric_name]) > 1000:
            self.metrics['business'][metric_name] = \
                self.metrics['business'][metric_name][-1000:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics."""
        return self.metrics
    
    def reset_metrics(self):
        """Reset all metrics."""
        self.__init__()


# Global metrics collector
metrics_collector = MetricsCollector()


@api_view(['GET'])
@permission_classes([AllowAny])  # Should be restricted in production
def metrics_endpoint(request):
    """
    Metrics endpoint for monitoring systems.
    Returns Prometheus-compatible metrics.
    """
    metrics = metrics_collector.get_metrics()
    
    # Format metrics for Prometheus
    prometheus_metrics = []
    
    # Request metrics
    for endpoint, data in metrics['requests'].items():
        avg_time = data['total_time'] / data['count'] if data['count'] > 0 else 0
        prometheus_metrics.append(
            f'http_requests_total{{endpoint="{endpoint}"}} {data["count"]}'
        )
        prometheus_metrics.append(
            f'http_request_duration_ms{{endpoint="{endpoint}"}} {avg_time}'
        )
    
    # Error metrics
    for error_type, data in metrics['errors'].items():
        prometheus_metrics.append(
            f'errors_total{{type="{error_type}"}} {data["count"]}'
        )
    
    # Business metrics
    for metric_name, values in metrics['business'].items():
        if values:
            latest_value = values[-1]['value']
            prometheus_metrics.append(
                f'business_metric{{name="{metric_name}"}} {latest_value}'
            )
    
    return Response('\n'.join(prometheus_metrics), 
                   content_type='text/plain; version=0.0.4')
