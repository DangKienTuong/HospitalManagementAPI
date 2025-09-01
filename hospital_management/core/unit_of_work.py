"""
Unit of Work pattern implementation.
Manages database transactions and ensures data consistency.
"""

from typing import Dict, Any, Optional, List, Type
from django.db import transaction, models
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


class IUnitOfWork:
    """
    Interface for Unit of Work pattern.
    Defines contract for transaction management.
    """
    
    def __enter__(self):
        """Enter transaction context."""
        pass
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context."""
        pass
    
    def commit(self):
        """Commit transaction."""
        pass
    
    def rollback(self):
        """Rollback transaction."""
        pass
    
    def complete(self):
        """Complete unit of work."""
        pass


class UnitOfWork(IUnitOfWork):
    """
    Unit of Work implementation for Django ORM.
    Manages transactions across multiple repositories.
    """
    
    def __init__(self):
        """Initialize Unit of Work."""
        self._repositories: Dict[str, Any] = {}
        self._new_objects: List[models.Model] = []
        self._dirty_objects: List[models.Model] = []
        self._removed_objects: List[models.Model] = []
        self._transaction = None
        self._is_committed = False
        
    def register_repository(self, name: str, repository: Any) -> 'UnitOfWork':
        """
        Register repository with unit of work.
        
        Args:
            name: Repository name
            repository: Repository instance
            
        Returns:
            Self for chaining
        """
        self._repositories[name] = repository
        return self
    
    def get_repository(self, name: str) -> Any:
        """
        Get registered repository.
        
        Args:
            name: Repository name
            
        Returns:
            Repository instance
            
        Raises:
            KeyError: If repository not found
        """
        if name not in self._repositories:
            raise KeyError(f"Repository '{name}' not registered")
        return self._repositories[name]
    
    def register_new(self, entity: models.Model) -> 'UnitOfWork':
        """
        Register new entity for creation.
        
        Args:
            entity: Entity to create
            
        Returns:
            Self for chaining
        """
        if entity not in self._new_objects:
            self._new_objects.append(entity)
            logger.debug(f"Registered new entity: {type(entity).__name__}")
        return self
    
    def register_dirty(self, entity: models.Model) -> 'UnitOfWork':
        """
        Register modified entity for update.
        
        Args:
            entity: Entity to update
            
        Returns:
            Self for chaining
        """
        if entity not in self._dirty_objects and entity not in self._new_objects:
            self._dirty_objects.append(entity)
            logger.debug(f"Registered dirty entity: {type(entity).__name__}")
        return self
    
    def register_removed(self, entity: models.Model) -> 'UnitOfWork':
        """
        Register entity for deletion.
        
        Args:
            entity: Entity to delete
            
        Returns:
            Self for chaining
        """
        if entity in self._new_objects:
            self._new_objects.remove(entity)
        else:
            if entity not in self._removed_objects:
                self._removed_objects.append(entity)
                logger.debug(f"Registered removed entity: {type(entity).__name__}")
        return self
    
    @transaction.atomic
    def commit(self):
        """
        Commit all registered changes.
        
        Raises:
            Exception: If commit fails
        """
        if self._is_committed:
            logger.warning("Unit of work already committed")
            return
        
        try:
            # Save new objects
            for entity in self._new_objects:
                entity.save()
                logger.debug(f"Saved new entity: {type(entity).__name__} with ID {entity.pk}")
            
            # Update dirty objects
            for entity in self._dirty_objects:
                entity.save()
                logger.debug(f"Updated entity: {type(entity).__name__} with ID {entity.pk}")
            
            # Delete removed objects
            for entity in self._removed_objects:
                entity.delete()
                logger.debug(f"Deleted entity: {type(entity).__name__}")
            
            self._is_committed = True
            logger.info(f"Unit of work committed: {len(self._new_objects)} created, "
                       f"{len(self._dirty_objects)} updated, {len(self._removed_objects)} deleted")
            
            # Clear collections after successful commit
            self._clear()
            
        except Exception as e:
            logger.error(f"Unit of work commit failed: {str(e)}")
            self.rollback()
            raise
    
    def rollback(self):
        """Rollback all changes."""
        logger.info("Rolling back unit of work")
        self._clear()
        self._is_committed = False
    
    def complete(self):
        """
        Complete unit of work and commit if not already done.
        """
        if not self._is_committed:
            self.commit()
    
    def _clear(self):
        """Clear all registered objects."""
        self._new_objects.clear()
        self._dirty_objects.clear()
        self._removed_objects.clear()
    
    def __enter__(self):
        """Enter transaction context."""
        self._transaction = transaction.atomic()
        self._transaction.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit transaction context."""
        if exc_type is None:
            self.complete()
        else:
            self.rollback()
        
        if self._transaction:
            self._transaction.__exit__(exc_type, exc_val, exc_tb)


