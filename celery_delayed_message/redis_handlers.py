from datetime import datetime

from celery._state import connect_on_app_finalize
from celery.utils.log import get_logger

from .consts import REDIS_CACHE_KEY, REQUEUE_RECENT, CACHE_MANAGER, CACHE_MANAGER_INTERVAL
from .helpers import loads, using_redis_transport
from .redis_clients import current_client, set_connection_url

logger = get_logger(__name__)


@connect_on_app_finalize
def add_redis_cache_manager_task(app):
    logger.info("add redis cache manager task")
    if using_redis_transport(app):
        set_connection_url(app.conf.broker_url)

    @app.task(name=CACHE_MANAGER, shared=False, lazy=False, bind=True)
    def cache_manager(self):
        set_connection_url(self.app.conf.broker_url)
        pop = current_client.register_script(
            """
            local stop = ARGV[1]
            local temp = redis.call("ZRANGEBYSCORE", KEYS[1], 0, stop)
            redis.call("ZREMRANGEBYSCORE", KEYS[1], 0, stop)
            return temp
            """
        )

        end_timestamp = int((self.app.now() + REQUEUE_RECENT).timestamp())
        cached_tasks = pop([REDIS_CACHE_KEY], args=[end_timestamp])
        logger.info("received: %s tasks", len(cached_tasks))
        for task_json in cached_tasks:
            task, param = loads(task_json)
            param.update(eta=datetime.fromisoformat(param["eta"]))
            task.apply_async(**param)

    @app.on_after_configure.connect
    def setup_cache_manager(sender, **_):
        sender.add_periodic_task(
            CACHE_MANAGER_INTERVAL,
            cache_manager.signature(),
        )

    return cache_manager
