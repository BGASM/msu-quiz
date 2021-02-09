import os


from msu_quiz import create_app, socketio

# Create an application instance that auxiliary processes such as Celery
# workers can use

application = app = create_app(os.environ.get('FLASK_ENV'))
socketio.run(app)