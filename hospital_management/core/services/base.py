"""
Base Service layer implementation.
Provides business logic abstraction following SOLID principles.
"""

from typing import Generic, TypeVar, Optional, List, Dict, Any, Type
from abc import ABC, abstractmethod
from django.db import transaction
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


class IService(ABC, Generic[T]):
    """
    Interface for Service Layer.
    Defines contract for business logic operations.
    """
    
    @abstractmethod
    def create(self, data: Dict[str, Any]) -> T:
        """Create new entity with business rules."""
        pass
    
    @abstractmethod
    def update(self, id: Any, data: Dict[str, Any]) -> Optional[T]:
        """Update entity with business rules."""
        pass
    
    @abstractmethod
    def delete(self, id: Any) -> bool:
        """Delete entity with business rules."""
        pass
    
    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """Get all entities with optional filters."""
        pass


class BaseService(IService[T]):
    """
    Base service implementing common business logic patterns.
    Follows Single Responsibility Principle for business logic.
    """
    
    def __init__(self, repository):
        """
        Initialize service with repository.
        
        Args:
            repository: Repository instance for data access
        """
        self.repository = repository
        self._validators = []
        self._rules = []
        
    def add_validator(self, validator):
        """Add validator to service."""
        self._validators.append(validator)
        return self
    
    def add_business_rule(self, rule):
        """Add business rule to service."""
        self._rules.append(rule)
        return self
    
    def validate(self, data: Dict[str, Any], instance: Optional[T] = None) -> Dict[str, Any]:
        """
        Validate data against all validators.
        
        Args:
            data: Data to validate
            instance: Existing instance for update validation
            
        Returns:
            Validated data
            
        Raises:
            ValidationError: If validation fails
        """
        errors = {}
        
        for validator in self._validators:
            try:
                validator.validate(data, instance)
            except ValidationError as e:
                errors.update(e.message_dict if hasattr(e, 'message_dict') else {'__all__': str(e)})
        
        if errors:
            raise ValidationError(errors)
        
        return data
    
    def apply_business_rules(self, data: Dict[str, Any], operation: str = 'create') -> Dict[str, Any]:
        """
        Apply business rules to data.
        
        Args:
            data: Data to process
            operation: Operation type (create, update, delete)
            
        Returns:
            Processed data
        """
        for rule in self._rules:
            if hasattr(rule, operation):
                data = getattr(rule, operation)(data)
        return data
    
    @transaction.atomic
    def create(self, data: Dict[str, Any]) -> T:
        """
        Create new entity with validation and business rules.
        
        Args:
            data: Entity data
            
        Returns:
            Created entity
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Validate data
            validated_data = self.validate(data)
            
            # Apply business rules
            processed_data = self.apply_business_rules(validated_data, 'create')
            
            # Create entity
            entity = self.repository.create(**processed_data)
            
            # Post-create hooks
            self._after_create(entity)
            
            logger.info(f"Created {type(entity).__name__} with ID {entity.pk}")
            return entity
            
        except ValidationError as e:
            logger.error(f"Validation error in create: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in create: {str(e)}")
            raise ValueError(f"Failed to create entity: {str(e)}")
    
    @transaction.atomic
    def update(self, id: Any, data: Dict[str, Any]) -> Optional[T]:
        """
        Update entity with validation and business rules.
        
        Args:
            id: Entity ID
            data: Update data
            
        Returns:
            Updated entity or None
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            # Get existing entity
            entity = self.repository.get_by_id(id)
            if not entity:
                logger.warning(f"Entity with ID {id} not found for update")
                return None
            
            # Validate data
            validated_data = self.validate(data, entity)
            
            # Apply business rules
            processed_data = self.apply_business_rules(validated_data, 'update')
            
            # Update entity
            updated_entity = self.repository.update(id, **processed_data)
            
            # Post-update hooks
            self._after_update(updated_entity)
            
            logger.info(f"Updated {type(updated_entity).__name__} with ID {id}")
            return updated_entity
            
        except ValidationError as e:
            logger.error(f"Validation error in update: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in update: {str(e)}")
            raise ValueError(f"Failed to update entity: {str(e)}")
    
    @transaction.atomic
    def delete(self, id: Any) -> bool:
        """
        Delete entity with business rules.
        
        Args:
            id: Entity ID
            
        Returns:
            True if deleted successfully
        """
        try:
            # Get existing entity
            entity = self.repository.get_by_id(id)
            if not entity:
                logger.warning(f"Entity with ID {id} not found for deletion")
                return False
            
            # Check if deletion is allowed
            if not self._can_delete(entity):
                logger.warning(f"Deletion not allowed for entity with ID {id}")
                return False
            
            # Pre-delete hooks
            self._before_delete(entity)
            
            # Delete entity
            result = self.repository.delete(id)
            
            # Post-delete hooks
            if result:
                self._after_delete(entity)
            
            logger.info(f"Deleted entity with ID {id}")
            return result
            
        except Exception as e:
            logger.error(f"Error in delete: {str(e)}")
            return False
    
    def get_by_id(self, id: Any) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            Entity or None
        """
        return self.repository.get_by_id(id)
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """
        Get all entities with optional filters.
        
        Args:
            filters: Filter parameters
            
        Returns:
            List of entities
        """
        if filters:
            return list(self.repository.get_all(**filters))
        return list(self.repository.get_all())
    
    def paginate(self, page: int = 1, page_size: int = 20, 
                 filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Get paginated entities.
        
        Args:
            page: Page number
            page_size: Items per page
            filters: Filter parameters
            
        Returns:
            Pagination dictionary
        """
        queryset = self.repository.get_all(**filters) if filters else self.repository.get_all()
        return self.repository.paginate(queryset, page, page_size)
    
    # Hook methods for subclasses
    def _after_create(self, entity: T):
        """Hook called after entity creation."""
        pass
    
    def _after_update(self, entity: T):
        """Hook called after entity update."""
        pass
    
    def _before_delete(self, entity: T):
        """Hook called before entity deletion."""
        pass
    
    def _after_delete(self, entity: T):
        """Hook called after entity deletion."""
        pass
    
    def _can_delete(self, entity: T) -> bool:
        """Check if entity can be deleted."""
        return True


