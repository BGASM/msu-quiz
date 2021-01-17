import os
from loguru import logger
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])
    db.init_app(app)
    from .models import MCQ, Question, Quiz, User
    migrate.init_app(app, db)
    return app
'''
    with app.app_context():
        from .quiz import routes
        from .auth import routes
        app.register_blueprint(quiz.quiz_bp)
        app.register_blueprint(auth.auth_bp)
'''

