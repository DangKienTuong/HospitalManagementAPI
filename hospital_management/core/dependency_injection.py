"""
Dependency Injection container for the Hospital Management System.
Implements IoC (Inversion of Control) for better testability and flexibility.
"""

from typing import Dict, Type, Any, Optional, Callable
from abc import ABC, abstractmethod
import inspect
import logging

logger = logging.getLogger(__name__)


class ServiceNotFoundError(Exception):
    """Exception raised when a service is not found in the container."""
    pass


class CircularDependencyError(Exception):
    """Exception raised when circular dependency is detected."""
    pass


class IServiceContainer(ABC):
    """
    Interface for Service Container.
    Defines contract for dependency injection container.
    """
    
    @abstractmethod
    def register(self, name: str, factory: Callable, singleton: bool = False):
        """Register a service."""
        pass
    
    @abstractmethod
    def resolve(self, name: str) -> Any:
        """Resolve a service."""
        pass
    
    @abstractmethod
    def has(self, name: str) -> bool:
        """Check if service is registered."""
        pass


class ServiceContainer(IServiceContainer):
    """
    Dependency Injection container implementation.
    Manages service registration and resolution.
    """
    
    def __init__(self):
        """Initialize the service container."""
        self._services: Dict[str, Dict[str, Any]] = {}
        self._singletons: Dict[str, Any] = {}
        self._resolving: set = set()
        
    def register(self, name: str, factory: Callable = None, 
                 singleton: bool = False, interface: Type = None):
        """
        Register a service in the container.
        
        Args:
            name: Service name
            factory: Factory function or class
            singleton: Whether to create single instance
            interface: Interface the service implements
        """
        if factory is None:
            # Used as decorator
            def decorator(cls):
                self._register_service(name, cls, singleton, interface)
                return cls
            return decorator
        
        self._register_service(name, factory, singleton, interface)
        
    def _register_service(self, name: str, factory: Callable, 
                         singleton: bool, interface: Type = None):
        """Internal method to register service."""
        self._services[name] = {
            'factory': factory,
            'singleton': singleton,
            'interface': interface
        }
        logger.debug(f"Registered service: {name} (singleton={singleton})")
        
    def register_instance(self, name: str, instance: Any):
        """
        Register an existing instance as a singleton.
        
        Args:
            name: Service name
            instance: Service instance
        """
        self._services[name] = {
            'factory': lambda: instance,
            'singleton': True,
            'interface': type(instance)
        }
        self._singletons[name] = instance
        logger.debug(f"Registered instance: {name}")
        
    def resolve(self, name: str) -> Any:
        """
        Resolve a service from the container.
        
        Args:
            name: Service name
            
        Returns:
            Service instance
            
        Raises:
            ServiceNotFoundError: If service not found
            CircularDependencyError: If circular dependency detected
        """
        if name not in self._services:
            raise ServiceNotFoundError(f"Service '{name}' not found in container")
        
        # Check for circular dependencies
        if name in self._resolving:
            raise CircularDependencyError(f"Circular dependency detected for '{name}'")
        
        service_config = self._services[name]
        
        # Return singleton if exists
        if service_config['singleton'] and name in self._singletons:
            return self._singletons[name]
        
        try:
            self._resolving.add(name)
            
            # Create instance
            factory = service_config['factory']
            
            # Auto-inject dependencies if it's a class
            if inspect.isclass(factory):
                instance = self._create_with_dependencies(factory)
            else:
                instance = factory()
            
            # Store singleton
            if service_config['singleton']:
                self._singletons[name] = instance
            
            logger.debug(f"Resolved service: {name}")
            return instance
            
        finally:
            self._resolving.remove(name)
    
    def _create_with_dependencies(self, cls: Type) -> Any:
        """
        Create instance with automatic dependency injection.
        
        Args:
            cls: Class to instantiate
            
        Returns:
            Class instance with injected dependencies
        """
        # Get constructor signature
        sig = inspect.signature(cls.__init__)
        kwargs = {}
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':
                continue
            
            # Try to resolve by parameter name
            if self.has(param_name):
                kwargs[param_name] = self.resolve(param_name)
            # Try to resolve by type annotation
            elif param.annotation != param.empty:
                service_name = self._find_service_by_type(param.annotation)
                if service_name:
                    kwargs[param_name] = self.resolve(service_name)
            # Use default if available
            elif param.default != param.empty:
                kwargs[param_name] = param.default
        
        return cls(**kwargs)
    
    def _find_service_by_type(self, service_type: Type) -> Optional[str]:
        """
        Find service name by type/interface.
        
        Args:
            service_type: Type to search for
            
        Returns:
            Service name or None
        """
        for name, config in self._services.items():
            if config.get('interface') == service_type:
                return name
            if inspect.isclass(config['factory']) and issubclass(config['factory'], service_type):
                return name
        return None
    
    def has(self, name: str) -> bool:
        """
        Check if service is registered.
        
        Args:
            name: Service name
            
        Returns:
            True if service is registered
        """
        return name in self._services
    
    def get_all_services(self) -> Dict[str, Any]:
        """
        Get all registered services.
        
        Returns:
            Dictionary of service configurations
        """
        return self._services.copy()
    
    def clear(self):
        """Clear all registered services."""
        self._services.clear()
        self._singletons.clear()
        self._resolving.clear()
        logger.debug("Cleared all services from container")


