# django_celery/celery.py

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "olxscraper.settings")
app = Celery("olxscraper", broker="redis://127.0.0.1:6379")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
