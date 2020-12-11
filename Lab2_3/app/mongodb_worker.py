"""Mongodb management worker."""
from celery import Celery
from docker_logs import get_logger
from pymongo import MongoClient

logging = get_logger("mongodb_worker")
app = Celery('celery_base', broker='amqp://localhost//', backend='amqp')
mongo_client = MongoClient(host='mongodb', port=27017)


@app.task(bind=True)
def save_submission(self, work, submission):
    """Saves submission do Mongo database."""
    db = mongo_client.reddits
    col = db.submissions
    s_id = col.insert(submission)
    logging.warning(f'{work}: Submission saved: {s_id}')
