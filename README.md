# Slim API - Rinha de Backend 2023

- Using Gunicorn over Uvicorn since we are not using async code on our application.

To run:
```bash
python -m venv venv
source venv/bin/activate
(venv) pip install -r requirements.txt
(venv) gunicorn main:app
```
