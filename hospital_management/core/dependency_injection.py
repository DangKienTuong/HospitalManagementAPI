"""
Dependency Injection Container for Hospital Management System.
Implements IoC container pattern for better testability and loose coupling.
"""

import inspect
from typing import Type, TypeVar, Dict, Any, Callable, Optional, Union
from abc import ABC, abstractmethod
from django.conf import settings
import threading

T = TypeVar('T')


class ServiceLifetime:
    """Service lifetime enumeration."""
    TRANSIENT = 'transient'
    SINGLETON = 'singleton'
    SCOPED = 'scoped'


class ServiceDescriptor:
    """Describes how a service should be created and managed."""
    
    def __init__(
        self, 
        service_type: Type, 
        implementation: Union[Type, Callable], 
        lifetime: str = ServiceLifetime.TRANSIENT,
        factory: Optional[Callable] = None
    ):
        self.service_type = service_type
        self.implementation = implementation
        self.lifetime = lifetime
        self.factory = factory
        self.instance = None
        self._lock = threading.RLock()
    
    def create_instance(self, container: 'DIContainer') -> Any:
        """Create an instance based on the service descriptor."""
        if self.lifetime == ServiceLifetime.SINGLETON:
            with self._lock:
                if self.instance is None:
                    self.instance = self._create_new_instance(container)
                return self.instance
        
        return self._create_new_instance(container)
    
    def _create_new_instance(self, container: 'DIContainer') -> Any:
        """Create a new instance of the service."""
        if self.factory:
            return self.factory(container)
        
        if inspect.isclass(self.implementation):
            # Get constructor parameters
            sig = inspect.signature(self.implementation.__init__)
            params = {}
            
            for name, param in sig.parameters.items():
                if name == 'self':
                    continue
                
                if param.annotation != param.empty:
                    # Resolve dependency from container
                    dependency = container.resolve(param.annotation)
                    params[name] = dependency
                elif param.default != param.empty:
                    # Use default value
                    params[name] = param.default
            
            return self.implementation(**params)
        else:
            return self.implementation


class DIContainer:
    """Dependency Injection Container implementing IoC pattern."""
    
    def __init__(self):
        self._services: Dict[Type, ServiceDescriptor] = {}
        self._lock = threading.RLock()
        self._scoped_instances: Dict[Type, Any] = {}
    
    def register_transient(self, service_type: Type[T], implementation: Type[T]) -> 'DIContainer':
        """Register a transient service (new instance every time)."""
        return self._register_service(service_type, implementation, ServiceLifetime.TRANSIENT)
    
    def register_singleton(self, service_type: Type[T], implementation: Type[T]) -> 'DIContainer':
        """Register a singleton service (single instance for application lifetime)."""
        return self._register_service(service_type, implementation, ServiceLifetime.SINGLETON)
    
    def register_scoped(self, service_type: Type[T], implementation: Type[T]) -> 'DIContainer':
        """Register a scoped service (single instance per request/scope)."""
        return self._register_service(service_type, implementation, ServiceLifetime.SCOPED)
    
    def register_factory(self, service_type: Type[T], factory: Callable[['DIContainer'], T]) -> 'DIContainer':
        """Register a service with a custom factory function."""
        descriptor = ServiceDescriptor(service_type, None, ServiceLifetime.TRANSIENT, factory)
        with self._lock:
            self._services[service_type] = descriptor
        return self
    
    def register_instance(self, service_type: Type[T], instance: T) -> 'DIContainer':
        """Register a specific instance as a singleton."""
        descriptor = ServiceDescriptor(service_type, type(instance), ServiceLifetime.SINGLETON)
        descriptor.instance = instance
        with self._lock:
            self._services[service_type] = descriptor
        return self
    
    def _register_service(self, service_type: Type, implementation: Type, lifetime: str) -> 'DIContainer':
        """Internal method to register a service."""
        descriptor = ServiceDescriptor(service_type, implementation, lifetime)
        with self._lock:
            self._services[service_type] = descriptor
        return self
    
    def resolve(self, service_type: Type[T]) -> T:
        """Resolve a service from the container."""
        with self._lock:
            if service_type not in self._services:
                # Try to resolve concrete type if not registered
                if inspect.isclass(service_type) and not inspect.isabstract(service_type):
                    return self._auto_resolve(service_type)
                
                raise ServiceNotRegisteredException(f"Service {service_type.__name__} is not registered")
            
            descriptor = self._services[service_type]
            
            if descriptor.lifetime == ServiceLifetime.SCOPED:
                if service_type in self._scoped_instances:
                    return self._scoped_instances[service_type]
                
                instance = descriptor.create_instance(self)
                self._scoped_instances[service_type] = instance
                return instance
            
            return descriptor.create_instance(self)
    
    def _auto_resolve(self, service_type: Type[T]) -> T:
        """Automatically resolve a concrete type by analyzing its dependencies."""
        sig = inspect.signature(service_type.__init__)
        params = {}
        
        for name, param in sig.parameters.items():
            if name == 'self':
                continue
            
            if param.annotation != param.empty:
                dependency = self.resolve(param.annotation)
                params[name] = dependency
            elif param.default != param.empty:
                params[name] = param.default
            else:
                raise DependencyResolutionException(
                    f"Cannot resolve parameter '{name}' for type {service_type.__name__}"
                )
        
        return service_type(**params)
    
    def clear_scoped(self):
        """Clear scoped instances (typically called at end of request)."""
        with self._lock:
            self._scoped_instances.clear()
    
    def is_registered(self, service_type: Type) -> bool:
        """Check if a service type is registered."""
        return service_type in self._services
    
    def get_registered_services(self) -> Dict[Type, ServiceDescriptor]:
        """Get all registered services."""
        return self._services.copy()


