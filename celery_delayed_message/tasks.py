import json
from datetime import timedelta, datetime
from typing import Union, Tuple

from celery.app.task import Task
from celery.result import AsyncResult
from celery.utils.time import maybe_make_aware
from kombu.utils.objects import cached_property
from kombu.utils.url import parse_url
from kombu.utils.uuid import uuid

from .consts import REDIS_CACHE_KEY, AMQP_QUEUE_BASENAME
from .redis_clients import current_client, set_connection_url


class DelayTask(Task):
    abstract = True

    @property
    def app(self):
        return self._get_app()

    @property
    def broker_url(self):
        return self.app.conf.broker_url

    @property
    def broker_transport(self) -> str:
        return parse_url(self.broker_url)["transport"]

    @property
    def is_redis_broker(self):
        is_redis = self.broker_transport == "redis"
        if is_redis:
            set_connection_url(self.broker_url)
        return is_redis

    @property
    def is_amqp_broker(self):
        return self.broker_transport == "amqp"

    @cached_property
    def delay_conf(self):
        """
        {
            "minimum": timedelta(hours=1),
            "requeue_recent": timedelta(hours=1),
        }
        """
        return self.app.conf.DELAY

    def get_countdown_and_eta(self, options) -> Tuple[Union[int, float], datetime]:
        now = self.app.now()
        countdown, eta = options.get("countdown"), options.get("eta")
        if countdown:
            return countdown, now + timedelta(seconds=countdown)
        elif eta:
            aware_eta = maybe_make_aware(eta, self.app.timezone)
            return (aware_eta - now).total_seconds(), aware_eta
        else:
            return 0, now

    def apply_async(
        self,
        args=None,
        kwargs=None,
        task_id=None,
        producer=None,
        link=None,
        link_error=None,
        shadow=None,
        **options
    ):
        task_id = task_id or uuid()
        parameters = locals()
        del parameters["self"]
        _options = parameters.pop("options")
        parameters.update(_options)

        countdown, eta = self.get_countdown_and_eta(options)
        if countdown >= self.delay_conf["minimum"].total_seconds():
            if self.is_amqp_broker:
                queue_name = AMQP_QUEUE_BASENAME + ":" + task_id
                self.app.amqp.queues.add(
                    queue_name,
                    routing_key=options["routing_key"],
                    queue_arguments={
                        "x-message-ttl": countdown * 1000,
                        "x-dead-letter-exchange": options["queue"],
                        "x-expires": (countdown + 1) * 1000,
                    },
                )
                options.update({"queue": queue_name})
            elif self.is_redis_broker:
                parameters.update(original_task_name=self.name)
                current_client.zadd(
                    REDIS_CACHE_KEY,
                    {json.dumps(parameters): int(eta.timestamp())},
                )
                return AsyncResult(task_id, task_name=self.name, app=self.app)
            else:
                pass

        return super(DelayTask, self).apply_async(
            args, kwargs, task_id, producer, link, link_error, shadow, **options
        )
