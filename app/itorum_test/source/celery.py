import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'source.settings')

app = Celery('source')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.beat_schedule = {
    'check-event-status': {
         'task': 'check-event-status',
         'schedule': crontab(minute='*/15'),
     },
    'send-notice-before-event': {
         'task': 'send-notice-before-event',
         'schedule': crontab(hour='*/3'),
    },
}
app.conf.timezone = 'UTC'