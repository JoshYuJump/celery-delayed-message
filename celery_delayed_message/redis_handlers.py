import time
import json

from celery import shared_task, current_app
from celery.utils.log import get_logger

from .consts import REDIS_CACHE_KEY

logger = get_logger(__name__)


@shared_task
def faker(*_1, **_2):
    pass


def get_faker(app):
    def faker(self, *_1, **_2):
        print('faker executed...')
    return app.task(bind=True)(faker)


@current_app.task(bind=True)
def manager(self):
    from .lua_scripts import ZSET_POP

    requeue_times = 30  # Each execution requeue times
    executed = 0
    while executed < requeue_times:
        current_timestamp = current_app.now().timestamp()
        for serialized_task in ZSET_POP([REDIS_CACHE_KEY], args=[0, current_timestamp]):
            parameters = json.loads(serialized_task)
            faker.name = parameters.pop("original_task_name")
            faker.apply_async(**parameters)
        executed += 1
        time.sleep(1)

    logger.debug('Celery delayed message requeue successfully')
    self.delay()


def get_requeue_task(app):
    def requeue(self):
        from .lua_scripts import ZSET_POP
        print('requeue', requeue)
        print('ZSET_POP', ZSET_POP)
        requeue_times = 30  # Each execution requeue times
        executed = 0
        while executed < requeue_times:
            current_timestamp = current_app.now().timestamp()
            print('current_timestamp %s' % current_timestamp)
            serialized_tasks = ZSET_POP([REDIS_CACHE_KEY], args=[0, current_timestamp])
            print('serialized_tasks' % serialized_tasks)
            for serialized_task in serialized_tasks:
                print('serialized_task' % serialized_task)
                parameters = json.loads(serialized_task)

                faker = get_faker(app)
                faker.name = parameters.pop("original_task_name")
                faker.apply_async(**parameters)

            executed += 1
            time.sleep(1)

        logger.debug('Celery delayed message requeue successfully')
        self.delay()
    return app.task(bind=True)(requeue)
