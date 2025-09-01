"""
Base models and mixins for the Hospital Management System.
Provides reusable model components following DRY principle.
"""

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from typing import Optional
import uuid


class TimestampMixin(models.Model):
    """
    Mixin for automatic timestamp fields.
    Adds created_at and updated_at fields to models.
    """
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_column='created_at',
        help_text='Timestamp when record was created'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        db_column='updated_at',
        help_text='Timestamp when record was last updated'
    )
    
    class Meta:
        abstract = True


class AuditMixin(TimestampMixin):
    """
    Mixin for audit fields.
    Tracks who created and last modified records.
    """
    
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        db_column='created_by',
        help_text='User who created this record'
    )
    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        db_column='updated_by',
        help_text='User who last updated this record'
    )
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """Override save to set audit fields."""
        # Get user from kwargs if provided
        user = kwargs.pop('user', None)
        
        if user:
            if not self.pk:  # New record
                self.created_by = user
            self.updated_by = user
        
        super().save(*args, **kwargs)


class SoftDeleteMixin(models.Model):
    """
    Mixin for soft delete functionality.
    Records are marked as deleted instead of being removed.
    """
    
    is_deleted = models.BooleanField(
        default=False,
        db_column='is_deleted',
        help_text='Whether this record is soft deleted'
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        db_column='deleted_at',
        help_text='Timestamp when record was soft deleted'
    )
    deleted_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted',
        db_column='deleted_by',
        help_text='User who deleted this record'
    )
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False, soft=True, user=None):
        """
        Override delete for soft delete.
        
        Args:
            soft: If True, perform soft delete. If False, hard delete.
            user: User performing the deletion
        """
        if soft:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            if user:
                self.deleted_by = user
            self.save()
        else:
            super().delete(using=using, keep_parents=keep_parents)
    
    def restore(self):
        """Restore soft deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.save()
    
    @classmethod
    def all_with_deleted(cls):
        """Get all records including soft deleted."""
        return cls.objects.all()
    
    @classmethod
    def only_deleted(cls):
        """Get only soft deleted records."""
        return cls.objects.filter(is_deleted=True)


class UUIDMixin(models.Model):
    """
    Mixin for UUID field.
    Adds a unique UUID identifier to models.
    """
    
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_column='uuid',
        help_text='Unique identifier'
    )
    
    class Meta:
        abstract = True


class StatusMixin(models.Model):
    """
    Mixin for status field with common statuses.
    """
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
        ('suspended', 'Suspended'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_column='status',
        help_text='Current status'
    )
    
    class Meta:
        abstract = True
    
    def is_active(self) -> bool:
        """Check if record is active."""
        return self.status == 'active'
    
    def activate(self):
        """Activate record."""
        self.status = 'active'
        self.save()
    
    def deactivate(self):
        """Deactivate record."""
        self.status = 'inactive'
        self.save()


class SlugMixin(models.Model):
    """
    Mixin for slug field.
    Adds URL-friendly slug field.
    """
    
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_column='slug',
        help_text='URL-friendly identifier'
    )
    
    class Meta:
        abstract = True


class OrderingMixin(models.Model):
    """
    Mixin for ordering/sorting.
    """
    
    display_order = models.IntegerField(
        default=0,
        db_column='display_order',
        help_text='Display order for sorting'
    )
    
    class Meta:
        abstract = True
        ordering = ['display_order']


class BaseModel(AuditMixin, SoftDeleteMixin, UUIDMixin):
    """
    Base model with all common mixins.
    All models should inherit from this for consistency.
    """
    
    class Meta:
        abstract = True
    
    def __str__(self):
        """Default string representation."""
        if hasattr(self, 'name'):
            return str(self.name)
        elif hasattr(self, 'title'):
            return str(self.title)
        else:
            return f"{self.__class__.__name__} #{self.pk}"
    
    @classmethod
    def get_model_name(cls) -> str:
        """Get model name for logging/display."""
        return cls._meta.verbose_name
    
    @classmethod
    def get_db_table(cls) -> str:
        """Get database table name."""
        return cls._meta.db_table
    
    def to_dict(self) -> dict:
        """Convert model instance to dictionary."""
        from django.forms.models import model_to_dict
        return model_to_dict(self)


class TreeNodeMixin(models.Model):
    """
    Mixin for hierarchical/tree structures.
    Implements parent-child relationships.
    """
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        db_column='parent_id',
        help_text='Parent node'
    )
    
    class Meta:
        abstract = True
    
    def get_ancestors(self):
        """Get all ancestors of this node."""
        ancestors = []
        node = self.parent
        while node:
            ancestors.append(node)
            node = node.parent
        return ancestors
    
    def get_descendants(self):
        """Get all descendants of this node."""
        descendants = []
        children = list(self.children.all())
        descendants.extend(children)
        
        for child in children:
            descendants.extend(child.get_descendants())
        
        return descendants
    
    def get_root(self):
        """Get root node of the tree."""
        node = self
        while node.parent:
            node = node.parent
        return node
    
    def get_level(self) -> int:
        """Get level/depth in the tree."""
        level = 0
        node = self.parent
        while node:
            level += 1
            node = node.parent
        return level
    
    def is_root(self) -> bool:
        """Check if this is a root node."""
        return self.parent is None
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node."""
        return not self.children.exists()


