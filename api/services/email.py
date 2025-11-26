from django.conf import settings
from api.models import User, EmailTrigger
from api.utils.email import build_dynamic_context, replace_placeholders


__all__ = [
    'send_email',
    'send_bulk_emails',
    'notify_mentioned_users',
]


def send_email(event_type, user, **kwargs):
    """
    Send the email asynchronously using Celery.
    Side effect: Triggers Celery task (mutation).
    
    Args:
        event_type (str): The event type that triggers the email.
        user (User): The user to send the email to.
        **kwargs: Additional context data for template rendering.
    """
    from merlin.celery import app as celery_app
    
    celery_app.send_task(
        'api.tasks.send_dynamic_email_task',
        args=[event_type, user.id, kwargs],
        countdown=1
    )


def send_bulk_emails(event_type, users_queryset):
    """
    Sends notifications to each user individually, with personalized context.
    Side effect: Orchestrates multiple email sends (mutation).
    
    Args:
        event_type (str): The event triggering the email.
        users_queryset (QuerySet): A queryset of User objects.
    """
    trigger = EmailTrigger.objects.get(event_type=event_type)
    placeholders = trigger.placeholders
    
    for user in users_queryset:
        # Build personalized context for this user dynamically based on the template
        context = build_dynamic_context(user, placeholders)
        send_email(event_type, user, **context)


# def notify_all_employees_for_new_appraisal_cycle():
#     """
#     Business logic: Notify all employees when a new appraisal cycle starts.
#     Side effect: Sends emails to all employees (mutation).
#     """
#     # Fetch the trigger based on the event type
#     try:
#         trigger = EmailTrigger.objects.get(event_type="new_appraisal_cycle_started")
#         template = trigger.template
#         subject = template.subject
#         body = template.body
#     except EmailTrigger.DoesNotExist:
#         raise Exception("Email trigger for new appraisal cycle does not exist.")
    
#     # Fetch all employees to notify
#     employees = User.objects.all()

#     # Build the context for the email body (if needed, add dynamic values)
#     context = {
#         "employee_names": [emp.name for emp in employees],
#     }

#     final_body = replace_placeholders(body, context)

#     recipients = [emp.email for emp in employees]
    
#     # Use Django's send_mail directly for bulk sending without personalization
#     from django.core.mail import send_mail
#     from django.conf import settings
    
#     send_mail(
#         subject,
#         final_body,
#         settings.EMAIL_HOST_USER,
#         recipients,
#         fail_silently=False,
#     )


def notify_mentioned_users(note, mentioned_user_ids):
    """
    Send email notifications to users when they are mentioned in a note.
    Side effect: Sends emails to mentioned users (mutation).
    
    Args:
        note: The Note instance where users were mentioned.
        mentioned_user_ids: List of user IDs that were just added to mentions.
    """
    # Get the users that were mentioned
    mentioned_users = User.objects.filter(id__in=mentioned_user_ids)
    
    # Skip if note was created during import (to prevent spam)
    if hasattr(note, '_skip_access_grants') and note._skip_access_grants:
        return
    
    # Skip if note is marked as import
    if getattr(note, 'is_import', False):
        return
    
    # Get frontend URL from settings or use default
    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    
    # Construct note URL based on note type
    note_url = _get_note_url(note, frontend_url)
    
    # Send email to each mentioned user
    for user in mentioned_users:
        # Skip if user is the note owner (they don't need notification for their own note)
        if user.id == note.owner_id:
            continue
        
        # Build context for email template
        context = {
            'user_name': user.name or user.email,
            'note_title': note.title,
            'note_owner': note.owner.name or note.owner.email,
            'note_type': note.get_type_display(),
            'note_url': note_url,
        }
        
        send_email('user_mentioned', user, **context)


def _get_note_url(note, frontend_url):
    """
    Construct the frontend URL for a note based on its type.
    
    Args:
        note: The Note instance
        frontend_url: Base URL of the frontend application
        
    Returns:
        str: Full URL to the note
    """
    from api.models import NoteType
    
    # Remove trailing slash from frontend_url
    base_url = frontend_url.rstrip('/')
    
    # Map note types to URL patterns
    if note.type == NoteType.ONE_ON_ONE:
        # One-on-one notes have special URL structure
        if hasattr(note, 'one_on_one') and note.one_on_one:
            return f"{base_url}/one-on-one/{note.one_on_one.member.uuid}/{note.uuid}"
        return f"{base_url}/notes/one-on-one/{note.uuid}"
    
    elif note.type == NoteType.FEEDBACK_REQUEST:
        # Feedback request has special URL
        if hasattr(note, 'feedback_request') and note.feedback_request:
            return f"{base_url}/feedback/{note.feedback_request.uuid}"
        return f"{base_url}/notes/feedback-request/{note.uuid}"
    
    elif note.type == NoteType.FEEDBACK:
        # Feedback (ad-hoc) has special URL
        if hasattr(note, 'feedback') and note.feedback:
            return f"{base_url}/adhoc-feedback/{note.feedback.uuid}"
        return f"{base_url}/notes/feedback/{note.uuid}"
    
    elif note.type == NoteType.Template:
        return f"{base_url}/templates/{note.uuid}"
    
    else:
        # Default: /notes/[type]/[uuid]
        # Map note type to URL-friendly format
        type_map = {
            NoteType.GOAL: 'goal',
            NoteType.MEETING: 'meeting',
            NoteType.Personal: 'personal',
            NoteType.TASK: 'task',
            NoteType.Proposal: 'proposal',
            NoteType.Message: 'message',
        }
        note_type_slug = type_map.get(note.type, 'note')
        return f"{base_url}/notes/{note_type_slug}/{note.uuid}"