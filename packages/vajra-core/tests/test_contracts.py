import pytest
from vajra_core.abstractions.bus import InMemoryBus
from vajra_core.abstractions.cache import InMemoryCache
from vajra_core.abstractions.store import LocalFSStore
import os

def test_inmemory_bus():
    bus = InMemoryBus()
    received = []
    
    def handler(payload):
        received.append(payload)
        
    bus.subscribe("test.topic", "group1", handler)
    bus.publish("test.topic", {"msg": "hello"})
    
    assert len(received) == 1
    assert received[0]["msg"] == "hello"

def test_inmemory_bus_idempotency():
    bus = InMemoryBus()
    received = []
    
    def handler(payload):
        received.append(payload)
        
    bus.subscribe("test.topic", "group1", handler)
    
    # Publish same idempotency key twice
    bus.publish("test.topic", {"msg": "hello"}, idempotency_key="key1")
    bus.publish("test.topic", {"msg": "hello"}, idempotency_key="key1")
    
    assert len(received) == 1

def test_inmemory_cache():
    cache = InMemoryCache()
    cache.set("key1", "val1")
    assert cache.get("key1") == "val1"
    cache.delete("key1")
    assert cache.get("key1") is None

def test_localfs_store(tmp_path):
    store = LocalFSStore(str(tmp_path))
    store.put("folder/file.txt", b"hello world")
    
    assert store.exists("folder/file.txt")
    assert store.get("folder/file.txt") == b"hello world"
    
    store.delete("folder/file.txt")
    assert not store.exists("folder/file.txt")
