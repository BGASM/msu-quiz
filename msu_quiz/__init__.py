import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()

def get_config():
    app = Flask(__name__)
    app.config.from_object(os.environ['APP_SETTINGS'])
    return app.config


def create_app():
    app = Flask(__name__)
    base_config = get_config()
    app.config.update(base_config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from .models.models import User, Quiz, MCQ, Question
    migrate.init_app(app, db)


    with app.app_context():
        from .views.quiz import quiz_bp
        app.register_blueprint(quiz_bp)

        from .views.auth import auth_bp
        app.register_blueprint(auth_bp)

        from .views.quiz import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')

        return app
