"""
URL configuration for health check endpoints.
"""

from django.urls import path
from .health_checks import (
    health_check,
    health_check_detailed,
    liveness_probe,
    readiness_probe,
    metrics_endpoint
)

app_name = 'health'

urlpatterns = [
    # Basic health check
    path('', health_check, name='health-check'),
    
    # Detailed health check with metrics
    path('detailed/', health_check_detailed, name='health-check-detailed'),
    
    # Kubernetes probes
    path('live/', liveness_probe, name='liveness-probe'),
    path('ready/', readiness_probe, name='readiness-probe'),
    
    # Metrics endpoint
    path('metrics/', metrics_endpoint, name='metrics'),
]
