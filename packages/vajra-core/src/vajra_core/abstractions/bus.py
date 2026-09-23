from abc import ABC, abstractmethod
from typing import Callable, Any, Dict, Optional, List
import json
import logging

logger = logging.getLogger(__name__)

class EventBus(ABC):
    @abstractmethod
    def publish(self, topic: str, payload: dict, partition_key: Optional[str] = None, idempotency_key: Optional[str] = None) -> None:
        pass

    @abstractmethod
    def subscribe(self, topic: str, group: str, handler: Callable[[dict], None]) -> None:
        pass

class InMemoryBus(EventBus):
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[dict], None]]] = {}
        self._processed_keys = set()
        self.dead_letters = []

    def publish(self, topic: str, payload: dict, partition_key: Optional[str] = None, idempotency_key: Optional[str] = None) -> None:
        if idempotency_key:
            if idempotency_key in self._processed_keys:
                return # duplicate
            self._processed_keys.add(idempotency_key)
            
        handlers = self._subscribers.get(topic, [])
        for handler in handlers:
            try:
                handler(payload)
            except Exception as e:
                logger.error(f"Error handling event: {e}")
                self.dead_letters.append({"topic": topic, "payload": payload, "error": str(e)})

    def subscribe(self, topic: str, group: str, handler: Callable[[dict], None]) -> None:
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

class RedisStreamBus(EventBus):
    def __init__(self, host: str, port: int):
        import redis
        self.client = redis.Redis(host=host, port=port, decode_responses=True)

    def publish(self, topic: str, payload: dict, partition_key: Optional[str] = None, idempotency_key: Optional[str] = None) -> None:
        if idempotency_key:
            # Check if idempotency key exists in a redis set (cache it with TTL)
            if self.client.setnx(f"idemp:{idempotency_key}", "1"):
                self.client.expire(f"idemp:{idempotency_key}", 86400) # 1 day TTL
            else:
                return # Duplicate
        
        # Redis streams payload must be dict of strings
        str_payload = {"data": json.dumps(payload)}
        self.client.xadd(topic, str_payload)

    def subscribe(self, topic: str, group: str, handler: Callable[[dict], None]) -> None:
        # A real implementation would create consumer group and loop `xreadgroup`
        # In this mock we raise NotImplementedError for brevity as it's complex to simulate async loops here
        raise NotImplementedError("RedisStreamBus loop not fully implemented in skeleton")

class KafkaBus(EventBus):
    def __init__(self, bootstrap_servers: str):
        from confluent_kafka import Producer, Consumer
        self.bootstrap_servers = bootstrap_servers
        self.producer = Producer({'bootstrap.servers': bootstrap_servers})

    def publish(self, topic: str, payload: dict, partition_key: Optional[str] = None, idempotency_key: Optional[str] = None) -> None:
        # Kafka handles idempotency natively if enabled, but we can also use headers
        headers = []
        if idempotency_key:
            headers.append(('idempotency_key', idempotency_key.encode('utf-8')))
            
        key_bytes = partition_key.encode('utf-8') if partition_key else None
        
        def delivery_report(err, msg):
            if err is not None:
                logger.error(f'Message delivery failed: {err}')
                
        self.producer.produce(
            topic, 
            key=key_bytes, 
            value=json.dumps(payload).encode('utf-8'),
            headers=headers,
            callback=delivery_report
        )
        self.producer.poll(0)

    def subscribe(self, topic: str, group: str, handler: Callable[[dict], None]) -> None:
        # A real implementation would spin up a background thread with consumer loop
        raise NotImplementedError("KafkaBus loop not fully implemented in skeleton")
