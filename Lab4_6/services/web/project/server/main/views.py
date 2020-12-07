"""View of application."""
import redis
from rq import Queue, push_connection, pop_connection
from flask import current_app, render_template, Blueprint, jsonify, request

from server.main.tasks import (
    load_submissions,
    train_all_models, test_all_models
)

main_blueprint = Blueprint('main', __name__,)


@main_blueprint.route('/', methods=['GET'])
def home():
    """Home view."""
    return render_template('main/home.html')


@main_blueprint.route('/trainAll', methods=['GET'])
def train_all():
    """Train all - view."""
    q = Queue()
    task = q.enqueue(train_all_models)
    response_object = {
        'status': 'success',
        'data': {
            'task_id': task.get_id()
        }
    }
    return jsonify(response_object), 202


@main_blueprint.route('/mongo', methods=['GET'])
def run_mongo():
    """Run Mongo - view."""
    q = Queue()
    task = q.enqueue(load_submissions)
    response_object = {
        'status': 'success',
        'data': {
            'task_id': task.get_id()
        }
    }
    return jsonify(response_object), 202


@main_blueprint.route('/testModels', methods=['POST'])
def test_models():
    """Test models - view."""
    text = request.form['text']
    q = Queue()
    task = q.enqueue(test_all_models, text)
    response_object = {
        'status': 'success',
        'data': {
            'task_id': task.get_id()
        }
    }
    return jsonify(response_object), 202


@main_blueprint.route('/tasks/<task_id>', methods=['GET'])
def get_status(task_id):
    """Get status - view."""
    q = Queue()
    task = q.fetch_job(task_id)
    if task:
        response_object = {
            'status': 'success',
            'data': {
                'task_id': task.get_id(),
                'task_status': task.get_status(),
                'task_result': task.result,
            }
        }
    else:
        response_object = {'status': 'error'}
    return jsonify(response_object)


@main_blueprint.before_request
def push_rq_connection():
    """Push rq connection - view."""
    push_connection(redis.from_url(current_app.config['REDIS_URL']))


@main_blueprint.teardown_request
def pop_rq_connection(exception=None):
    """Pop rq connection - view."""
    pop_connection()
