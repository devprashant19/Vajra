import os
from abc import ABC, abstractmethod
from typing import BinaryIO, Optional

class ObjectStore(ABC):
    @abstractmethod
    def put(self, key: str, data: bytes) -> None:
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[bytes]:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        pass

class LocalFSStore(ObjectStore):
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def _get_path(self, key: str) -> str:
        return os.path.join(self.base_dir, key)

    def put(self, key: str, data: bytes) -> None:
        path = self._get_path(key)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            f.write(data)

    def get(self, key: str) -> Optional[bytes]:
        path = self._get_path(key)
        if not os.path.exists(path):
            return None
        with open(path, 'rb') as f:
            return f.read()

    def delete(self, key: str) -> None:
        path = self._get_path(key)
        if os.path.exists(path):
            os.remove(path)

    def exists(self, key: str) -> bool:
        return os.path.exists(self._get_path(key))

class S3Store(ObjectStore):
    def __init__(self, endpoint_url: str, bucket: str, access_key: str, secret_key: str):
        self.bucket = bucket
        # Implementation would use boto3 or similar
        # Since this is a placeholder interface, we'll raise NotImplementedError
        # A real implementation would initialize the S3 client here
        
    def put(self, key: str, data: bytes) -> None:
        raise NotImplementedError()

    def get(self, key: str) -> Optional[bytes]:
        raise NotImplementedError()

    def delete(self, key: str) -> None:
        raise NotImplementedError()

    def exists(self, key: str) -> bool:
        raise NotImplementedError()
