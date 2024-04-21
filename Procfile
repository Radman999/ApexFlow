release: python manage.py migrate
web: gunicorn config.asgi:application -k uvicorn.workers.UvicornWorker
#worker: celery -A config.celery_app worker --loglevel=info
#beat: celery -A config.celery_app beat --loglevel=info
