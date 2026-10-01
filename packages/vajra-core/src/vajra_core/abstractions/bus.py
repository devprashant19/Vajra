from abc import ABC, abstractmethod
from typing import Callable, Any, Dict, Optional, List
import json
import logging

logger = logging.getLogger(__name__)

class EventBus(ABC):
    @abstractmethod
    def publish(self, topic: str, payload: Dict[str, Any], partition_key: Optional[str] = None, idempotency_key: Optional[str] = None) -> None:
        pass

    @abstractmethod
    def subscribe(self, topic: str, group: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        pass

class InMemoryBus(EventBus):
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}
        self._processed_keys = set()
        self.dead_letters = []

    def publish(self, topic: str, payload: Dict[str, Any], partition_key: Optional[str] = None, idempotency_key: Optional[str] = None) -> None:
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

    def subscribe(self, topic: str, group: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

class RedisStreamBus(EventBus):
    def __init__(self, host: str, port: int, max_retries: int = 3):
        import redis
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        self.max_retries = max_retries

    def publish(self, topic: str, payload: Dict[str, Any], partition_key: Optional[str] = None, idempotency_key: Optional[str] = None) -> None:
        if idempotency_key:
            if self.client.setnx(f"idemp:{idempotency_key}", "1"):
                self.client.expire(f"idemp:{idempotency_key}", 86400)
            else:
                return # Duplicate
        
        str_payload = {"data": json.dumps(payload)}
        self.client.xadd(topic, str_payload)

    def subscribe(self, topic: str, group: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        import time
        from redis.exceptions import ResponseError
        
        consumer_name = "consumer_1"
        try:
            self.client.xgroup_create(topic, group, id='0', mkstream=True)
        except ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise
                
        def consume_loop():
            while True:
                # Reclaim pending entries older than 60s
                try:
                    pending = self.client.xpending_range(topic, group, "-", "+", 10)
                    for p in pending:
                        msg_id, consumer, idle, delivered = p['message_id'], p['consumer'], p['time_since_delivered'], p['deliveries']
                        if idle > 60000:
                            if delivered > self.max_retries:
                                # dead letter
                                msgs = self.client.xrange(topic, min=msg_id, max=msg_id)
                                if msgs:
                                    self.client.xadd("dead_letters", {"topic": topic, "group": group, "data": msgs[0][1].get("data")})
                                self.client.xack(topic, group, msg_id)
                            else:
                                self.client.xclaim(topic, group, consumer_name, 60000, [msg_id])
                except Exception as e:
                    logger.error(f"Error reclaiming: {e}")
                    
                # Read new or claimed messages
                try:
                    messages = self.client.xreadgroup(group, consumer_name, {topic: '>'}, count=10, block=1000)
                    for stream, msg_list in messages:
                        for msg_id, msg_data in msg_list:
                            try:
                                payload = json.loads(msg_data["data"])
                                handler(payload)
                                self.client.xack(topic, group, msg_id)
                            except Exception as e:
                                logger.error(f"Error handling message {msg_id}: {e}")
                except Exception as e:
                    logger.error(f"Error reading group: {e}")
                    time.sleep(1)

        import threading
        t = threading.Thread(target=consume_loop, daemon=True)
        t.start()

class KafkaBus(EventBus):
    def __init__(self, bootstrap_servers: str, max_retries: int = 3):
        from confluent_kafka import Producer
        self.bootstrap_servers = bootstrap_servers
        self.producer = Producer({'bootstrap.servers': bootstrap_servers})
        self.max_retries = max_retries

    def publish(self, topic: str, payload: Dict[str, Any], partition_key: Optional[str] = None, idempotency_key: Optional[str] = None) -> None:
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

    def subscribe(self, topic: str, group: str, handler: Callable[[Dict[str, Any]], None]) -> None:
        def consume_loop():
            from confluent_kafka import Consumer, KafkaError
            import time
            consumer = Consumer({
                'bootstrap.servers': self.bootstrap_servers,
                'group.id': group,
                'auto.offset.reset': 'earliest',
                'enable.auto.commit': False
            })
            consumer.subscribe([topic])
            
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                        time.sleep(1)
                        continue
                
                try:
                    headers_dict = dict(msg.headers() or [])
                    idemp_key = headers_dict.get('idempotency_key')
                    if idemp_key:
                        idemp_key_str = idemp_key.decode('utf-8')
                        if hasattr(self, '_processed_keys') and idemp_key_str in self._processed_keys:
                            consumer.commit(asynchronous=False)
                            continue
                        if not hasattr(self, '_processed_keys'):
                            self._processed_keys = set()
                        self._processed_keys.add(idemp_key_str)
                    
                    payload = json.loads(msg.value().decode('utf-8'))
                    handler(payload)
                    consumer.commit(asynchronous=False)
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    # Dead letter logic would go here in a real implementation
                    # (e.g. tracking retries in headers, publishing to dead_letters topic)
                    # For now we'll just log and commit to avoid poison pill blocking
                    consumer.commit(asynchronous=False)

        import threading
        t = threading.Thread(target=consume_loop, daemon=True)
        t.start()
