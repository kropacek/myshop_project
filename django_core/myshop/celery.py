import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')

CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'

app = Celery('myshop', broker=CELERY_BROKER_URL)
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
