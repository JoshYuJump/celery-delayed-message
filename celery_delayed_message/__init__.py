from celery.app import task
from celery.utils.log import get_logger

from .redis_handlers import add_redis_cache_manager_task
from .tasks import DelayTask

__all__ = ["DelayTask", "monkey"]

logger = get_logger(__name__)


def patch_celery_task():

    task.Task = DelayTask
    logger.debug('celery delayed message patched successfully.')


monkey = type('Monkey', (object, ), dict(patch=patch_celery_task))