# Global container instance
container = ServiceContainer()


def inject(func: Callable) -> Callable:
    """
    Decorator for automatic dependency injection.
    
    Usage:
        @inject
        def my_function(user_service: UserService):
            # user_service will be automatically injected
            pass
    """
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        
        for param_name, param in sig.parameters.items():
            if param_name not in kwargs:
                # Try to resolve by parameter name
                if container.has(param_name):
                    kwargs[param_name] = container.resolve(param_name)
                # Try to resolve by type annotation
                elif param.annotation != param.empty:
                    service_name = container._find_service_by_type(param.annotation)
                    if service_name:
                        kwargs[param_name] = container.resolve(service_name)
        
        return func(*args, **kwargs)
    
    return wrapper


class ServiceProvider:
    """
    Base class for service providers.
    Groups related service registrations.
    """
    
    def __init__(self, container: ServiceContainer):
        """
        Initialize service provider.
        
        Args:
            container: Service container
        """
        self.container = container
    
    def register(self):
        """Register services. Override in subclasses."""
        raise NotImplementedError
    
    def boot(self):
        """Bootstrap services after all providers registered."""
        pass


class RepositoryServiceProvider(ServiceProvider):
    """
    Service provider for repository registration.
    """
    
    def register(self):
        """Register all repositories."""
        from core.repositories import (
            UserRepository,
            PatientRepository,
            MedicalFacilityRepository,
            DoctorRepository,
            SpecialtyRepository,
            ServiceRepository,
            AppointmentRepository,
            ScheduleRepository,
            TeleconsultationRepository,
            PaymentRepository
        )
        
        # Register repositories as singletons
        self.container.register('user_repository', UserRepository, singleton=True)
        self.container.register('patient_repository', PatientRepository, singleton=True)
        self.container.register('facility_repository', MedicalFacilityRepository, singleton=True)
        self.container.register('doctor_repository', DoctorRepository, singleton=True)
        self.container.register('specialty_repository', SpecialtyRepository, singleton=True)
        self.container.register('service_repository', ServiceRepository, singleton=True)
        self.container.register('appointment_repository', AppointmentRepository, singleton=True)
        self.container.register('schedule_repository', ScheduleRepository, singleton=True)
        self.container.register('teleconsultation_repository', TeleconsultationRepository, singleton=True)
        self.container.register('payment_repository', PaymentRepository, singleton=True)


class ServiceLayerProvider(ServiceProvider):
    """
    Service provider for service layer registration.
    """
    
    def register(self):
        """Register all services."""
        from core.services.user_service import UserService, PatientService
        
        # Register services
        self.container.register('user_service', UserService, singleton=False)
        self.container.register('patient_service', PatientService, singleton=False)


class DependencyInjectionMiddleware:
    """
    Middleware to inject container into request.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Attach container to request
        request.container = container
        
        response = self.get_response(request)
        return response


def setup_dependency_injection():
    """
    Setup dependency injection for the application.
    Called during application startup.
    """
    # Register providers
    providers = [
        RepositoryServiceProvider(container),
        ServiceLayerProvider(container),
    ]
    
    # Register all services
    for provider in providers:
        provider.register()
    
    # Bootstrap services
    for provider in providers:
        provider.boot()
    
    logger.info("Dependency injection container initialized")


# Interfaces for dependency injection
class IUserService(ABC):
    """Interface for user service."""
    
    @abstractmethod
    def authenticate_user(self, phone: str, password: str) -> Optional[Dict]:
        pass
    
    @abstractmethod
    def register_user(self, data: Dict) -> Dict:
        pass


class IPaymentService(ABC):
    """Interface for payment service."""
    
    @abstractmethod
    def process_payment(self, payment_id: int, data: Dict) -> bool:
        pass
    
    @abstractmethod
    def refund_payment(self, payment_id: int) -> bool:
        pass


class INotificationService(ABC):
    """Interface for notification service."""
    
    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> bool:
        pass
    
    @abstractmethod
    def send_sms(self, to: str, message: str) -> bool:
        pass