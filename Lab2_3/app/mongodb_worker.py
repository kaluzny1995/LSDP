"""Mongodb management worker."""
import os
from celery import Celery
from docker_logs import get_logger
from pymongo import MongoClient

logging = get_logger("mongodb_worker")
app = Celery('celery_base', broker='amqp://localhost//', backend='amqp')
mongo_client = MongoClient(host=os.environ['MONGODB_HOST'],
                           port=int(os.environ['MONGODB_PORT']))


@app.task(bind=True)
def save_submission(self, work, submission):
    """Saves submission do Mongo database."""
    try:
        db = mongo_client.reddits
        col = db.submissions
        s_id = col.insert(submission)
        logging.info(f'{work}: Submission saved into MongoDB: {s_id}')
    except Exception as e:
        logging.error(f'{work}: MongoDB saving error: {e}')
