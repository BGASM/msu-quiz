import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO
from celery import Celery
from . import celeryconfig
from .config import config
from itsdangerous import URLSafeTimedSerializer
ts = URLSafeTimedSerializer(os.environ.get('SECRET_KEY'))

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
socketio = SocketIO()
bcrypt = Bcrypt()
celery = Celery(__name__, broker=celeryconfig.broker_url,
                backend=celeryconfig.result_backend)

from .models.models import User, Quiz, Question, Exam
from . import events  # noqa


def create_app(config_name=None, main=True):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    bcrypt.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    migrate.init_app(app, db)


    from .views.quiz import quiz_bp
    app.register_blueprint(quiz_bp)

    from .views.auth import auth_bp
    app.register_blueprint(auth_bp)

    from .views.quiz import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')


    if main:
        # Initialize socketio server and attach it to the message queue, so
        # that everything works even when there are multiple servers or
        # additional processes such as Celery workers wanting to access
        # Socket.IO
        socketio.init_app(app,
                          message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'], logger=True, engineio_logger=True)
    else:
        # Initialize socketio to emit events through through the message queue
        # Note that since Celery does not use eventlet, we have to be explicit
        # in setting the async mode to not use it.
        socketio.init_app(None,
                          message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'],
                          async_mode='threading', logger=True, engineio_logger=True)
        #celery.conf.update(app.config)
    return app
