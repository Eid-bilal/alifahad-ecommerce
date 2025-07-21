# celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alifahad_perfumes.settings')

app = Celery('alifahad_perfumes')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
# should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Update for Windows support with solo pool
app.conf.update(
    task_create_missing_queues=True,
    task_serializer='json',
    result_backend='django-db',  # or use Redis, depending on your choice
    broker='redis://localhost:6379/0',  # Your broker URL
    backend='redis://localhost:6379/0',  # Your backend URL
    worker_pool='solo',  # Use solo pool for Windows
    broker_connection_retry_on_startup=True,  # Add this line to address the warning
)

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
