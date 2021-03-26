import threading

from celery.local import Proxy
from redis.client import Redis

__all__ = ["set_connection_url", "current_client"]

_connection_url = None


class _RedisClients(threading.local):
    current_client = None


_redis_clients = _RedisClients()


def set_connection_url(connection_url: str) -> None:
    global _connection_url
    _connection_url = connection_url


def get_current_redis_client() -> Redis:
    client = _redis_clients.current_client

    if client is None:
        assert _connection_url is not None, "please set connection string first"
        client = Redis.from_url(_connection_url)
        _redis_clients.current_client = client

    return client


current_client = Proxy(get_current_redis_client)
