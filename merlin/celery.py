from __future__ import absolute_import, unicode_literals
import os
import django
from celery import Celery
from celery.schedules import crontab

# Use the DJANGO_SETTINGS_MODULE environment variable if set, otherwise default to development
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'merlin.settings.development'))

django.setup()

app = Celery('merlin')
app.config_from_object('django.conf:settings', namespace='CELERY') # Means all celery-related config keys should have a `CELERY_` prefix

app.conf.beat_schedule = {
    # I can add scheduled tasks here in the future.
    # Example (leave commented for now):
    # 'send-reminder-every-morning': {
    #     'task': 'api.email_notifications.tasks.send_pending_request_reminders',
    #     'schedule': crontab(hour=7, minute=0),
    # },
}

app.autodiscover_tasks(['api.email_notifications'])

