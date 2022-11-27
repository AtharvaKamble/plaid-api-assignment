import os
from celery import Celery

# Celery configuration

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "assignment.settings")
app = Celery("assignment", broker=os.environ.get(
    'REDIS_ENDPOINT'), backend=os.environ.get('REDIS_ENDPOINT'))

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
