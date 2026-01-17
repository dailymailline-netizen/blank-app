"""
Live Stream Image Management with Private/Public Access and Caching
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
import uuid
from enum import Enum
import hashlib
from PIL import Image
import io


class ImageVisibility(Enum):
    """Image visibility levels"""
    PRIVATE = "private"      # Only stream owner
    PUBLIC = "public"        # All viewers
    SUBSCRIBERS = "subscribers"  # Paying members


class StreamImage:
    """Individual stream image metadata"""
    
    def __init__(self, image_id: str, stream_id: str, filename: str, 
                 file_path: str, visibility: ImageVisibility = ImageVisibility.PUBLIC,
                 title: str = "", description: str = ""):
        self.image_id = image_id
        self.stream_id = stream_id
        self.filename = filename
        self.file_path = file_path
        self.visibility = visibility
        self.title = title
        self.description = description
        self.created_at = datetime.now().isoformat()
        self.size_bytes = 0
        self.dimensions = None  # (width, height)
        self.thumbnail_path = None
        self.view_count = 0
        self.last_accessed = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON storage"""
        return {
            "image_id": self.image_id,
            "stream_id": self.stream_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "visibility": self.visibility.value,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at,
            "size_bytes": self.size_bytes,
            "dimensions": self.dimensions,
            "thumbnail_path": self.thumbnail_path,
            "view_count": self.view_count,
            "last_accessed": self.last_accessed
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "StreamImage":
        """Create from dictionary"""
        img = StreamImage(
            data["image_id"],
            data["stream_id"],
            data["filename"],
            data["file_path"],
            ImageVisibility(data.get("visibility", "public")),
            data.get("title", ""),
            data.get("description", "")
        )
        img.size_bytes = data.get("size_bytes", 0)
        img.dimensions = data.get("dimensions")
        img.thumbnail_path = data.get("thumbnail_path")
        img.view_count = data.get("view_count", 0)
        img.last_accessed = data.get("last_accessed")
        img.created_at = data.get("created_at", datetime.now().isoformat())
        return img


class StreamImageCache:
    """Memory and disk cache for stream images"""
    
    def __init__(self, cache_dir: Path, max_memory_mb: int = 500, ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.ttl = timedelta(hours=ttl_hours)
        
        # In-memory cache
        self.memory_cache: Dict[str, Tuple[bytes, datetime]] = {}
        self.memory_used = 0
        
        # Cache metadata
        self.metadata_file = cache_dir / "cache_metadata.json"
        self._load_metadata()
    
    def cache_image(self, image_id: str, image_data: bytes, 
                   page: str = "default") -> bool:
        """
        Cache image in memory with page organization
        
        Args:
            image_id: Unique image identifier
            image_data: Image binary data
            page: Page/section identifier for organization
        
        Returns:
            Success status
        """
        image_size = len(image_data)
        
        # Check if adding this would exceed memory limit
        if self.memory_used + image_size > self.max_memory_bytes:
            self._evict_old_entries()
        
        # Add to memory cache
        cache_key = f"{page}:{image_id}"
        self.memory_cache[cache_key] = (image_data, datetime.now())
        self.memory_used += image_size
        
        # Save to disk as backup
        self._save_to_disk(cache_key, image_data, page)
        
        return True
    
    def get_image(self, image_id: str, page: str = "default") -> Optional[bytes]:
        """Retrieve cached image"""
        cache_key = f"{page}:{image_id}"
        
        # Check memory cache first
        if cache_key in self.memory_cache:
            data, timestamp = self.memory_cache[cache_key]
            # Check if expired
            if datetime.now() - timestamp < self.ttl:
                return data
            else:
                del self.memory_cache[cache_key]
        
        # Try disk cache
        disk_path = self._get_disk_path(cache_key, page)
        if disk_path.exists():
            try:
                with open(disk_path, 'rb') as f:
                    data = f.read()
                # Restore to memory
                self.memory_cache[cache_key] = (data, datetime.now())
                self.memory_used += len(data)
                return data
            except Exception as e:
                print(f"Error reading disk cache: {e}")
        
        return None
    
    def clear_page_cache(self, page: str) -> int:
        """Clear all cached images for a page"""
        prefix = f"{page}:"
        removed_count = 0
        removed_size = 0
        
        # Remove from memory
        keys_to_remove = [k for k in self.memory_cache.keys() if k.startswith(prefix)]
        for key in keys_to_remove:
            _, timestamp = self.memory_cache[key]
            removed_size += len(self.memory_cache[key][0])
            del self.memory_cache[key]
            removed_count += 1
        
        self.memory_used -= removed_size
        
        # Remove from disk
        for file in self.cache_dir.glob(f"{page}_*.img"):
            file.unlink()
        
        return removed_count
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total_items = len(self.memory_cache)
        return {
            "memory_used_mb": round(self.memory_used / (1024 * 1024), 2),
            "memory_max_mb": self.max_memory_bytes / (1024 * 1024),
            "cached_items": total_items,
            "cache_dir": str(self.cache_dir),
            "ttl_hours": self.ttl.total_seconds() / 3600
        }
    
    def _evict_old_entries(self):
        """LRU eviction: remove oldest entries"""
        if not self.memory_cache:
            return
        
        # Sort by timestamp
        sorted_items = sorted(
            self.memory_cache.items(),
            key=lambda x: x[1][1]
        )
        
        # Remove oldest 20% of entries
        remove_count = max(1, len(sorted_items) // 5)
        removed_size = 0
        
        for key, (data, _) in sorted_items[:remove_count]:
            removed_size += len(data)
            del self.memory_cache[key]
        
        self.memory_used -= removed_size
    
    def _save_to_disk(self, cache_key: str, data: bytes, page: str):
        """Save image to disk cache"""
        try:
            path = self._get_disk_path(cache_key, page)
            with open(path, 'wb') as f:
                f.write(data)
        except Exception as e:
            print(f"Error saving to disk cache: {e}")
    
    def _get_disk_path(self, cache_key: str, page: str) -> Path:
        """Get disk cache file path"""
        filename = f"{page}_{cache_key.replace(':', '_')}.img"
        return self.cache_dir / filename
    
    def _load_metadata(self):
        """Load cache metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
            except:
                self.metadata = {}
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """Save cache metadata"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f)
        except Exception as e:
            print(f"Error saving cache metadata: {e}")


class StreamImageManager:
    """Manage stream images with access control and caching"""
    
    def __init__(self, images_dir: Path, cache_dir: Path):
        self.images_dir = images_dir
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.cache = StreamImageCache(cache_dir)
        
        # Stream images index
        self.stream_images: Dict[str, List[StreamImage]] = {}
        self._load_images()
    
    def upload_stream_image(self, stream_id: str, image_data: bytes, 
                           filename: str, visibility: ImageVisibility,
                           title: str = "", description: str = "",
                           page: str = "default") -> Optional[str]:
        """
        Upload image for stream
        
        Args:
            stream_id: Stream ID
            image_data: Image binary data
            filename: Original filename
            visibility: Public/Private/Subscribers
            title: Image title
            description: Image description
            page: Page section (for cache organization)
        
        Returns:
            Image ID or None if failed
        """
        try:
            image_id = str(uuid.uuid4())
            
            # Create stream images dir if not exists
            stream_dir = self.images_dir / stream_id
            stream_dir.mkdir(exist_ok=True)
            
            # Save image
            file_path = stream_dir / f"{image_id}_{filename}"
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            # Create metadata
            img_obj = StreamImage(
                image_id, stream_id, filename,
                str(file_path), visibility, title, description
            )
            img_obj.size_bytes = len(image_data)
            
            # Extract dimensions
            try:
                pil_img = Image.open(io.BytesIO(image_data))
                img_obj.dimensions = pil_img.size
                
                # Generate thumbnail
                pil_img.thumbnail((200, 200))
                thumb_path = stream_dir / f"{image_id}_thumb.jpg"
                pil_img.save(thumb_path, quality=85)
                img_obj.thumbnail_path = str(thumb_path)
            except Exception as e:
                print(f"Error processing image: {e}")
            
            # Cache the image
            self.cache.cache_image(image_id, image_data, page)
            
            # Store metadata
            if stream_id not in self.stream_images:
                self.stream_images[stream_id] = []
            self.stream_images[stream_id].append(img_obj)
            
            # Persist
            self._save_images()
            
            return image_id
        
        except Exception as e:
            print(f"Error uploading stream image: {e}")
            return None
    
    def get_stream_images(self, stream_id: str, user_id: Optional[str] = None,
                         is_owner: bool = False, page: str = "default") -> List[StreamImage]:
        """
        Get visible images for stream with access control
        
        Args:
            stream_id: Stream ID
            user_id: Requesting user ID
            is_owner: Whether user is stream owner
            page: Page filter
        
        Returns:
            List of visible images
        """
        if stream_id not in self.stream_images:
            return []
        
        visible_images = []
        
        for img in self.stream_images[stream_id]:
            # Owner can see all
            if is_owner:
                visible_images.append(img)
            # Others see public
            elif img.visibility == ImageVisibility.PUBLIC:
                visible_images.append(img)
            # Future: subscriber check
            # elif img.visibility == ImageVisibility.SUBSCRIBERS and user_subscribed:
            #     visible_images.append(img)
        
        # Record view
        for img in visible_images:
            img.view_count += 1
            img.last_accessed = datetime.now().isoformat()
        
        self._save_images()
        
        return visible_images
    
    def delete_stream_image(self, stream_id: str, image_id: str) -> bool:
        """Delete stream image"""
        try:
            if stream_id not in self.stream_images:
                return False
            
            # Find and remove image
            self.stream_images[stream_id] = [
                img for img in self.stream_images[stream_id]
                if img.image_id != image_id
            ]
            
            # Delete files
            stream_dir = self.images_dir / stream_id
            for file in stream_dir.glob(f"{image_id}*"):
                file.unlink()
            
            self._save_images()
            return True
        except Exception as e:
            print(f"Error deleting image: {e}")
            return False
    
    def get_image_stats(self, stream_id: str) -> Dict:
        """Get statistics for stream images"""
        if stream_id not in self.stream_images:
            return {"total": 0, "public": 0, "private": 0, "total_size_mb": 0}
        
        images = self.stream_images[stream_id]
        total_size = sum(img.size_bytes for img in images)
        
        return {
            "total": len(images),
            "public": len([img for img in images if img.visibility == ImageVisibility.PUBLIC]),
            "private": len([img for img in images if img.visibility == ImageVisibility.PRIVATE]),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "most_viewed": max([img.view_count for img in images], default=0)
        }
    
    def _save_images(self):
        """Persist image metadata"""
        try:
            metadata_file = self.images_dir / "images_metadata.json"
            data = {
                stream_id: [img.to_dict() for img in images]
                for stream_id, images in self.stream_images.items()
            }
            with open(metadata_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving image metadata: {e}")
    
    def _load_images(self):
        """Load image metadata"""
        try:
            metadata_file = self.images_dir / "images_metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    data = json.load(f)
                    self.stream_images = {
                        stream_id: [StreamImage.from_dict(img) for img in images]
                        for stream_id, images in data.items()
                    }
        except Exception as e:
            print(f"Error loading image metadata: {e}")
