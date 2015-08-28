import os

ASYNC_ENABLED = os.environ.setdefault('ASYNC_ENABLED',
                                      'false').lower() == 'true'
if ASYNC_ENABLED:
    CELERY_ALWAYS_EAGER = False
else:
    CELERY_ALWAYS_EAGER = True
