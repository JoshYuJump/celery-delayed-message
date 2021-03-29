import os

from celery import Celery

from celery_delayed_message import monkey

# settings redis password in environment
auth = os.getenv('REDIS_AUTH')
print('Redis auth is', auth)
app = Celery('tasks', broker=f'redis://:{auth}@localhost')

monkey.patch(app)


@app.task
def add(x, y):
    return x + y
