"""
Custom pagination classes for Hospital Management System.
Implements enhanced pagination with metadata and performance optimizations.
"""

from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, CursorPagination
from rest_framework.response import Response
from collections import OrderedDict
from django.core.paginator import InvalidPage
from django.utils.translation import gettext_lazy as _
from typing import Dict, Any, Optional
import math


class CustomPageNumberPagination(PageNumberPagination):
    """Enhanced page number pagination with metadata."""
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """Return paginated response with enhanced metadata."""
        return Response(OrderedDict([
            ('status', 'success'),
            ('pagination', {
                'count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'page_size': self.get_page_size(self.request),
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
                'next_page': self.page.next_page_number() if self.page.has_next() else None,
                'previous_page': self.page.previous_page_number() if self.page.has_previous() else None,
                'start_index': self.page.start_index(),
                'end_index': self.page.end_index(),
            }),
            ('links', {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'first': self.get_first_link(),
                'last': self.get_last_link(),
            }),
            ('data', data),
            ('message', f'Retrieved {len(data)} items from page {self.page.number}')
        ]))
    
    def get_first_link(self):
        """Get link to first page."""
        if self.page.number <= 1:
            return None
        
        url = self.request.build_absolute_uri()
        return self.replace_query_param(url, self.page_query_param, 1)
    
    def get_last_link(self):
        """Get link to last page."""
        if self.page.number >= self.page.paginator.num_pages:
            return None
        
        url = self.request.build_absolute_uri()
        return self.replace_query_param(url, self.page_query_param, self.page.paginator.num_pages)
    
    def replace_query_param(self, url, key, val):
        """Replace query parameter in URL."""
        from django.utils.http import urlencode
        from urllib.parse import urlparse, parse_qs, urlunparse
        
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        query_params[key] = [str(val)]
        new_query = urlencode(query_params, doseq=True)
        return urlunparse(parsed._replace(query=new_query))


class OptimizedLimitOffsetPagination(LimitOffsetPagination):
    """Optimized limit/offset pagination for large datasets."""
    
    default_limit = 20
    limit_query_param = 'limit'
    offset_query_param = 'offset'
    max_limit = 100
    
    def get_paginated_response(self, data):
        """Return paginated response with performance metrics."""
        total_count = self.count if hasattr(self, 'count') else len(data)
        
        return Response(OrderedDict([
            ('status', 'success'),
            ('pagination', {
                'count': total_count,
                'limit': self.get_limit(self.request),
                'offset': self.get_offset(self.request),
                'has_next': self.get_next_link() is not None,
                'has_previous': self.get_previous_link() is not None,
            }),
            ('links', {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            }),
            ('data', data),
            ('message', f'Retrieved {len(data)} items with offset {self.get_offset(self.request)}')
        ]))


class CursorBasedPagination(CursorPagination):
    """Cursor-based pagination for real-time data and large datasets."""
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    cursor_query_param = 'cursor'
    ordering = '-created_at'  # Default ordering
    
    def get_paginated_response(self, data):
        """Return cursor-paginated response."""
        return Response(OrderedDict([
            ('status', 'success'),
            ('pagination', {
                'page_size': self.get_page_size(self.request),
                'has_next': self.has_next,
                'has_previous': self.has_previous,
            }),
            ('links', {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            }),
            ('data', data),
            ('message', f'Retrieved {len(data)} items using cursor pagination')
        ]))


class SmartPagination:
    """Smart pagination that chooses the best strategy based on context."""
    
    def __init__(self, request, queryset, context: Optional[Dict[str, Any]] = None):
        self.request = request
        self.queryset = queryset
        self.context = context or {}
    
    def get_paginated_response(self, data):
        """Choose and apply the best pagination strategy."""
        # Determine best pagination strategy
        strategy = self._determine_strategy()
        
        if strategy == 'cursor':
            paginator = CursorBasedPagination()
        elif strategy == 'offset':
            paginator = OptimizedLimitOffsetPagination()
        else:
            paginator = CustomPageNumberPagination()
        
        # Apply pagination
        page = paginator.paginate_queryset(self.queryset, self.request)
        if page is not None:
            serialized_data = data if isinstance(data, list) else [data]
            return paginator.get_paginated_response(serialized_data)
        
        return Response({
            'status': 'success',
            'data': data,
            'message': 'Data retrieved without pagination'
        })
    
    def _determine_strategy(self) -> str:
        """Determine the best pagination strategy."""
        # Check for real-time requirements
        if self.context.get('real_time', False):
            return 'cursor'
        
        # Check dataset size
        if hasattr(self.queryset, 'count'):
            count = self.queryset.count()
            if count > 10000:
                return 'cursor'
            elif count > 1000:
                return 'offset'
        
        # Default to page number pagination
        return 'page'


