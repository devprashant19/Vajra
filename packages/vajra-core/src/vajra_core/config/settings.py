from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

class VajraSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="VAJRA_")
    
    profile: Literal["lite", "full", "national"] = "lite"
    
    # Store settings
    store_type: Literal["local", "s3"] = "local"
    s3_endpoint: str = "http://localhost:9000"
    s3_bucket: str = "vajra-data"
    
    # Bus settings
    bus_type: Literal["inmemory", "redis", "kafka"] = "inmemory"
    kafka_brokers: str = "localhost:9092"
    
    # Cache settings
    cache_type: Literal["inmemory", "redis"] = "inmemory"
    redis_url: str = "redis://localhost:6379/0"
    
    # DB settings
    database_url: str = "postgresql://vajra:vajra@localhost:5432/vajra"

settings = VajraSettings()
