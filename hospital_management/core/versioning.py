"""
API versioning implementation for Hospital Management System.
Provides URL-based versioning with backward compatibility support.
"""

from rest_framework.versioning import URLPathVersioning
from rest_framework.exceptions import NotFound
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CustomURLPathVersioning(URLPathVersioning):
    """
    Custom URL path versioning with enhanced features.
    Supports version-specific serializers and views.
    """
    
    default_version = 'v1'
    allowed_versions = ['v1', 'v2']
    version_param = 'version'
    
    def determine_version(self, request, *args, **kwargs):
        """
        Determine API version from URL path.
        
        Args:
            request: HTTP request
            
        Returns:
            Version string
        """
        version = super().determine_version(request, *args, **kwargs)
        
        # Log API version usage for monitoring
        logger.debug(f"API request to version: {version} - {request.path}")
        
        # Set version in request for later use
        request.version = version
        request.versioning_scheme = self
        
        return version
    
    def reverse(self, viewname, args=None, kwargs=None, request=None, 
                format=None, **extra):
        """
        Reverse URL with version namespace.
        """
        if request and request.version:
            kwargs = kwargs or {}
            kwargs[self.version_param] = request.version
        
        return super().reverse(viewname, args, kwargs, request, format, **extra)


class VersionedSerializerMixin:
    """
    Mixin for version-specific serializer selection.
    Allows different serializers for different API versions.
    """
    
    # Map versions to serializer classes
    serializer_classes = {
        'v1': None,  # Set in subclass
        'v2': None,  # Set in subclass
    }
    
    def get_serializer_class(self):
        """
        Get serializer class based on API version.
        
        Returns:
            Serializer class for current version
        """
        version = getattr(self.request, 'version', 'v1')
        
        # Try to get version-specific serializer
        serializer_class = self.serializer_classes.get(version)
        
        # Fall back to default if not found
        if not serializer_class:
            serializer_class = self.serializer_classes.get('v1') or self.serializer_class
        
        logger.debug(f"Using serializer {serializer_class.__name__} for version {version}")
        return serializer_class


class VersionedViewMixin:
    """
    Mixin for version-specific view behavior.
    Allows different logic for different API versions.
    """
    
    def get_api_version(self) -> str:
        """
        Get current API version.
        
        Returns:
            Version string
        """
        return getattr(self.request, 'version', 'v1')
    
    def is_version(self, version: str) -> bool:
        """
        Check if current request is for specific version.
        
        Args:
            version: Version to check
            
        Returns:
            True if current version matches
        """
        return self.get_api_version() == version
    
    def version_dispatch(self, method_prefix: str, *args, **kwargs):
        """
        Dispatch to version-specific method.
        
        Args:
            method_prefix: Method name prefix
            
        Returns:
            Result from version-specific method
        """
        version = self.get_api_version()
        method_name = f"{method_prefix}_{version.replace('.', '_')}"
        
        # Try version-specific method
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(*args, **kwargs)
        
        # Fall back to default method
        if hasattr(self, method_prefix):
            method = getattr(self, method_prefix)
            return method(*args, **kwargs)
        
        raise NotFound(f"Method {method_prefix} not implemented for version {version}")


class APIVersionMiddleware:
    """
    Middleware for API version handling.
    Adds version information to response headers.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add API version to response headers
        if hasattr(request, 'version'):
            response['X-API-Version'] = request.version
            response['X-API-Deprecated'] = self._is_deprecated(request.version)
        
        return response
    
    def _is_deprecated(self, version: str) -> str:
        """
        Check if version is deprecated.
        
        Args:
            version: API version
            
        Returns:
            'true' if deprecated, 'false' otherwise
        """
        deprecated_versions = []  # Add deprecated versions here
        return 'true' if version in deprecated_versions else 'false'


class VersionedRouter:
    """
    URL router with API versioning support.
    Automatically creates versioned URL patterns.
    """
    
    def __init__(self, versions: list = None):
        """
        Initialize versioned router.
        
        Args:
            versions: List of supported versions
        """
        self.versions = versions or ['v1', 'v2']
        self.registrations = []
    
    def register(self, prefix: str, viewset, basename: str = None):
        """
        Register viewset for all versions.
        
        Args:
            prefix: URL prefix
            viewset: ViewSet class
            basename: Base name for URL names
        """
        self.registrations.append({
            'prefix': prefix,
            'viewset': viewset,
            'basename': basename or prefix
        })
    
    def get_urls(self):
        """
        Get versioned URL patterns.
        
        Returns:
            List of URL patterns
        """
        from django.urls import path, include
        from rest_framework.routers import DefaultRouter
        
        patterns = []
        
        for version in self.versions:
            router = DefaultRouter()
            
            for registration in self.registrations:
                # Check if viewset supports this version
                if self._supports_version(registration['viewset'], version):
                    router.register(
                        registration['prefix'],
                        registration['viewset'],
                        basename=f"{version}-{registration['basename']}"
                    )
            
            # Add version-specific URLs
            patterns.append(
                path(f'api/{version}/', include(router.urls))
            )
        
        return patterns
    
    def _supports_version(self, viewset, version: str) -> bool:
        """
        Check if viewset supports specific version.
        
        Args:
            viewset: ViewSet class
            version: API version
            
        Returns:
            True if version is supported
        """
        if hasattr(viewset, 'supported_versions'):
            return version in viewset.supported_versions
        return True  # Support all versions by default


def version_deprecated(deprecated_in: str, removed_in: str = None, 
                       alternative: str = None):
    """
    Decorator to mark API endpoint as deprecated.
    
    Args:
        deprecated_in: Version where deprecation started
        removed_in: Version where endpoint will be removed
        alternative: Alternative endpoint to use
    """
    def decorator(func):
        def wrapper(self, request, *args, **kwargs):
            # Add deprecation warning to response
            response = func(self, request, *args, **kwargs)
            
            warning = f"Deprecated since version {deprecated_in}"
            if removed_in:
                warning += f", will be removed in {removed_in}"
            if alternative:
                warning += f". Use {alternative} instead"
            
            response['X-API-Deprecation-Warning'] = warning
            
            # Log deprecation usage
            logger.warning(
                f"Deprecated endpoint called: {request.path} "
                f"(deprecated in {deprecated_in})"
            )
            
            return response
        
        wrapper._deprecated = True
        wrapper._deprecated_in = deprecated_in
        wrapper._removed_in = removed_in
        wrapper._alternative = alternative
        
        return wrapper
    
    return decorator


class BackwardCompatibilityMixin:
    """
    Mixin for maintaining backward compatibility.
    Transforms data between API versions.
    """
    
    def transform_request_data(self, data: Dict[str, Any], 
                              from_version: str, to_version: str) -> Dict[str, Any]:
        """
        Transform request data between versions.
        
        Args:
            data: Request data
            from_version: Source version
            to_version: Target version
            
        Returns:
            Transformed data
        """
        transformer_method = f"transform_{from_version}_to_{to_version}"
        
        if hasattr(self, transformer_method):
            return getattr(self, transformer_method)(data)
        
        return data
    
    def transform_response_data(self, data: Dict[str, Any], 
                               from_version: str, to_version: str) -> Dict[str, Any]:
        """
        Transform response data between versions.
        
        Args:
            data: Response data
            from_version: Source version
            to_version: Target version
            
        Returns:
            Transformed data
        """
        transformer_method = f"transform_response_{from_version}_to_{to_version}"
        
        if hasattr(self, transformer_method):
            return getattr(self, transformer_method)(data)
        
        return data
