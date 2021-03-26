from .redis_clients import current_client

ZSET_POP = current_client.register_script(
    """
    local start = ARGV[1]
    local stop = ARGV[2]
    local temp = redis.call("ZREVRANGEBYSCORE", KEYS[1], stop, start)
    redis.call("ZREMRANGEBYSCORE", KEYS[1], start, stop)
    return temp
    """
)
