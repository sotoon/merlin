from merlin.celery import app as celery_app

from ..email_notifications.template_helpers import build_dynamic_context
from ..models.email import EmailTrigger

__all__ = ['send_email', 'send_bulk_emails']

# Here, we have the email sending mechanisms

def send_email(event_type, user, **kwargs):
    """
    Send the email asynchronously using Celery.
    """
    celery_app.send_task(
        'api.email_notifications.tasks.send_dynamic_email_task',
        args=[event_type, user.id, kwargs],
        countdown=1
    )


def send_bulk_emails(event_type, users_queryset):
    """
    Sends notifications to each user individually, with personalized context.
    
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

