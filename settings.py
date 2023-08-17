import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/postgres')
DATABASE_MAX_CONNECTIONS = int(os.getenv('DATABASE_MAX_CONNECTIONS', 10))

GUNICORN_BIND = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
GUNICORN_WORKERS = int(os.getenv('GUNICORN_EXTRA_WORKERS', 5))
GUNICORN_KEEPALIVE = int(os.getenv('GUNICORN_KEEPALIVE', 5))
GUNICORN_FORWARDED_ALLOW_IPS = os.getenv('GUNICORN_FORWARDED_ALLOW_IPS', '*')