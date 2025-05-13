from .base import *
import sys

from decouple import config


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

if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }

CORS_ALLOW_ALL_ORIGINS = True

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

CACHES = {
      'default': {
          'BACKEND': 'django_redis.cache.RedisCache',
          'LOCATION': os.getenv('REDIS_URL', 'redis://127.0.0.1:6379/1'),
          'OPTIONS': {
              'CLIENT_CLASS': 'django_redis.client.DefaultClient',
          }
      }
  }

CACHEOPS = {
    'orders.*': {'ops': 'all', 'timeout': 60*60},
    'products.*': {'ops': 'all', 'timeout': 60*60},
    'analytics.*': {'ops': 'all', 'timeout': 60*60},
}