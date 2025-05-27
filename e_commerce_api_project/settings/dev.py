from .base import *
import sys

from decouple import config
import logging

logger = logging.getLogger(__name__)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

is_testing = (
    'test' in sys.argv or
    'pytest' in sys.argv or
    'PYTEST_CURRENT_TEST' in os.environ or
    os.environ.get('DJANGO_DATABASE_URL') == 'sqlite:///:memory:' or
    any('pytest' in arg for arg in sys.argv)
)
if is_testing:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
    logger.info(f"Using SQLite for tests: {DATABASES['default']}")
else:
    logger.info(f"Using Postgres: {DATABASES['default']}")

logger.debug("sys.argv:", sys.argv)
logger.debug("PYTEST_CURRENT_TEST:", os.environ.get('PYTEST_CURRENT_TEST'))

SWAGGER_USE_COMPAT_RENDERERS = False

CORS_ALLOW_ALL_ORIGINS = True

DEBUG = True

# ALLOWED_HOSTS = ['localhost', '127.0.0.1','testserver' ]
ALLOWED_HOSTS = ['*' ]

CACHES = {
      'default': {
          'BACKEND': 'django_redis.cache.RedisCache',
          'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
          'OPTIONS': {
              'CLIENT_CLASS': 'django_redis.client.DefaultClient',
          }
      }
  }
