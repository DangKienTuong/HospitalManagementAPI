"""
Base Repository implementation following Repository Pattern.
Provides abstraction layer for data access with common CRUD operations.
"""

from typing import Generic, TypeVar, Optional, List, Dict, Any, Type
from django.db import models, transaction
from django.db.models import Q, QuerySet
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=models.Model)


class IRepository(ABC, Generic[T]):
    """
    Interface for Repository Pattern.
    Defines contract for data access operations.
    """
    
    @abstractmethod
    def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by primary key."""
        pass
    
    @abstractmethod
    def get_all(self, **filters) -> QuerySet[T]:
        """Get all entities with optional filters."""
        pass
    
    @abstractmethod
    def create(self, **data) -> T:
        """Create new entity."""
        pass
    
    @abstractmethod
    def update(self, id: Any, **data) -> Optional[T]:
        """Update existing entity."""
        pass
    
    @abstractmethod
    def delete(self, id: Any) -> bool:
        """Delete entity by id."""
        pass
    
    @abstractmethod
    def exists(self, **filters) -> bool:
        """Check if entity exists."""
        pass
    
    @abstractmethod
    def count(self, **filters) -> int:
        """Count entities matching filters."""
        pass


class BaseRepository(IRepository[T]):
    """
    Base repository implementing common data access patterns.
    Follows SOLID principles with single responsibility for data access.
    """
    
    def __init__(self, model: Type[T]):
        """
        Initialize repository with model class.
        
        Args:
            model: Django model class
        """
        self.model = model
        self._queryset = model.objects.all()
        
    def get_queryset(self) -> QuerySet[T]:
        """
        Get base queryset. Can be overridden for custom behavior.
        
        Returns:
            QuerySet for the model
        """
        return self._queryset.select_related().prefetch_related()
    
    def get_by_id(self, id: Any) -> Optional[T]:
        """
        Get entity by primary key.
        
        Args:
            id: Primary key value
            
        Returns:
            Model instance or None
        """
        try:
            return self.get_queryset().get(pk=id)
        except ObjectDoesNotExist:
            logger.warning(f"{self.model.__name__} with id {id} not found")
            return None
        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__} by id: {str(e)}")
            return None
    
    def get_all(self, **filters) -> QuerySet[T]:
        """
        Get all entities with optional filters.
        
        Args:
            **filters: Django ORM filter parameters
            
        Returns:
            Filtered QuerySet
        """
        try:
            queryset = self.get_queryset()
            if filters:
                queryset = queryset.filter(**filters)
            return queryset
        except Exception as e:
            logger.error(f"Error fetching {self.model.__name__} list: {str(e)}")
            return self.model.objects.none()
    
    def find(self, specification: Optional[Q] = None, **filters) -> QuerySet[T]:
        """
        Find entities matching specification pattern.
        
        Args:
            specification: Q object for complex queries
            **filters: Additional filter parameters
            
        Returns:
            Filtered QuerySet
        """
        queryset = self.get_queryset()
        
        if specification:
            queryset = queryset.filter(specification)
        
        if filters:
            queryset = queryset.filter(**filters)
            
        return queryset
    
    def create(self, **data) -> T:
        """
        Create new entity.
        
        Args:
            **data: Field values for new entity
            
        Returns:
            Created model instance
            
        Raises:
            ValueError: If validation fails
        """
        try:
            instance = self.model(**data)
            instance.full_clean()  # Validate before saving
            instance.save()
            logger.info(f"Created {self.model.__name__} with id {instance.pk}")
            return instance
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            raise ValueError(f"Failed to create {self.model.__name__}: {str(e)}")
    
    def bulk_create(self, objects: List[Dict[str, Any]], batch_size: int = 1000) -> List[T]:
        """
        Bulk create multiple entities.
        
        Args:
            objects: List of dictionaries with field values
            batch_size: Number of objects to create in one query
            
        Returns:
            List of created instances
        """
        try:
            instances = [self.model(**obj) for obj in objects]
            created = self.model.objects.bulk_create(instances, batch_size=batch_size)
            logger.info(f"Bulk created {len(created)} {self.model.__name__} instances")
            return created
        except Exception as e:
            logger.error(f"Error bulk creating {self.model.__name__}: {str(e)}")
            raise ValueError(f"Failed to bulk create {self.model.__name__}: {str(e)}")
    
    def update(self, id: Any, **data) -> Optional[T]:
        """
        Update existing entity.
        
        Args:
            id: Primary key value
            **data: Field values to update
            
        Returns:
            Updated model instance or None
        """
        try:
            instance = self.get_by_id(id)
            if not instance:
                return None
                
            for key, value in data.items():
                setattr(instance, key, value)
                
            instance.full_clean()  # Validate before saving
            instance.save()
            logger.info(f"Updated {self.model.__name__} with id {id}")
            return instance
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__}: {str(e)}")
            raise ValueError(f"Failed to update {self.model.__name__}: {str(e)}")
    
    def bulk_update(self, objects: List[T], fields: List[str], batch_size: int = 1000) -> int:
        """
        Bulk update multiple entities.
        
        Args:
            objects: List of model instances to update
            fields: List of field names to update
            batch_size: Number of objects to update in one query
            
        Returns:
            Number of updated instances
        """
        try:
            updated = self.model.objects.bulk_update(objects, fields, batch_size=batch_size)
            logger.info(f"Bulk updated {updated} {self.model.__name__} instances")
            return updated
        except Exception as e:
            logger.error(f"Error bulk updating {self.model.__name__}: {str(e)}")
            raise ValueError(f"Failed to bulk update {self.model.__name__}: {str(e)}")
    
    def delete(self, id: Any) -> bool:
        """
        Delete entity by id.
        
        Args:
            id: Primary key value
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            instance = self.get_by_id(id)
            if not instance:
                return False
                
            instance.delete()
            logger.info(f"Deleted {self.model.__name__} with id {id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__}: {str(e)}")
            return False
    
    def soft_delete(self, id: Any) -> bool:
        """
        Soft delete entity (mark as deleted without removing).
        
        Args:
            id: Primary key value
            
        Returns:
            True if soft deleted, False otherwise
        """
        try:
            instance = self.get_by_id(id)
            if not instance:
                return False
                
            if hasattr(instance, 'is_deleted'):
                instance.is_deleted = True
                instance.save()
                logger.info(f"Soft deleted {self.model.__name__} with id {id}")
                return True
            else:
                logger.warning(f"{self.model.__name__} does not support soft delete")
                return False
        except Exception as e:
            logger.error(f"Error soft deleting {self.model.__name__}: {str(e)}")
            return False
    
    def exists(self, **filters) -> bool:
        """
        Check if entity exists.
        
        Args:
            **filters: Filter parameters
            
        Returns:
            True if exists, False otherwise
        """
        try:
            return self.get_queryset().filter(**filters).exists()
        except Exception as e:
            logger.error(f"Error checking existence: {str(e)}")
            return False
    
    def count(self, **filters) -> int:
        """
        Count entities matching filters.
        
        Args:
            **filters: Filter parameters
            
        Returns:
            Number of matching entities
        """
        try:
            return self.get_queryset().filter(**filters).count()
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            return 0
    
    def paginate(self, queryset: QuerySet[T], page: int = 1, 
                 page_size: int = 20) -> Dict[str, Any]:
        """
        Paginate queryset.
        
        Args:
            queryset: QuerySet to paginate
            page: Page number (1-indexed)
            page_size: Number of items per page
            
        Returns:
            Dictionary with pagination data
        """
        try:
            paginator = Paginator(queryset, page_size)
            page_obj = paginator.get_page(page)
            
            return {
                'items': list(page_obj.object_list),
                'total': paginator.count,
                'page': page,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        except Exception as e:
            logger.error(f"Error paginating: {str(e)}")
            return {
                'items': [],
                'total': 0,
                'page': page,
                'page_size': page_size,
                'total_pages': 0,
                'has_next': False,
                'has_previous': False,
            }
    
    @transaction.atomic
    def transaction(self, func, *args, **kwargs):
        """
        Execute function in database transaction.
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}")
            raise


class CachedRepository(BaseRepository[T]):
    """
    Repository with caching support.
    Extends BaseRepository with Redis caching capabilities.
    """
    
    def __init__(self, model: Type[T], cache_timeout: int = 300):
        """
        Initialize cached repository.
        
        Args:
            model: Django model class
            cache_timeout: Cache timeout in seconds
        """
        super().__init__(model)
        self.cache_timeout = cache_timeout
        self._cache = None
        
    @property
    def cache(self):
        """Get cache instance."""
        if self._cache is None:
            from django.core.cache import cache
            self._cache = cache
        return self._cache
    
    def _get_cache_key(self, method: str, *args, **kwargs) -> str:
        """Generate cache key."""
        key_parts = [
            self.model.__name__.lower(),
            method,
            str(args),
            str(sorted(kwargs.items()))
        ]
        return ':'.join(key_parts)
    
    def get_by_id(self, id: Any) -> Optional[T]:
        """Get entity by ID with caching."""
        cache_key = self._get_cache_key('get_by_id', id)
        
        # Try to get from cache
        cached = self.cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit for {self.model.__name__} id {id}")
            return cached
        
        # Get from database
        instance = super().get_by_id(id)
        
        # Store in cache
        if instance:
            self.cache.set(cache_key, instance, self.cache_timeout)
            
        return instance
    
    def invalidate_cache(self, method: str = None, *args, **kwargs):
        """
        Invalidate cache entries.
        
        Args:
            method: Method name to invalidate
            *args: Method arguments
            **kwargs: Method keyword arguments
        """
        if method:
            cache_key = self._get_cache_key(method, *args, **kwargs)
            self.cache.delete(cache_key)
        else:
            # Clear all cache for this model
            pattern = f"{self.model.__name__.lower()}:*"
            self.cache.delete_pattern(pattern)
