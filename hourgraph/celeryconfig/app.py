import os
from celery import Celery
from celery.schedules import crontab
from . import tasks

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

celery = Celery('hourgraph')
celery.config_from_object('django.conf:settings', namespace='CELERY')
celery.autodiscover_tasks()

celery.conf.beat_schedule = {
    'check-lesson-status': {
        'task': 'celeryconfig.tasks.check_lesson_status',
        'schedule': crontab(minute='*'),
    },
}