class RepositoryUnitOfWork(UnitOfWork):
    """
    Extended Unit of Work with repository integration.
    Automatically registers common repositories.
    """
    
    def __init__(self):
        super().__init__()
        self._initialize_repositories()
    
    def _initialize_repositories(self):
        """Initialize and register common repositories."""
        from core.repositories import (
            UserRepository,
            MedicalFacilityRepository,
            DoctorRepository,
            AppointmentRepository,
            PaymentRepository
        )
        
        self.register_repository('users', UserRepository())
        self.register_repository('facilities', MedicalFacilityRepository())
        self.register_repository('doctors', DoctorRepository())
        self.register_repository('appointments', AppointmentRepository())
        self.register_repository('payments', PaymentRepository())
    
    @property
    def users(self):
        """Get user repository."""
        return self.get_repository('users')
    
    @property
    def facilities(self):
        """Get medical facility repository."""
        return self.get_repository('facilities')
    
    @property
    def doctors(self):
        """Get doctor repository."""
        return self.get_repository('doctors')
    
    @property
    def appointments(self):
        """Get appointment repository."""
        return self.get_repository('appointments')
    
    @property
    def payments(self):
        """Get payment repository."""
        return self.get_repository('payments')


class AsyncUnitOfWork(UnitOfWork):
    """
    Asynchronous Unit of Work for async operations.
    Supports async/await pattern for database operations.
    """
    
    async def commit_async(self):
        """
        Asynchronously commit all registered changes.
        """
        if self._is_committed:
            logger.warning("Unit of work already committed")
            return
        
        try:
            from django.db import connection
            from asgiref.sync import sync_to_async
            
            # Convert sync operations to async
            save_new = sync_to_async(self._save_new_objects)
            save_dirty = sync_to_async(self._save_dirty_objects)
            delete_removed = sync_to_async(self._delete_removed_objects)
            
            # Execute operations asynchronously
            await save_new()
            await save_dirty()
            await delete_removed()
            
            self._is_committed = True
            logger.info(f"Async unit of work committed")
            
            self._clear()
            
        except Exception as e:
            logger.error(f"Async unit of work commit failed: {str(e)}")
            await self.rollback_async()
            raise
    
    async def rollback_async(self):
        """Asynchronously rollback all changes."""
        from asgiref.sync import sync_to_async
        await sync_to_async(self.rollback)()
    
    def _save_new_objects(self):
        """Save new objects synchronously."""
        for entity in self._new_objects:
            entity.save()
    
    def _save_dirty_objects(self):
        """Save dirty objects synchronously."""
        for entity in self._dirty_objects:
            entity.save()
    
    def _delete_removed_objects(self):
        """Delete removed objects synchronously."""
        for entity in self._removed_objects:
            entity.delete()


@contextmanager
def unit_of_work_scope():
    """
    Context manager for Unit of Work scope.
    
    Usage:
        with unit_of_work_scope() as uow:
            # Perform operations
            uow.commit()
    """
    uow = RepositoryUnitOfWork()
    try:
        yield uow
        uow.complete()
    except Exception as e:
        uow.rollback()
        raise
    finally:
        pass


class UnitOfWorkManager:
    """
    Manager for Unit of Work instances.
    Provides factory methods and lifecycle management.
    """
    
    _instances: Dict[str, UnitOfWork] = {}
    
    @classmethod
    def create(cls, name: str = 'default') -> UnitOfWork:
        """
        Create new Unit of Work instance.
        
        Args:
            name: Instance name
            
        Returns:
            New Unit of Work instance
        """
        uow = RepositoryUnitOfWork()
        cls._instances[name] = uow
        return uow
    
    @classmethod
    def get(cls, name: str = 'default') -> Optional[UnitOfWork]:
        """
        Get existing Unit of Work instance.
        
        Args:
            name: Instance name
            
        Returns:
            Unit of Work instance or None
        """
        return cls._instances.get(name)
    
    @classmethod
    def remove(cls, name: str = 'default'):
        """
        Remove Unit of Work instance.
        
        Args:
            name: Instance name
        """
        if name in cls._instances:
            del cls._instances[name]
    
    @classmethod
    def clear(cls):
        """Clear all Unit of Work instances."""
        cls._instances.clear()
