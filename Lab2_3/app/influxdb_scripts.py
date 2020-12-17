"""Influxdb management scripts."""
from datetime import datetime


def create_db(client, db_name):
    """Creates Influx database."""
    client.create_database(db_name)


def insert_submissions(client, db_name, submissions):
    """Insert submission into database."""
    client.switch_database(db_name)
    task_records = [
        {
            "measurement": "tasks",
            "tags": {
                "tag": submission['id']
            },
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fields": {
                'id': submission['id'],
                'author': submission['author'],
                'score': submission['score'],
                'upvote_ratio': submission['upvote_ratio'],
                'time': datetime.fromtimestamp(int(submission['time'])).
                strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        for submission in submissions]
    client.write_points(task_records)
