import os

CELERY_ALWAYS_EAGER = True
if os.environ.setdefault('CELERY_ALWAYS_EAGER', 'true').lower() == 'false':
    CELERY_ALWAYS_EAGER = False
