from os import environ
# global Celery options that apply to all configurations
broker_url = environ.get('RABBIT_MQ_URL', 'redis://'),
broker_pool_limit = 10
result_backend = environ.get('REDIS_URL', 'redis://')
redis_max_connections = 10
