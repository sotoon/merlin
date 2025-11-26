from __future__ import absolute_import, unicode_literals
import os
import django
from celery import Celery

# Use the DJANGO_SETTINGS_MODULE environment variable if set, otherwise default to development
# Set the DJANGO_SETTINGS_MODULE in the production environment
os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE', os.environ.get('DJANGO_SETTINGS_MODULE', 'merlin.settings.development'))

django.setup()

app = Celery('merlin')

app.config_from_object('django.conf:settings', namespace='CELERY') # Means all celery-related config keys should have a `CELERY_` prefix

app.autodiscover_tasks(['api'])
