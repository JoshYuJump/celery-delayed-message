import json
from functools import partial

from kombu.utils.url import parse_url

from .consts import CONF_DELAY_TIME_AT_LEAST, DELAY_TIME_AT_LEAST


def parse_transport(app):
    return parse_url(app.conf.broker_url)["transport"]


def using_some_transport(transport, app):
    return parse_transport(app) == transport


using_redis_transport = partial(using_some_transport, "redis")
using_amqp_transport = partial(using_some_transport, "amqp")


def get_delay_conf(conf):
    default = {CONF_DELAY_TIME_AT_LEAST: DELAY_TIME_AT_LEAST}
    try:
        return {**default, **conf.DELAY}
    except AttributeError:
        return default


def dumps(task, param):
    return json.dumps({
        "task": task.name,
        "param": param,
    })


def loads(app, task_json):
    task_data = json.loads(task_json)
    return (
        app.tasks[task_data["task"]],
        task_data["param"],
    )