class ServiceNotRegisteredException(Exception):
    """Exception raised when trying to resolve an unregistered service."""
    pass


class DependencyResolutionException(Exception):
    """Exception raised when dependency resolution fails."""
    pass


class ServiceProvider:
    """Service provider for managing container lifecycle."""
    
    def __init__(self, container: DIContainer):
        self.container = container
    
    def get_service(self, service_type: Type[T]) -> T:
        """Get a service from the container."""
        return self.container.resolve(service_type)
    
    def get_required_service(self, service_type: Type[T]) -> T:
        """Get a required service, raising exception if not found."""
        if not self.container.is_registered(service_type):
            raise ServiceNotRegisteredException(f"Required service {service_type.__name__} is not registered")
        return self.container.resolve(service_type)


# Global container instance
_container: Optional[DIContainer] = None
_container_lock = threading.RLock()


def get_container() -> DIContainer:
    """Get the global DI container instance."""
    global _container
    if _container is None:
        with _container_lock:
            if _container is None:
                _container = DIContainer()
                _configure_services(_container)
    return _container


def _configure_services(container: DIContainer):
    """Configure default services in the container."""
    from .interfaces import (
        ILogger, IRepository, IUnitOfWork, IEventPublisher, 
        ICacheService, IValidationService
    )
    
    # Register core services
    # Note: These would be implemented in their respective modules
    
    # Example registrations (would be uncommented when implementations exist):
    # container.register_singleton(ILogger, ConsoleLogger)
    # container.register_scoped(IUnitOfWork, UnitOfWork)
    # container.register_singleton(ICacheService, RedisCacheService)
    
    pass


def inject(*service_types: Type) -> Callable:
    """Decorator for dependency injection into functions/methods."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            container = get_container()
            
            # Inject services as keyword arguments
            for service_type in service_types:
                if service_type.__name__.lower() not in kwargs:
                    service_instance = container.resolve(service_type)
                    kwargs[service_type.__name__.lower()] = service_instance
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class DIMiddleware:
    """Django middleware for managing DI container lifecycle."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Clear scoped instances at start of request
        container = get_container()
        container.clear_scoped()
        
        # Add container to request
        request.container = container
        
        try:
            response = self.get_response(request)
        finally:
            # Clear scoped instances at end of request
            container.clear_scoped()
        
        return response


class ServiceModule(ABC):
    """Abstract base class for service modules."""
    
    @abstractmethod
    def configure_services(self, container: DIContainer) -> None:
        """Configure services for this module."""
        pass


class AuthenticationServiceModule(ServiceModule):
    """Service module for authentication-related services."""
    
    def configure_services(self, container: DIContainer) -> None:
        """Configure authentication services."""
        from authentication.services import AuthenticationService, UserManagementService
        from authentication.repositories import NguoiDungRepository
        
        container.register_scoped(NguoiDungRepository, NguoiDungRepository)
        container.register_scoped(AuthenticationService, AuthenticationService)
        container.register_scoped(UserManagementService, UserManagementService)


class MedicalServiceModule(ServiceModule):
    """Service module for medical-related services."""
    
    def configure_services(self, container: DIContainer) -> None:
        """Configure medical services."""
        from medical.services import (
            MedicalFacilityService, SpecialtyService, 
            DoctorService, MedicalServiceService
        )
        from medical.repositories import (
            CoSoYTeRepository, ChuyenKhoaRepository,
            BacSiRepository, DichVuYTeRepository
        )
        
        # Repositories
        container.register_scoped(CoSoYTeRepository, CoSoYTeRepository)
        container.register_scoped(ChuyenKhoaRepository, ChuyenKhoaRepository)
        container.register_scoped(BacSiRepository, BacSiRepository)
        container.register_scoped(DichVuYTeRepository, DichVuYTeRepository)
        
        # Services
        container.register_scoped(MedicalFacilityService, MedicalFacilityService)
        container.register_scoped(SpecialtyService, SpecialtyService)
        container.register_scoped(DoctorService, DoctorService)
        container.register_scoped(MedicalServiceService, MedicalServiceService)


class UsersServiceModule(ServiceModule):
    """Service module for user/patient-related services."""
    
    def configure_services(self, container: DIContainer) -> None:
        """Configure user services."""
        from users.services import PatientService
        from users.repositories import BenhNhanRepository
        
        container.register_scoped(BenhNhanRepository, BenhNhanRepository)
        container.register_scoped(PatientService, PatientService)


class AppointmentsServiceModule(ServiceModule):
    """Service module for appointment-related services."""
    
    def configure_services(self, container: DIContainer) -> None:
        """Configure appointment services."""
        from appointments.services import (
            ScheduleService, AppointmentService, TeleconsultationService
        )
        from appointments.repositories import (
            LichLamViecRepository, LichKhamRepository, BuoiTuVanRepository
        )
        
        # Repositories
        container.register_scoped(LichLamViecRepository, LichLamViecRepository)
        container.register_scoped(LichKhamRepository, LichKhamRepository)
        container.register_scoped(BuoiTuVanRepository, BuoiTuVanRepository)
        
        # Services
        container.register_scoped(ScheduleService, ScheduleService)
        container.register_scoped(AppointmentService, AppointmentService)
        container.register_scoped(TeleconsultationService, TeleconsultationService)


def configure_all_services(container: DIContainer) -> None:
    """Configure all application services."""
    modules = [
        AuthenticationServiceModule(),
        MedicalServiceModule(),
        UsersServiceModule(),
        AppointmentsServiceModule(),
    ]
    
    for module in modules:
        module.configure_services(container)
