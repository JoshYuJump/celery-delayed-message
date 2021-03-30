from celery.app import task

from .redis_handlers import add_redis_cache_manager_task
from .tasks import DelayTask

__all__ = ["DelayTask", "patch_celery_task"]


def patch_celery_task():
    task.Task = DelayTask
