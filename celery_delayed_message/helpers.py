import base64
import pickle
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
        "task": base64.b64encode(pickle.dumps(task)).decode(),
        "param": param,
    })


def loads(content):
    data = json.loads(content)
    return (
        pickle.loads(base64.b64decode(data["task"].encode())),
        data["param"],
    )
