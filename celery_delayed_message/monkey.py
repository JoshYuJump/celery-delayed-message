from celery.app import task

from .tasks import DelayTask


def patch():
    task.Task = DelayTask
