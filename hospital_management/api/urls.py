"""
Main API URL configuration with versioning support.
"""

from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

urlpatterns = [
    # API v1
    path('v1/', include('api.v1.urls', namespace='v1')),
    
    # API v2 (future version)
    # path('v2/', include('api.v2.urls', namespace='v2')),
    
    # API Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Health checks
    path('health/', include('core.health_check_urls')),
]
