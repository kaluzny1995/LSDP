"""Scheduling worker."""
from celery_base import app
from docker_logs import get_logger

logging = get_logger("worker")


app.conf.beat_schedule = {
    'work_every_20_minutes_new': {
        'task': 'celery_base.submissions',
        'schedule': 10 * 60.0,
        'args': ('worker', 'AskReddit', 50, 'new', 10 * 60.0)
    }
}
app.conf.timezone = 'UTC'
