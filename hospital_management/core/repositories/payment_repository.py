"""
Payment domain repository implementation.
Handles data access for payment and billing operations.
"""

from typing import Optional, List, Dict, Any
from django.db.models import Q, QuerySet, Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, date, timedelta
from decimal import Decimal
from .base import BaseRepository, CachedRepository
import logging

logger = logging.getLogger(__name__)


class PaymentRepository(CachedRepository):
    """
    Repository for ThanhToan (Payment) model.
    """
    
    def __init__(self):
        from payments.models import ThanhToan
        super().__init__(ThanhToan, cache_timeout=300)  # 5 minutes cache
    
    def find_by_appointment(self, appointment_id: int) -> Optional[Any]:
        """
        Find payment by appointment.
        
        Args:
            appointment_id: Appointment ID
            
        Returns:
            Payment instance or None
        """
        return self.get_all(ma_lich_hen_id=appointment_id).first()
    
    def find_by_status(self, status: str) -> QuerySet:
        """
        Find payments by status.
        
        Args:
            status: Payment status
            
        Returns:
            QuerySet of payments
        """
        return self.get_all(trang_thai=status)
    
    def find_pending_payments(self) -> QuerySet:
        """
        Find all pending payments.
        
        Returns:
            QuerySet of pending payments
        """
        return self.find_by_status('Chua thanh toan')
    
    def find_completed_payments(self, start_date: date = None, 
                              end_date: date = None) -> QuerySet:
        """
        Find completed payments within date range.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            QuerySet of completed payments
        """
        queryset = self.find_by_status('Da thanh toan')
        
        if start_date:
            queryset = queryset.filter(thoi_gian_thanh_toan__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(thoi_gian_thanh_toan__date__lte=end_date)
        
        return queryset.order_by('-thoi_gian_thanh_toan')
    
    def find_by_payment_method(self, method: str) -> QuerySet:
        """
        Find payments by payment method.
        
        Args:
            method: Payment method
            
        Returns:
            QuerySet of payments
        """
        return self.get_all(phuong_thuc=method)
    
    def find_by_transaction_id(self, transaction_id: str) -> Optional[Any]:
        """
        Find payment by transaction ID.
        
        Args:
            transaction_id: Transaction ID
            
        Returns:
            Payment instance or None
        """
        return self.get_all(ma_giao_dich=transaction_id).first()
    
    def get_payment_with_details(self, payment_id: int) -> Optional[Any]:
        """
        Get payment with all related details.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Payment instance with details
        """
        return self.get_queryset().select_related(
            'ma_lich_hen',
            'ma_lich_hen__ma_benh_nhan',
            'ma_lich_hen__ma_bac_si',
            'ma_lich_hen__ma_dich_vu'
        ).filter(pk=payment_id).first()
    
    def process_payment(self, payment_id: int, transaction_id: str, 
                       method: str = None) -> bool:
        """
        Process payment and update status.
        
        Args:
            payment_id: Payment ID
            transaction_id: Transaction ID from payment gateway
            method: Payment method (optional)
            
        Returns:
            True if processed successfully
        """
        try:
            payment = self.get_by_id(payment_id)
            if not payment or payment.trang_thai != 'Chua thanh toan':
                return False
            
            payment.trang_thai = 'Da thanh toan'
            payment.ma_giao_dich = transaction_id
            payment.thoi_gian_thanh_toan = timezone.now()
            
            if method:
                payment.phuong_thuc = method
            
            payment.save()
            
            # Invalidate cache
            self.invalidate_cache('get_by_id', payment_id)
            
            logger.info(f"Payment {payment_id} processed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            return False
    
    def refund_payment(self, payment_id: int, refund_transaction_id: str) -> bool:
        """
        Process payment refund.
        
        Args:
            payment_id: Payment ID
            refund_transaction_id: Refund transaction ID
            
        Returns:
            True if refunded successfully
        """
        try:
            payment = self.get_by_id(payment_id)
            if not payment or payment.trang_thai != 'Da thanh toan':
                return False
            
            payment.trang_thai = 'Da hoan tien'
            payment.ma_giao_dich = f"{payment.ma_giao_dich}_REFUND_{refund_transaction_id}"
            payment.save()
            
            # Invalidate cache
            self.invalidate_cache('get_by_id', payment_id)
            
            logger.info(f"Payment {payment_id} refunded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error refunding payment: {str(e)}")
            return False
    
    def get_payment_statistics(self, start_date: date = None, 
                              end_date: date = None) -> Dict[str, Any]:
        """
        Get payment statistics.
        
        Args:
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            Dictionary with payment statistics
        """
        queryset = self.get_queryset()
        
        if start_date:
            queryset = queryset.filter(thoi_gian_thanh_toan__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(thoi_gian_thanh_toan__date__lte=end_date)
        
        # Overall statistics
        overall_stats = queryset.aggregate(
            total_payments=Count('ma_thanh_toan'),
            total_revenue=Sum('so_tien', filter=Q(trang_thai='Da thanh toan')),
            pending_amount=Sum('so_tien', filter=Q(trang_thai='Chua thanh toan')),
            refunded_amount=Sum('so_tien', filter=Q(trang_thai='Da hoan tien')),
            average_payment=Avg('so_tien', filter=Q(trang_thai='Da thanh toan'))
        )
        
        # Payment method breakdown
        method_stats = queryset.filter(trang_thai='Da thanh toan').values(
            'phuong_thuc'
        ).annotate(
            count=Count('ma_thanh_toan'),
            total=Sum('so_tien')
        )
        
        # Status breakdown
        status_stats = queryset.values('trang_thai').annotate(
            count=Count('ma_thanh_toan'),
            total=Sum('so_tien')
        )
        
        return {
            'total_payments': overall_stats['total_payments'] or 0,
            'total_revenue': float(overall_stats['total_revenue'] or 0),
            'pending_amount': float(overall_stats['pending_amount'] or 0),
            'refunded_amount': float(overall_stats['refunded_amount'] or 0),
            'average_payment': float(overall_stats['average_payment'] or 0),
            'by_method': {
                item['phuong_thuc']: {
                    'count': item['count'],
                    'total': float(item['total'])
                } for item in method_stats
            },
            'by_status': {
                item['trang_thai']: {
                    'count': item['count'],
                    'total': float(item['total'])
                } for item in status_stats
            }
        }
    
    def get_revenue_by_period(self, period: str = 'daily', 
                             days: int = 30) -> List[Dict[str, Any]]:
        """
        Get revenue grouped by time period.
        
        Args:
            period: 'daily', 'weekly', or 'monthly'
            days: Number of days to look back
            
        Returns:
            List of revenue data by period
        """
        from django.db.models import DateField
        from django.db.models.functions import TruncDate, TruncWeek, TruncMonth
        
        start_date = timezone.now().date() - timedelta(days=days)
        
        queryset = self.get_queryset().filter(
            trang_thai='Da thanh toan',
            thoi_gian_thanh_toan__date__gte=start_date
        )
        
        # Choose truncation based on period
        if period == 'weekly':
            trunc_func = TruncWeek('thoi_gian_thanh_toan')
        elif period == 'monthly':
            trunc_func = TruncMonth('thoi_gian_thanh_toan')
        else:  # daily
            trunc_func = TruncDate('thoi_gian_thanh_toan')
        
        revenue_data = queryset.annotate(
            period_date=trunc_func
        ).values('period_date').annotate(
            count=Count('ma_thanh_toan'),
            total=Sum('so_tien')
        ).order_by('period_date')
        
        return [
            {
                'date': item['period_date'],
                'count': item['count'],
                'total': float(item['total'])
            } for item in revenue_data
        ]
    
    def get_outstanding_payments(self, days_overdue: int = 7) -> QuerySet:
        """
        Get outstanding payments that are overdue.
        
        Args:
            days_overdue: Number of days to consider as overdue
            
        Returns:
            QuerySet of overdue payments
        """
        overdue_date = timezone.now().date() - timedelta(days=days_overdue)
        
        return self.get_queryset().filter(
            trang_thai='Chua thanh toan',
            ma_lich_hen__ngay_kham__lte=overdue_date
        ).select_related(
            'ma_lich_hen',
            'ma_lich_hen__ma_benh_nhan'
        ).order_by('ma_lich_hen__ngay_kham')
    
    def get_patient_payment_history(self, patient_id: int) -> QuerySet:
        """
        Get payment history for a patient.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            QuerySet of patient's payments
        """
        return self.get_queryset().filter(
            ma_lich_hen__ma_benh_nhan_id=patient_id
        ).select_related(
            'ma_lich_hen',
            'ma_lich_hen__ma_dich_vu'
        ).order_by('-thoi_gian_thanh_toan')
    
    def calculate_patient_balance(self, patient_id: int) -> Dict[str, float]:
        """
        Calculate patient's payment balance.
        
        Args:
            patient_id: Patient ID
            
        Returns:
            Dictionary with balance information
        """
        payments = self.get_patient_payment_history(patient_id)
        
        stats = payments.aggregate(
            total_billed=Sum('so_tien'),
            total_paid=Sum('so_tien', filter=Q(trang_thai='Da thanh toan')),
            total_pending=Sum('so_tien', filter=Q(trang_thai='Chua thanh toan')),
            total_refunded=Sum('so_tien', filter=Q(trang_thai='Da hoan tien'))
        )
        
        return {
            'total_billed': float(stats['total_billed'] or 0),
            'total_paid': float(stats['total_paid'] or 0),
            'total_pending': float(stats['total_pending'] or 0),
            'total_refunded': float(stats['total_refunded'] or 0),
            'balance': float((stats['total_pending'] or 0))
        }
