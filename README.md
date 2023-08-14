# Slim API - Rinha de Backend 2023

To run:
```bash
python -m venv venv
source venv/bin/activate
(venv) pip install -r requirements.txt
(venv) gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```
