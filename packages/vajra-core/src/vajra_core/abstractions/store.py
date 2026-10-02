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

    @abstractmethod
    def get_range(self, key: str, offset: int, length: int) -> Optional[bytes]:
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

    def get_range(self, key: str, offset: int, length: int) -> Optional[bytes]:
        path = self._get_path(key)
        if not os.path.exists(path):
            return None
        with open(path, 'rb') as f:
            f.seek(offset)
            return f.read(length)

    def delete(self, key: str) -> None:
        path = self._get_path(key)
        if os.path.exists(path):
            os.remove(path)

    def exists(self, key: str) -> bool:
        return os.path.exists(self._get_path(key))

    def list(self, prefix: str = "") -> list[str]:
        result = []
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, self.base_dir)
                if os.name == 'nt':
                    rel_path = rel_path.replace('\\', '/')
                if rel_path.startswith(prefix):
                    result.append(rel_path)
        return result

class S3Store(ObjectStore):
    def __init__(self, endpoint_url: str, bucket: str, access_key: str, secret_key: str):
        from minio import Minio
        from urllib.parse import urlparse
        import io
        
        self.bucket = bucket
        parsed_url = urlparse(endpoint_url)
        # minio client expects endpoint without scheme
        endpoint = parsed_url.netloc if parsed_url.netloc else parsed_url.path
        
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=(parsed_url.scheme == "https")
        )
        
        # Ensure bucket exists
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def put(self, key: str, data: bytes) -> None:
        import io
        data_stream = io.BytesIO(data)
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=key,
            data=data_stream,
            length=len(data)
        )

    def get(self, key: str) -> Optional[bytes]:
        from minio.error import S3Error
        try:
            response = self.client.get_object(self.bucket, key)
            return response.read()
        except S3Error as e:
            if e.code == "NoSuchKey":
                return None
            raise
        finally:
            if 'response' in locals():
                response.close()
                response.release_conn()

    def delete(self, key: str) -> None:
        self.client.remove_object(self.bucket, key)

    def exists(self, key: str) -> bool:
        from minio.error import S3Error
        try:
            self.client.stat_object(self.bucket, key)
            return True
        except S3Error as e:
            if e.code == "NoSuchKey" or e.code == "NotFound":
                return False
            raise
            
    def list(self, prefix: str = "") -> list[str]:
        # Helper for testing
        objects = self.client.list_objects(self.bucket, prefix=prefix, recursive=True)
        return [obj.object_name for obj in objects]

    def get_range(self, key: str, offset: int, length: int) -> Optional[bytes]:
        from minio.error import S3Error
        try:
            # S3 Range header is inclusive e.g., bytes=0-499
            response = self.client.get_object(
                self.bucket, 
                key, 
                offset=offset,
                length=length
            )
            return response.read()
        except S3Error as e:
            if e.code == "NoSuchKey":
                return None
            raise
        finally:
            if 'response' in locals():
                response.close()
                response.release_conn()
