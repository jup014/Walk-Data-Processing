import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'walk_data_processing.settings')

app = Celery('walk_data_processing')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.result_expires = None
app.conf.worker_prefetch_multiplier = 1
app.conf.broker_url = "amqp://guest@rabbitmq:5672"
app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"

app.conf.task_default_queue = 'default'