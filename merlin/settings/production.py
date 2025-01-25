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

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "info-file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/logs/info.log",
            "formatter": "verbose",
            "maxBytes": 1024 * 1024 * 1,
            "backupCount": 1,
        },
        "error-file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/logs/error.log",
            "formatter": "verbose",
            "maxBytes": 1024 * 1024 * 1,
            "backupCount": 1,
        },
        "trace-file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/logs/trace.log",
            "maxBytes": 1024 * 1024 * 1,
            "backupCount": 1,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "tracing": {
            "handlers": ["trace-file"],
            "level": "ERROR",
            "propagate": False,
        },
        "django": {
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "level": "ERROR",
            "propagate": False,
        },
        "django.server": {
            "level": "ERROR",
            "propagate": False,
        },
        "": {
            "handlers": ["info-file", "error-file", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
