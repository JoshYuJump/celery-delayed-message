from datetime import timedelta

AMQP_QUEUE_BASENAME = REDIS_CACHE_KEY = "celery_delayed_message.cache"
CACHE_MANAGER = REDIS_CACHE_KEY + "_manager"
CONF_DELAY_TIME_AT_LEAST = "delay_time_at_least"

DELAY_TIME_AT_LEAST = timedelta(hours=2)
CACHE_MANAGER_INTERVAL = timedelta(hours=1)
REQUEUE_RECENT = CACHE_MANAGER_INTERVAL + timedelta(minutes=1)
