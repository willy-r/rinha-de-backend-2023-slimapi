import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/postgres')
DATABASE_MAX_CONNECTIONS = int(os.getenv('DATABASE_MAX_CONNECTIONS', 10))

CACHE_HOST = os.getenv('CACHE_HOST', 'localhost')
CACHE_PORT = int(os.getenv('CACHE_PORT', 6379))

GUNICORN_BIND = os.getenv('GUNICORN_BIND', 'localhost:8000')
GUNICORN_WORKERS = int(os.getenv('GUNICORN_WORKERS', 1))
GUNICORN_KEEPALIVE = int(os.getenv('GUNICORN_KEEPALIVE', 2))
GUNICORN_FORWARDED_ALLOW_IPS = os.getenv('GUNICORN_FORWARDED_ALLOW_IPS', '*')
