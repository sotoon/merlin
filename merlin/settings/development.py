from merlin.settings.base import *

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "merlin",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": os.environ.get("DATABASE_HOST", "localhost"),
        "PORT": "5432",
        "OPTIONS": {
            "connect_timeout": 60,
        },
    },
}
