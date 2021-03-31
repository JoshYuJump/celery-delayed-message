import os

from celery import Celery

from celery_delayed_message import patch_celery_task

# settings redis password in environment
auth = ""
print('Redis auth is', auth)
app = Celery('tasks', broker=f'redis://:{auth}@localhost')

patch_celery_task()


@app.task
def add(x, y):
    return x + y
