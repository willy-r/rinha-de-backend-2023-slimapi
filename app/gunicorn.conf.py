import settings

bind = settings.GUNICORN_BIND
workers = settings.GUNICORN_WORKERS
worker_class = 'uvicorn.workers.UvicornWorker'
keepalive = settings.GUNICORN_KEEPALIVE
forwarded_allow_ips = settings.GUNICORN_FORWARDED_ALLOW_IPS
