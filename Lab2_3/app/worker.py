"""Scheduling worker."""
import os
from celery_base import app
from docker_logs import get_logger

logging = get_logger("worker")


app.conf.beat_schedule = {
    'work_every_n_minutes_new': {
        'task': 'celery_base.submissions',
        'schedule': float(os.environ['CELERYBEAT_MINUTES_INTERVAL']) * 60.0,
        'args': ('worker', 'AskReddit', 50, 'new',
                 float(os.environ['CELERYBEAT_MINUTES_INTERVAL']) * 60.0)
    }
}
app.conf.timezone = 'UTC'
