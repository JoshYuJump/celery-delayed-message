from datetime import timedelta

AMQP_QUEUE_BASENAME = REDIS_CACHE_KEY = "celery_delayed_message.cache"
CACHE_MANAGER = REDIS_CACHE_KEY + "_manager"
CACHE_MANAGER_INTERVAL = timedelta(minutes=1)
DELAY_TIME_AT_LEAST = timedelta(minutes=2)
REQUEUE_RECENT = timedelta(hours=1.5)
CONF_DELAY_TIME_AT_LEAST = "delay_time_at_least"
