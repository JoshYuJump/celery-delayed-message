from celery.app import task
from celery.utils.log import get_logger

from .tasks import DelayTask

__all__ = ["DelayTask", "monkey"]

logger = get_logger(__name__)


def patch_celery_task():

    task.Task = DelayTask
    logger.info('celery delayed message patched successfully.')


def patch(app):
    patch_celery_task()

    # Register `requeue_manager` task
    from .redis_handlers import faker as requeue_faker
    from .redis_handlers import manager as requeue_manager
    from .redis_handlers import get_requeue_task
    requeue_faker.app = app
    requeue_manager.app = app
    # app.tasks.register(requeue_faker)
    app.tasks.register(get_requeue_task(app))


monkey = type('Monkey', (object, ), dict(patch=patch))
