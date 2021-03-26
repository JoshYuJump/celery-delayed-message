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


def _get_current_redis_client() -> Redis:
    global _redis_clients
    client = _redis_clients.current_client

    if client is None:
        assert _connection_url is not None, "please set connection string first"
        client = _redis_clients.current_client = Redis.from_url(_connection_url)

    return client


current_client = Proxy(_get_current_redis_client)
