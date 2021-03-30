from datetime import timedelta

from celery.app.task import Task
from celery.result import AsyncResult
from celery.utils import gen_unique_id
from celery.utils.time import maybe_make_aware
from kombu.utils.objects import cached_property

from .consts import REDIS_CACHE_KEY, AMQP_QUEUE_BASENAME, CONF_DELAY_TIME_AT_LEAST
from .redis_clients import current_client
from .helpers import using_redis_transport, using_amqp_transport, get_delay_conf, dumps


class DelayTask(Task):
    abstract = True

    @cached_property
    def app(self):
        return self._get_app()

    @cached_property
    def delay_conf(self):
        return get_delay_conf(self.app.conf)

    def get_countdown_and_eta(self, options):
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
        task_id = task_id or gen_unique_id()
        param = {k: v for k, v in locals().items() if not k.startswith("__")}
        del param["self"]
        _options = param.pop("options")
        param.update(_options)

        countdown, eta = self.get_countdown_and_eta(options)
        if countdown >= self.delay_conf[CONF_DELAY_TIME_AT_LEAST].total_seconds():
            if using_amqp_transport(self.app):
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
            elif using_redis_transport(self.app):
                param.update(eta=eta.isoformat())
                param.pop("countdown", None)
                current_client.zadd(REDIS_CACHE_KEY, {dumps(self, param): int(eta.timestamp())})
                return AsyncResult(task_id, task_name=self.name, app=self.app)
            else:
                pass

        return super(DelayTask, self).apply_async(
            args, kwargs, task_id, producer, link, link_error, shadow, **options
        )
