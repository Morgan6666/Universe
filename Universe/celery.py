import os
from celery import Celery


from Universe import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE','Universe.settings')

app = Celery('Universe')

app.config_from_object('django.conf:settings', namespace = 'CELERY')
app.autodiscover_tasks(lambda: settings.INSSTALLED_APPS)



@app.task
def add(x, y):
    return x/ y