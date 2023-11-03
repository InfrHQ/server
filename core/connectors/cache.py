from core.configurations import Redis
from core.utils.general import colored_print
from cachetools import TTLCache
import redis


class Cache:
    def __init__(self):
        if Redis.uri:
            self._cache_backend = "redis"
            self._redis_client = redis.Redis().from_url(Redis.uri)
        else:
            self._cache_backend = "in_memory"
            self._ttl_cache = TTLCache(maxsize=1000, ttl=3600)

        self._warn_about_configuration()

    def _warn_about_configuration(self):
        if self._cache_backend == "in_memory":
            colored_print("Warning: Redis is not configured. Cache will be stored in memory.", "yellow")
        elif self._cache_backend == "redis":
            colored_print("Redis is configured. Cache client will use Redis.", "green")

    def set_item(self, key: str, value: str, expiry: int = 3600):
        """
        :dev This function stores an item in the cache.
        :param key (str): Key.
        :param value (str): Value.
        :param expiry (int): Expiry in seconds.
        """
        if self._cache_backend == "redis":
            self._redis_client.set(key, value, ex=expiry)
        elif self._cache_backend == "in_memory":
            self._ttl_cache[key] = value

    def get_item(self, key: str):
        """
        :dev This function gets an item from the cache.
        :param key (str): Key.
        """
        if self._cache_backend == "redis":
            return self._redis_client.get(key)
        elif self._cache_backend == "in_memory":
            return self._ttl_cache.get(key, default=None)
        return None


# Usage
cache_client = Cache()