class CachedService(BaseService[T]):
    """
    Service with caching support.
    Extends BaseService with cache invalidation on mutations.
    """
    
    def create(self, data: Dict[str, Any]) -> T:
        """Create entity and invalidate cache."""
        entity = super().create(data)
        if hasattr(self.repository, 'invalidate_cache'):
            self.repository.invalidate_cache()
        return entity
    
    def update(self, id: Any, data: Dict[str, Any]) -> Optional[T]:
        """Update entity and invalidate cache."""
        entity = super().update(id, data)
        if entity and hasattr(self.repository, 'invalidate_cache'):
            self.repository.invalidate_cache('get_by_id', id)
        return entity
    
    def delete(self, id: Any) -> bool:
        """Delete entity and invalidate cache."""
        result = super().delete(id)
        if result and hasattr(self.repository, 'invalidate_cache'):
            self.repository.invalidate_cache('get_by_id', id)
        return result


class TransactionalService(BaseService[T]):
    """
    Service with advanced transaction management.
    Implements Unit of Work pattern for complex operations.
    """
    
    def __init__(self, repository):
        super().__init__(repository)
        self._operations = []
        
    def add_operation(self, operation, *args, **kwargs):
        """Add operation to transaction queue."""
        self._operations.append((operation, args, kwargs))
        return self
    
    @transaction.atomic
    def execute_transaction(self) -> List[Any]:
        """
        Execute all queued operations in a single transaction.
        
        Returns:
            List of operation results
        """
        results = []
        try:
            for operation, args, kwargs in self._operations:
                result = operation(*args, **kwargs)
                results.append(result)
            
            self._operations.clear()
            logger.info(f"Successfully executed {len(results)} operations in transaction")
            return results
            
        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}")
            self._operations.clear()
            raise
    
    @transaction.atomic
    def bulk_create(self, data_list: List[Dict[str, Any]]) -> List[T]:
        """
        Bulk create multiple entities in transaction.
        
        Args:
            data_list: List of entity data
            
        Returns:
            List of created entities
        """
        entities = []
        try:
            for data in data_list:
                validated_data = self.validate(data)
                processed_data = self.apply_business_rules(validated_data, 'create')
                entities.append(processed_data)
            
            created = self.repository.bulk_create(entities)
            logger.info(f"Bulk created {len(created)} entities")
            return created
            
        except Exception as e:
            logger.error(f"Bulk create failed: {str(e)}")
            raise
