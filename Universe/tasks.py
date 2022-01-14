from __future__ import absolute_import
from celery import current_task, Celery

app = Celery('Universe')
app.config_from_object('django.conf:settings')
@app.task(name = 'random_name')
def test():
    print('this is test')