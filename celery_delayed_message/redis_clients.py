import threading

from celery import current_app
from celery.local import Proxy
from redis.client import Redis
from .utils import get_broker_transport

__all__ = ["set_connection_url", "current_client"]

_connection_url = None


def set_connection_url(connection_url: str) -> None:
    global _connection_url
    _connection_url = connection_url


# connect to redis broker
if get_broker_transport(current_app) == "redis":
    set_connection_url(current_app.conf.broker_url)


class _RedisClients(threading.local):
    current_client = None


_redis_clients = _RedisClients()


def _get_current_redis_client() -> Redis:
    global _redis_clients
    client = _redis_clients.current_client

    # re-connect to redis is client is None
    if client is None:
        # connect to redis broker
        if get_broker_transport(current_app) == "redis":
            set_connection_url(current_app.conf.broker_url)

        assert _connection_url is not None, "please set connection string first"
        client = _redis_clients.current_client = Redis.from_url(_connection_url)

    return client


current_client = Proxy(_get_current_redis_client)
