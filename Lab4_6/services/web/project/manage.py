"""App manager."""
import random
import string as s

import redis
from rq import Connection, Worker
from flask_script import Manager
from docker_logs import get_logger

from server import app


manager = Manager(app)
logging = get_logger('spark-worker')


@manager.command
def run_worker():
    """Launches worker and establishes connection via Redis."""
    worker_name = ''.join((random.choice(s.ascii_letters + s.digits)
                          for i in range(12)))

    redis_url = app.config['REDIS_URL']
    redis_connection = redis.from_url(redis_url)
    with Connection(redis_connection):
        worker = Worker(app.config['QUEUES'], name=worker_name)
        worker.work()


if __name__ == '__main__':
    manager.run()
