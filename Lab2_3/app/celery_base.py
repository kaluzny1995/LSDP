"""Base of all celery processes."""
from celery import Celery
from kombu import Queue
from influxdb import InfluxDBClient

from datetime import datetime, timedelta
from docker_logs import get_logger
from embedder import embedding
from scraper import get_submissions
from influxdb_scripts import create_db, insert_submissions
logging = get_logger("celery_base")

app = Celery('celery_base', broker='amqp://localhost//', backend='amqp')
db_client = InfluxDBClient(host="database", port=8086)

app.conf.task_default_queue = 'default'
app.conf.task_queues = (
    Queue('default', routing_key='worker.#'),
    Queue('embedding_tasks', routing_key='embedder.#'),
    Queue('mongodb_tasks', routing_key='mongodb_worker.#')
)


@app.task(bind=True)
def submissions(self, work, topic, count, type, interval):
    """Scraps submissions given params."""
    submissions = get_submissions(topic, count, type)
    last_submission_time = datetime.now() - timedelta(0, interval)
    submissions = [subm for subm in submissions if datetime.fromtimestamp(
        int(subm['time'])) > last_submission_time]
    logging.info(f'{work}: Submission fetched: {len(submissions)}')

    if len(submissions) > 0:
        embedding.apply_async(args=['embedder', submissions],
                              queue='embedding_tasks')

    db_name = 'celery'
    if db_name not in [db['name'] for db in db_client.get_list_database()]:
        create_db(db_client, db_name)
        logging.info(f'{work}: Database created: {db_name}')
    insert_submissions(db_client, db_name, submissions)
    return submissions
