import os
from . import socketio, celery
from celery.utils.log import get_task_logger
from .models.models import User
import functools
from flask import request, jsonify
from flask import current_app
from flask_login import current_user
from flask_socketio import disconnect, emit, SocketIO



def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


def push_msg(msg):
    print('In push/emit method.')
    socketio.emit('incoming msg', msg, broadcast=True)


@socketio.on('connect')
def connect_handler():
    if current_user.is_authenticated:
        print('About to broadcast a new user!')
        emit('my response',
             {'message': '{0} has joined'.format(current_user.name)},
             broadcast=True)
    else:
        return False  # not allowed here


@socketio.on('post_message')
@authenticated_only
def on_post_message(message):
    print(f'In post message event. {current_user.name} and {message}')
    print(celery)
    result = post_message.delay(current_user.name, message)
    print(result)


@celery.task(name='events.post_message')
def post_message(user_id, data):
    """Celery task that posts a message."""
    user = user_id
    local_sock = SocketIO(message_queue=os.environ.get('REDIS_URL'))

    local_sock.emit('incoming message', {'user_name': user, 'message': data['message']})
    #from .aux_service import app
    #with app.app_context():
    #    msg = {'user_name': user, 'message': data['message']}
    #    push_msg(msg)

