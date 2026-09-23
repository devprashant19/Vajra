from abc import ABC, abstractmethod
from typing import Optional, Any
import json

class Cache(ABC):
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

class InMemoryCache(Cache):
    def __init__(self):
        self._store = {}

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        # For in-memory, we ignore TTL for this simplified mock
        self._store[key] = value

    def get(self, key: str) -> Optional[Any]:
        return self._store.get(key)

    def delete(self, key: str) -> None:
        if key in self._store:
            del self._store[key]

class RedisCache(Cache):
    def __init__(self, host: str, port: int, db: int = 0):
        import redis
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=True)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        val_str = json.dumps(value)
        self.client.set(key, val_str, ex=ttl)

    def get(self, key: str) -> Optional[Any]:
        val_str = self.client.get(key)
        if val_str:
            return json.loads(val_str)
        return None

    def delete(self, key: str) -> None:
        self.client.delete(key)