class SearchResultsPagination(CustomPageNumberPagination):
    """Specialized pagination for search results with relevance scoring."""
    
    page_size = 15
    max_page_size = 50
    
    def get_paginated_response(self, data):
        """Return search results with pagination and search metadata."""
        search_query = self.request.query_params.get('q', '')
        search_time = self.context.get('search_time', 0) if hasattr(self, 'context') else 0
        
        return Response(OrderedDict([
            ('status', 'success'),
            ('search_metadata', {
                'query': search_query,
                'search_time_ms': round(search_time * 1000, 2),
                'total_results': self.page.paginator.count,
                'results_per_page': self.get_page_size(self.request),
            }),
            ('pagination', {
                'count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
            }),
            ('links', {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            }),
            ('results', data),
            ('message', f'Found {self.page.paginator.count} results for "{search_query}"')
        ]))


class DashboardPagination(CustomPageNumberPagination):
    """Pagination optimized for dashboard views with summary data."""
    
    page_size = 10
    max_page_size = 25
    
    def get_paginated_response(self, data):
        """Return dashboard data with pagination and summary statistics."""
        summary = self.context.get('summary', {}) if hasattr(self, 'context') else {}
        
        return Response(OrderedDict([
            ('status', 'success'),
            ('summary', summary),
            ('pagination', {
                'count': self.page.paginator.count,
                'current_page': self.page.number,
                'total_pages': self.page.paginator.num_pages,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
            }),
            ('data', data),
            ('message', f'Dashboard page {self.page.number} of {self.page.paginator.num_pages}')
        ]))


class InfinitePagination(LimitOffsetPagination):
    """Pagination for infinite scroll interfaces."""
    
    default_limit = 20
    max_limit = 50
    
    def get_paginated_response(self, data):
        """Return response optimized for infinite scroll."""
        next_offset = None
        if self.get_next_link():
            next_offset = self.get_offset(self.request) + self.get_limit(self.request)
        
        return Response(OrderedDict([
            ('status', 'success'),
            ('has_more': self.get_next_link() is not None,
            ('next_offset': next_offset,
            ('current_offset': self.get_offset(self.request),
            ('limit': self.get_limit(self.request),
            ('data', data),
            ('message', f'Loaded {len(data)} more items')
        ]))


class PerformancePagination(CustomPageNumberPagination):
    """High-performance pagination with caching and optimization."""
    
    page_size = 25
    max_page_size = 100
    
    def __init__(self):
        super().__init__()
        self.cache_timeout = 300  # 5 minutes
        
    def paginate_queryset(self, queryset, request, view=None):
        """Paginate queryset with performance optimizations."""
        # Add select_related and prefetch_related optimizations
        if hasattr(view, 'pagination_select_related'):
            queryset = queryset.select_related(*view.pagination_select_related)
        
        if hasattr(view, 'pagination_prefetch_related'):
            queryset = queryset.prefetch_related(*view.pagination_prefetch_related)
        
        return super().paginate_queryset(queryset, request, view)
    
    def get_paginated_response(self, data):
        """Return response with performance metadata."""
        performance_data = {
            'db_queries': getattr(self, 'db_queries', 0),
            'cache_hits': getattr(self, 'cache_hits', 0),
            'response_time_ms': getattr(self, 'response_time_ms', 0),
        }
        
        response = super().get_paginated_response(data)
        response.data['performance'] = performance_data
        
        return response


class CustomPaginationMixin:
    """Mixin to add custom pagination functionality to ViewSets."""
    
    def get_pagination_context(self):
        """Get context data for pagination."""
        return {}
    
    def paginate_queryset(self, queryset):
        """Paginate queryset with context."""
        if self.paginator is None:
            return None
        
        # Add context to paginator
        if hasattr(self.paginator, 'context'):
            self.paginator.context = self.get_pagination_context()
        
        return self.paginator.paginate_queryset(queryset, self.request, view=self)
    
    def get_paginated_response(self, data):
        """Get paginated response with context."""
        if hasattr(self.paginator, 'context'):
            self.paginator.context = self.get_pagination_context()
        
        return self.paginator.get_paginated_response(data)


def get_pagination_class(pagination_type: str = 'default'):
    """Factory function to get appropriate pagination class."""
    pagination_classes = {
        'default': CustomPageNumberPagination,
        'page': CustomPageNumberPagination,
        'offset': OptimizedLimitOffsetPagination,
        'cursor': CursorBasedPagination,
        'search': SearchResultsPagination,
        'dashboard': DashboardPagination,
        'infinite': InfinitePagination,
        'performance': PerformancePagination,
    }
    
    return pagination_classes.get(pagination_type, CustomPageNumberPagination)


def calculate_pagination_stats(total_count: int, page_size: int, current_page: int) -> Dict[str, Any]:
    """Calculate pagination statistics."""
    total_pages = math.ceil(total_count / page_size) if page_size > 0 else 1
    start_index = (current_page - 1) * page_size + 1 if total_count > 0 else 0
    end_index = min(current_page * page_size, total_count)
    
    return {
        'total_count': total_count,
        'total_pages': total_pages,
        'current_page': current_page,
        'page_size': page_size,
        'start_index': start_index,
        'end_index': end_index,
        'has_next': current_page < total_pages,
        'has_previous': current_page > 1,
        'items_on_page': end_index - start_index + 1 if total_count > 0 else 0,
    }
