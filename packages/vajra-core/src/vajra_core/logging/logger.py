import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, str | None] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id
            
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

class VajraError(Exception):
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        super().__init__(message)
        self.code = code

class DataValidationError(VajraError):
    def __init__(self, message: str):
        super().__init__(message, "DATA_VALIDATION_ERROR")

class UpstreamTimeoutError(VajraError):
    def __init__(self, message: str):
        super().__init__(message, "UPSTREAM_TIMEOUT_ERROR")

class StorageError(VajraError):
    def __init__(self, message: str):
        super().__init__(message, "STORAGE_ERROR")

def setup_logging(level=logging.INFO):
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)
        
    root_logger.addHandler(handler)
