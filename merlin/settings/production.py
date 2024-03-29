from merlin.settings.base import *

DEBUG = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("MERLIN_DATABASE_NAME", ""),
        "USER": os.environ.get("MERLIN_DATABASE_USER", ""),
        "PASSWORD": os.environ.get("MERLIN_DATABASE_PASSWORD", ""),
        "HOST": os.environ.get("MERLIN_DATABASE_HOST", ""),
        "PORT": "5432",
        "OPTIONS": {
            "connect_timeout": 60,
        },
    },
}
