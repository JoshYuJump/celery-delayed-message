import json

from celery import shared_task, current_app

from .lua_scripts import ZSET_POP


@shared_task
def faker(*_1, **_2):
    pass


@shared_task
def manager():
    now, delay_conf = current_app.now(), current_app.conf.DELAY
    for parameters_json in ZSET_POP(
        [delay_conf["redis"]["cache_key"]],
        args=[int(now.timestamp()),
              int(now(now + delay_conf["requeue_recent"]).timestamp())],
    ):
        parameters = json.loads(parameters_json)
        faker.name = parameters.pop("original_task_name")
        faker.apply_async(**parameters)
