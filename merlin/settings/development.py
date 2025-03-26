from decouple import config 
from merlin.settings.base import *

DEBUG = config('DEBUG', default=True, cast=bool)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('MERLIN_DATABASE_NAME', default='merlin'),
        'USER': config('MERLIN_DATABASE_USER', default='merlin_user'),
        'PASSWORD': config('MERLIN_DATABASE_PASSWORD', default='merlin_psql'),
        'HOST': config('MERLIN_DATABASE_HOST', default='localhost'),
        'PORT': config('MERLIN_DATABASE_PORT', default=5432, cast=int),
        "OPTIONS": {
            "connect_timeout": 60,
        },
    },
}

CELERY_BROKER_URL = 'redis://localhost:6379/0'
