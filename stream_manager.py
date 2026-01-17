"""
Advanced stream management module for Stream & Upload Hub
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
import json
from pathlib import Path
import uuid


@dataclass
class StreamStats:
    """Stream statistics data class"""
    viewers: int = 0
    upload_speed: float = 0.0  # Mbps
    bitrate: float = 0.0  # Mbps
    frames_per_second: float = 0.0
    duration_seconds: int = 0
    resolution: str = "1080p"


class StreamManager:
    """Manages stream lifecycle and operations"""
    
    def __init__(self, streams_dir: Path):
        self.streams_dir = streams_dir
        self.active_streams: Dict[str, dict] = {}
        self.streams_dir.mkdir(exist_ok=True)
    
    def create_stream(self, name: str, description: str, resolution: str, 
                     bitrate: str) -> str:
        """Create a new stream and return stream ID"""
        stream_id = str(uuid.uuid4())
        stream_data = {
            "id": stream_id,
            "name": name,
            "description": description,
            "resolution": resolution,
            "bitrate": bitrate,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "stats": {
                "viewers": 0,
                "upload_speed": 0.0,
                "bitrate": float(bitrate.split()[0]),
                "frames_per_second": 30.0,
                "duration_seconds": 0,
            }
        }
        
        self.active_streams[stream_id] = stream_data
        self._save_stream(stream_id, stream_data)
        return stream_id
    
    def get_stream(self, stream_id: str) -> Optional[dict]:
        """Get stream information"""
        if stream_id in self.active_streams:
            return self.active_streams[stream_id]
        return self._load_stream(stream_id)
    
    def update_stream_stats(self, stream_id: str, stats: StreamStats) -> bool:
        """Update stream statistics"""
        if stream_id in self.active_streams:
            self.active_streams[stream_id]["stats"] = {
                "viewers": stats.viewers,
                "upload_speed": stats.upload_speed,
                "bitrate": stats.bitrate,
                "frames_per_second": stats.frames_per_second,
                "duration_seconds": stats.duration_seconds,
                "resolution": stats.resolution,
            }
            self.active_streams[stream_id]["updated_at"] = datetime.now().isoformat()
            self._save_stream(stream_id, self.active_streams[stream_id])
            return True
        return False
    
    def stop_stream(self, stream_id: str) -> bool:
        """Stop a stream"""
        if stream_id in self.active_streams:
            self.active_streams[stream_id]["status"] = "stopped"
            self.active_streams[stream_id]["stopped_at"] = datetime.now().isoformat()
            self._save_stream(stream_id, self.active_streams[stream_id])
            return True
        return False
    
    def list_active_streams(self) -> List[dict]:
        """Get list of active streams"""
        return [s for s in self.active_streams.values() if s["status"] == "active"]
    
    def list_all_streams(self) -> List[dict]:
        """Get list of all streams"""
        return list(self.active_streams.values())
    
    def _save_stream(self, stream_id: str, stream_data: dict) -> bool:
        """Save stream data to file"""
        try:
            file_path = self.streams_dir / f"{stream_id}.json"
            with open(file_path, 'w') as f:
                json.dump(stream_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving stream: {e}")
            return False
    
    def _load_stream(self, stream_id: str) -> Optional[dict]:
        """Load stream data from file"""
        try:
            file_path = self.streams_dir / f"{stream_id}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading stream: {e}")
        return None
    
    def delete_stream(self, stream_id: str) -> bool:
        """Delete a stream"""
        try:
            if stream_id in self.active_streams:
                del self.active_streams[stream_id]
            file_path = self.streams_dir / f"{stream_id}.json"
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e:
            print(f"Error deleting stream: {e}")
            return False


class VideoProcessor:
    """Handles video processing operations"""
    
    @staticmethod
    def get_video_duration(file_path: str) -> int:
        """Get video duration in seconds"""
        try:
            import cv2
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                return 0
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            cap.release()
            
            if fps > 0:
                return int(frame_count / fps)
            return 0
        except Exception as e:
            print(f"Error getting video duration: {e}")
            return 0
    
    @staticmethod
    def get_video_resolution(file_path: str) -> tuple:
        """Get video resolution (width, height)"""
        try:
            import cv2
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                return (0, 0)
            
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            return (width, height)
        except Exception as e:
            print(f"Error getting video resolution: {e}")
            return (0, 0)
    
    @staticmethod
    def create_thumbnail(video_path: str, output_path: str, 
                        timestamp: int = 0) -> bool:
        """Create thumbnail from video at specified timestamp"""
        try:
            import cv2
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return False
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(timestamp * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                cv2.imwrite(output_path, frame)
                return True
            return False
        except Exception as e:
            print(f"Error creating thumbnail: {e}")
            return False


class AnalyticsTracker:
    """Track analytics for streams and videos"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        self.events: List[dict] = []
    
    def log_event(self, event_type: str, stream_id: str, 
                  metadata: Optional[dict] = None) -> None:
        """Log an analytics event"""
        event = {
            "type": event_type,
            "stream_id": stream_id,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.events.append(event)
    
    def log_viewer_join(self, stream_id: str, viewer_id: str) -> None:
        """Log viewer joining stream"""
        self.log_event("viewer_join", stream_id, {"viewer_id": viewer_id})
    
    def log_viewer_leave(self, stream_id: str, viewer_id: str, 
                         watch_duration: int) -> None:
        """Log viewer leaving stream"""
        self.log_event("viewer_leave", stream_id, {
            "viewer_id": viewer_id,
            "watch_duration": watch_duration
        })
    
    def log_video_view(self, video_id: str, duration_watched: int) -> None:
        """Log video view"""
        self.log_event("video_view", video_id, {
            "duration_watched": duration_watched
        })
    
    def get_stream_analytics(self, stream_id: str) -> dict:
        """Get analytics for specific stream"""
        stream_events = [e for e in self.events if e["stream_id"] == stream_id]
        
        joins = len([e for e in stream_events if e["type"] == "viewer_join"])
        leaves = len([e for e in stream_events if e["type"] == "viewer_leave"])
        
        return {
            "stream_id": stream_id,
            "viewer_joins": joins,
            "viewer_leaves": leaves,
            "total_events": len(stream_events),
            "events": stream_events
        }
    
    def save_analytics(self, file_path: Path) -> bool:
        """Save analytics to file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(self.events, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving analytics: {e}")
            return False
