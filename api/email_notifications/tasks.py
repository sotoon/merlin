import datetime
from django.core.mail import send_mail
from django.conf import settings

from celery import shared_task

from .models import EmailTrigger, EmailLog
from api.models import User
from .template_helpers import replace_placeholders

# Here, we have the Celery task management logic

@shared_task
def send_dynamic_email_task(event_type, user_id, context, **kwargs):
    """
    Task to send email asynchronously. This will replace placeholders and send the email.
    """
    user  = User.objects.get(id=user_id)

    try:
        trigger = EmailTrigger.objects.get(event_type=event_type)
        template_obj = trigger.template
    except EmailTrigger.DoesNotExist:
        return
    
    subject = replace_placeholders(template_obj.subject, context)
    body = replace_placeholders(template_obj.body, context)

    # Initialize the EmailLog
    email_log = EmailLog.objects.create(
        event_type=event_type,
        user=user,
        email_template=template_obj,
        subject=subject,
        body=body,
        status = "Pending"
    )

    try:
        sent_count = send_mail(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
    
        if sent_count:
            email_log.status="Sent"
            email_log.sent_at=datetime.datetime.now()
        else:
            email_log.status="Failed"
            email_log.error_message="api.email_notifications.tasks.send_mail returned zero sent emails."

    except Exception as e:
        email_log.status="Failed"
        email_log.error_message=str(e)
    
    email_log.save()