from .base import *  # noqa

DEBUG = True
# Run Celery tasks synchronously in dev/CI — no Redis worker needed
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
