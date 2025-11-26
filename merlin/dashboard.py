"""
Custom dashboard callback for Django Unfold admin panel.
This replaces the redundant sidebar duplication with useful statistics and information.
"""
from django.utils import timezone
from django.contrib.sessions.models import Session
from datetime import timedelta, datetime
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

from api.models import (
    User,
    Note,
    Feedback,
    FeedbackRequest,
    Form,
    FormAssignment,
    Department,
    Cycle,
    ApiKey,
)
from api.models.note import NoteType, ProposalType, NoteSubmitStatus
from api.utils.performance_tables import get_persian_year_bounds_gregorian
from persiantools.jdatetime import JalaliDate
from datetime import date as date_class


def dashboard_callback(request, context):
    """
    Custom dashboard callback for Unfold admin panel.
    Returns context with statistics and recent activity widgets.
    """
    # Initialize default values first
    default_context = {
        'total_users': 0,
        'total_notes': 0,
        'total_feedback': 0,
        'total_feedback_requests': 0,
        'total_forms': 0,
        'total_cycles': 0,
        'total_departments': 0,
        'active_api_keys': 0,
        'recent_notes': 0,
        'recent_feedback': 0,
        'recent_users': 0,
        'latest_notes': [],
        'latest_users': [],
        'total_logins_this_week': 0,
        'avg_logins_per_day': 0,
        'unique_logins_this_week': 0,
        'proposals_by_type': {},
        'proposals_by_status_total': {},
        'proposals_by_status_week': {},
        'proposals_by_status_month': {},
        'proposal_types': [],
        'proposal_statuses': [],
        'pending_proposals': 0,
        'reviewed_proposals_this_week': 0,
        'reviewed_proposals_this_month': 0,
        'recent_proposals': [],
        'pending_forms': 0,
        'completed_forms': 0,
        'current_cycle_name': "هیچ دوره فعالی وجود ندارد",
    }
    
    try:
        # Try to get proposal types and statuses early
        try:
            default_context['proposal_types'] = ProposalType.choices
            default_context['proposal_statuses'] = NoteSubmitStatus.choices
        except Exception as e:
            logger.error(f"Error loading proposal types/statuses: {e}", exc_info=True)
        
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        
        # Get counts for major models
        total_users = User.objects.count()
        total_notes = Note.objects.count()
        total_feedback = Feedback.objects.count()
        total_feedback_requests = FeedbackRequest.objects.count()
        total_forms = Form.objects.count()
        total_cycles = Cycle.objects.count()
        total_departments = Department.objects.count()
        active_api_keys = ApiKey.objects.filter(is_active=True).count()
        
        # Recent activity (last 7 days)
        recent_notes = Note.objects.filter(date_created__gte=week_ago).count()
        recent_feedback = Feedback.objects.filter(date_created__gte=week_ago).count()
        recent_users = User.objects.filter(date_created__gte=week_ago).count()
        
        # Get latest items for quick access (increased to 10 for notes)
        latest_notes = Note.objects.select_related('owner', 'cycle').order_by('-date_created')[:10]
        latest_users = User.objects.order_by('-date_created')[:5]
        
        # Login statistics using User.last_login
        # Now tracking main app logins via LoginView and BepaCallbackView updates to last_login
        users_logged_in_this_week = User.objects.filter(
            last_login__gte=week_ago
        ).exclude(last_login__isnull=True)
        
        # Count unique users who logged in this week
        unique_logins_this_week = users_logged_in_this_week.count()
        
        # For total logins, we approximate by counting users who logged in multiple times
        # Since we track by last_login, we can count how many times users logged in
        # by checking sessions or using a different metric. For now, we'll use unique users
        # as total (since each unique login represents at least one login)
        # In a production system, you might want to track actual login events
        
        # Count active sessions as an approximation of total login activity
        active_sessions_with_users = 0
        try:
            active_sessions = Session.objects.filter(expire_date__gte=now)
            for session in active_sessions:
                try:
                    session_data = session.get_decoded()
                    if session_data.get('_auth_user_id'):
                        active_sessions_with_users += 1
                except Exception:
                    pass
        except Exception:
            pass
        
        # Total logins is approximate - use active sessions or unique users (whichever is higher)
        total_logins_this_week = max(unique_logins_this_week, active_sessions_with_users)
        
        # Calculate averages
        days_in_week = 7
        avg_logins_per_day = round(total_logins_this_week / days_in_week, 1) if days_in_week > 0 else 0
        
        # Proposals statistics
        proposals = Note.objects.filter(type=NoteType.Proposal)
        
        # Get Persian calendar month boundaries with error handling
        try:
            today_greg = now.date()
            jalali_today = JalaliDate.to_jalali(today_greg)
            # First day of current Persian month
            month_start_greg = JalaliDate(jalali_today.year, jalali_today.month, 1).to_gregorian()
            # Last day of current Persian month
            if jalali_today.month == 12:
                # If it's the last month, calculate next year's first month
                next_month_start = JalaliDate(jalali_today.year + 1, 1, 1).to_gregorian()
            else:
                next_month_start = JalaliDate(jalali_today.year, jalali_today.month + 1, 1).to_gregorian()
            month_end_greg = next_month_start - timedelta(days=1)
            month_start = timezone.make_aware(datetime.combine(month_start_greg, datetime.min.time()))
            month_end = timezone.make_aware(datetime.combine(month_end_greg, datetime.max.time()))
        except Exception as e:
            logger.error(f"Error calculating Persian calendar dates: {e}", exc_info=True)
            # Fallback to current month in Gregorian calendar
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = (now.replace(day=1) + timedelta(days=32)).replace(day=1)
            month_end = next_month - timedelta(days=1)
        
        # Proposals by type
        proposals_by_type = defaultdict(int)
        for proposal_type in ProposalType.choices:
            proposals_by_type[proposal_type[0]] = proposals.filter(proposal_type=proposal_type[0]).count()
        
        # Proposals by status - TOTAL
        proposals_by_status_total = defaultdict(dict)
        pending_proposals = 0
        
        for status_code, status_label in NoteSubmitStatus.choices:
            count = proposals.filter(submit_status=status_code).count()
            proposals_by_status_total[status_code] = {
                'count': count,
                'label': status_label
            }
            if status_code == NoteSubmitStatus.PENDING:
                pending_proposals = count
        
        # Proposals by status - THIS WEEK
        proposals_by_status_week = defaultdict(dict)
        for status_code, status_label in NoteSubmitStatus.choices:
            count = proposals.filter(
                submit_status=status_code,
                date_updated__gte=week_ago
            ).count()
            proposals_by_status_week[status_code] = {
                'count': count,
                'label': status_label
            }
        
        # Proposals by status - THIS MONTH (Persian calendar)
        proposals_by_status_month = defaultdict(dict)
        for status_code, status_label in NoteSubmitStatus.choices:
            count = proposals.filter(
                submit_status=status_code,
                date_updated__gte=month_start,
                date_updated__lte=month_end
            ).count()
            proposals_by_status_month[status_code] = {
                'count': count,
                'label': status_label
            }
        
        # Proposals reviewed this week
        reviewed_this_week = proposals.filter(
            submit_status=NoteSubmitStatus.REVIEWED,
            date_updated__gte=week_ago
        ).count()
        
        # Proposals reviewed this month
        reviewed_this_month = proposals.filter(
            submit_status=NoteSubmitStatus.REVIEWED,
            date_updated__gte=month_start,
            date_updated__lte=month_end
        ).count()
        
        # Get recent proposals (latest 20 for filtering)
        recent_proposals = proposals.select_related('owner', 'cycle').order_by('-date_updated')[:20]
        
        # Pending/completed items
        pending_forms = FormAssignment.objects.filter(is_completed=False).count()
        completed_forms = FormAssignment.objects.filter(is_completed=True).count()
        
        # Active cycle info
        try:
            current_cycle = Cycle.objects.filter(is_active=True).order_by('-start_date').first()
            current_cycle_name = current_cycle.name if current_cycle else "هیچ دوره فعالی وجود ندارد"
        except Exception:
            current_cycle_name = "هیچ دوره فعالی وجود ندارد"
        
        # Add statistics to context
        context.update({
            # Total counts
            'total_users': total_users,
            'total_notes': total_notes,
            'total_feedback': total_feedback,
            'total_feedback_requests': total_feedback_requests,
            'total_forms': total_forms,
            'total_cycles': total_cycles,
            'total_departments': total_departments,
            'active_api_keys': active_api_keys,
            
            # Recent activity
            'recent_notes': recent_notes,
            'recent_feedback': recent_feedback,
            'recent_users': recent_users,
            
            # Latest items
            'latest_notes': latest_notes,
            'latest_users': latest_users,
            
            # Login statistics
            'total_logins_this_week': total_logins_this_week,
            'avg_logins_per_day': round(avg_logins_per_day, 1),
            'unique_logins_this_week': unique_logins_this_week,
            
            # Proposals statistics
            'proposals_by_type': dict(proposals_by_type),
            'proposals_by_status_total': dict(proposals_by_status_total),
            'proposals_by_status_week': dict(proposals_by_status_week),
            'proposals_by_status_month': dict(proposals_by_status_month),
            'proposal_types': ProposalType.choices,  # For template iteration
            'proposal_statuses': NoteSubmitStatus.choices,  # For template iteration
            'pending_proposals': pending_proposals,
            'reviewed_proposals_this_week': reviewed_this_week,
            'reviewed_proposals_this_month': reviewed_this_month,
            'recent_proposals': recent_proposals,
            
            # Form statistics
            'pending_forms': pending_forms,
            'completed_forms': completed_forms,
            
            # Cycle info
            'current_cycle_name': current_cycle_name,
        })
    except Exception as e:
        logger.error(f"Error in dashboard_callback: {e}", exc_info=True)
        # Use pre-initialized default values
        context.update(default_context)
    
    return context