class VersionedMixin(models.Model):
    """
    Mixin for versioned records.
    Tracks version number for optimistic locking.
    """
    
    version = models.IntegerField(
        default=1,
        db_column='version',
        help_text='Version number for optimistic locking'
    )
    
    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs):
        """Increment version on save."""
        if self.pk:  # Existing record
            self.version += 1
        super().save(*args, **kwargs)


class MetadataMixin(models.Model):
    """
    Mixin for storing arbitrary metadata as JSON.
    """
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        db_column='metadata',
        help_text='Additional metadata as JSON'
    )
    
    class Meta:
        abstract = True
    
    def get_metadata(self, key: str, default=None):
        """Get metadata value by key."""
        return self.metadata.get(key, default)
    
    def set_metadata(self, key: str, value):
        """Set metadata value by key."""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
        self.save()
    
    def update_metadata(self, data: dict):
        """Update metadata with dictionary."""
        if self.metadata is None:
            self.metadata = {}
        self.metadata.update(data)
        self.save()


class TaggableMixin(models.Model):
    """
    Mixin for tagging functionality.
    """
    
    tags = models.JSONField(
        default=list,
        blank=True,
        db_column='tags',
        help_text='List of tags'
    )
    
    class Meta:
        abstract = True
    
    def add_tag(self, tag: str):
        """Add a tag."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.save()
    
    def remove_tag(self, tag: str):
        """Remove a tag."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.save()
    
    def has_tag(self, tag: str) -> bool:
        """Check if has a tag."""
        return tag in self.tags
    
    def clear_tags(self):
        """Clear all tags."""
        self.tags = []
        self.save()


class PublishableMixin(models.Model):
    """
    Mixin for publishable content.
    """
    
    is_published = models.BooleanField(
        default=False,
        db_column='is_published',
        help_text='Whether this content is published'
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        db_column='published_at',
        help_text='Publication timestamp'
    )
    
    class Meta:
        abstract = True
    
    def publish(self):
        """Publish content."""
        self.is_published = True
        self.published_at = timezone.now()
        self.save()
    
    def unpublish(self):
        """Unpublish content."""
        self.is_published = False
        self.published_at = None
        self.save()


# Query Managers
class ActiveManager(models.Manager):
    """Manager for active records only."""
    
    def get_queryset(self):
        return super().get_queryset().filter(
            models.Q(is_deleted=False) | models.Q(is_deleted__isnull=True)
        )


class PublishedManager(models.Manager):
    """Manager for published content only."""
    
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)
