import base64
import pickle
import json
from functools import partial

from celery.schedules import crontab
from kombu.utils.url import parse_url

from .consts import CONF_DELAY_TIME_AT_LEAST, CACHE_MANAGER_INTERVAL, CACHE_MANAGER, DELAY_TIME_AT_LEAST


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


def install_default_entries(self, data):
    entries = {}
    if self.app.conf.result_expires and \
            not self.app.backend.supports_autoexpire:
        if 'celery.backend_cleanup' not in data:
            entries['celery.backend_cleanup'] = {
                'task': 'celery.backend_cleanup',
                'schedule': crontab('0', '4', '*'),
                'options': {
                    'expires': 12 * 3600
                }
            }

    if CACHE_MANAGER not in data:
        entries[CACHE_MANAGER] = {
            'task': CACHE_MANAGER,
            'schedule': CACHE_MANAGER_INTERVAL,
        }

    self.update_from_dict(entries)
