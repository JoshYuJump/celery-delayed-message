from celery.app import task

from .tasks import DelayTask


def monkey_patch():
    task.Task = DelayTask
