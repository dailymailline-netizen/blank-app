"""
Storage abstraction layer supporting multiple backends (Local, AWS S3, etc.)
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, List, BinaryIO
import json
from datetime import datetime
import io


class StorageBackend(ABC):
    """Abstract base class for storage backends"""
    
    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file to storage backend"""
        pass
    
    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download file from storage backend"""
        pass
    
    @abstractmethod
    def delete_file(self, remote_path: str) -> bool:
        """Delete file from storage backend"""
        pass
    
    @abstractmethod
    def file_exists(self, remote_path: str) -> bool:
        """Check if file exists in storage"""
        pass
    
    @abstractmethod
    def list_files(self, prefix: str = "") -> List[str]:
        """List files in storage with optional prefix"""
        pass
    
    @abstractmethod
    def get_file_url(self, remote_path: str) -> str:
        """Get public URL for file (if supported)"""
        pass


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Copy file from local to local storage (essentially symlink/copy)"""
        try:
            src = Path(local_path)
            dst = self.base_path / remote_path
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            with open(src, 'rb') as src_file:
                with open(dst, 'wb') as dst_file:
                    dst_file.write(src_file.read())
            return True
        except Exception as e:
            print(f"Error uploading file to local storage: {e}")
            return False
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Copy file from local storage to local path"""
        try:
            src = self.base_path / remote_path
            dst = Path(local_path)
            dst.parent.mkdir(parents=True, exist_ok=True)
            
            with open(src, 'rb') as src_file:
                with open(dst, 'wb') as dst_file:
                    dst_file.write(src_file.read())
            return True
        except Exception as e:
            print(f"Error downloading file from local storage: {e}")
            return False
    
    def delete_file(self, remote_path: str) -> bool:
        """Delete file from local storage"""
        try:
            file_path = self.base_path / remote_path
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting file from local storage: {e}")
            return False
    
    def file_exists(self, remote_path: str) -> bool:
        """Check if file exists"""
        return (self.base_path / remote_path).exists()
    
    def list_files(self, prefix: str = "") -> List[str]:
        """List files with optional prefix filter"""
        try:
            search_path = self.base_path / prefix if prefix else self.base_path
            files = []
            if search_path.exists():
                for file in search_path.rglob('*'):
                    if file.is_file():
                        files.append(str(file.relative_to(self.base_path)))
            return files
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def get_file_url(self, remote_path: str) -> str:
        """Return local file path as URL"""
        return f"file://{self.base_path / remote_path}"


class S3StorageBackend(StorageBackend):
    """AWS S3 storage backend"""
    
    def __init__(self, bucket_name: str, region: str = "us-east-1", 
                 aws_access_key: Optional[str] = None, 
                 aws_secret_key: Optional[str] = None):
        try:
            import boto3
            self.boto3 = boto3
            self.s3_client = boto3.client(
                's3',
                region_name=region,
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key
            )
            self.bucket_name = bucket_name
            self.region = region
        except ImportError:
            raise ImportError("boto3 is required for S3 support. Install with: pip install boto3")
    
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload file to S3"""
        try:
            self.s3_client.upload_file(local_path, self.bucket_name, remote_path)
            print(f"Uploaded {local_path} to s3://{self.bucket_name}/{remote_path}")
            return True
        except Exception as e:
            print(f"Error uploading to S3: {e}")
            return False
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download file from S3"""
        try:
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            self.s3_client.download_file(self.bucket_name, remote_path, local_path)
            print(f"Downloaded s3://{self.bucket_name}/{remote_path} to {local_path}")
            return True
        except Exception as e:
            print(f"Error downloading from S3: {e}")
            return False
    
    def delete_file(self, remote_path: str) -> bool:
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=remote_path)
            return True
        except Exception as e:
            print(f"Error deleting from S3: {e}")
            return False
    
    def file_exists(self, remote_path: str) -> bool:
        """Check if file exists in S3"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=remote_path)
            return True
        except self.s3_client.exceptions.NoSuchKey:
            return False
        except Exception as e:
            print(f"Error checking S3 file: {e}")
            return False
    
    def list_files(self, prefix: str = "") -> List[str]:
        """List files in S3 bucket"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            files = []
            if 'Contents' in response:
                files = [obj['Key'] for obj in response['Contents'] if obj['Key'] != prefix]
            return files
        except Exception as e:
            print(f"Error listing S3 files: {e}")
            return []
    
    def get_file_url(self, remote_path: str) -> str:
        """Generate S3 file URL (public or pre-signed)"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': remote_path},
                ExpiresIn=3600  # URL expires in 1 hour
            )
            return url
        except Exception as e:
            print(f"Error generating S3 URL: {e}")
            return f"s3://{self.bucket_name}/{remote_path}"


class StorageFactory:
    """Factory for creating storage backend instances"""
    
    @staticmethod
    def create_backend(backend_type: str, **kwargs) -> StorageBackend:
        """Create storage backend based on type"""
        if backend_type.lower() == "local":
            return LocalStorageBackend(kwargs.get("base_path", "storage"))
        elif backend_type.lower() == "s3":
            return S3StorageBackend(
                bucket_name=kwargs.get("bucket_name"),
                region=kwargs.get("region", "us-east-1"),
                aws_access_key=kwargs.get("aws_access_key"),
                aws_secret_key=kwargs.get("aws_secret_key")
            )
        else:
            raise ValueError(f"Unknown storage backend: {backend_type}")
