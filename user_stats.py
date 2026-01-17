"""
User Statistics & Analytics System
Records user activity with safe defaults and subscriber features
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import uuid
from enum import Enum
from dataclasses import dataclass, field, asdict
import hashlib


class UserRole(Enum):
    """User role levels"""
    FREE = "free"
    SUBSCRIBER = "subscriber"
    PREMIUM = "premium"
    ADMIN = "admin"


class SubscriberFeature(Enum):
    """Premium subscriber features"""
    CUSTOM_BRANDING = "custom_branding"
    PRIORITY_UPLOAD = "priority_upload"
    ADVANCED_ANALYTICS = "advanced_analytics"
    HD_STREAMING = "hd_streaming"
    AD_FREE = "ad_free"
    EARLY_ACCESS = "early_access"
    CUSTOM_PLAYLISTS = "custom_playlists"
    BULK_OPERATIONS = "bulk_operations"


@dataclass
class WatchHistoryEntry:
    """Single watch history entry"""
    video_id: str
    stream_id: Optional[str]
    watched_at: str  # ISO timestamp
    duration_seconds: int
    content_type: str  # "video" | "stream" | "image"
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    completed: bool = False
    quality: str = "720p"
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict) -> "WatchHistoryEntry":
        return WatchHistoryEntry(**data)


@dataclass
class UserStats:
    """User statistics container (8 main stats)"""
    user_id: str
    
    # Stat 1: Subscriber Features Used
    subscriber_features_used: int = 0
    
    # Stat 2: Watch History Entries
    watch_history_entries: int = 0
    
    # Stat 3: Total Watched Hours
    total_watched_hours: float = 0.0
    
    # Stat 4: Videos Uploaded
    videos_uploaded: int = 0
    
    # Stat 5: Streams Created
    streams_created: int = 0
    
    # Stat 6: Images Uploaded
    images_uploaded: int = 0
    
    # Stat 7: Total Interactions
    total_interactions: int = 0  # likes, comments, shares
    
    # Stat 8: Last Activity
    last_activity_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict) -> "UserStats":
        return UserStats(**data)
    
    def increment_stat(self, stat_name: str, amount: int = 1) -> None:
        """Increment a stat by amount"""
        if hasattr(self, stat_name):
            current = getattr(self, stat_name)
            setattr(self, stat_name, current + amount)
            self.updated_at = datetime.now().isoformat()


class WatchHistoryTracker:
    """Track and manage user watch history"""
    
    def __init__(self, history_dir: Path):
        self.history_dir = history_dir
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.max_entries = 1000  # Max entries per user
    
    def add_watch_entry(self, user_id: str, video_id: str, 
                        duration_seconds: int, content_type: str,
                        stream_id: Optional[str] = None,
                        quality: str = "720p") -> WatchHistoryEntry:
        """Record a watch event"""
        entry = WatchHistoryEntry(
            video_id=video_id,
            stream_id=stream_id,
            watched_at=datetime.now().isoformat(),
            duration_seconds=duration_seconds,
            content_type=content_type,
            quality=quality,
            completed=False  # Mark as completed if duration > 90% watched
        )
        
        # Save entry
        user_history = self._get_user_history(user_id)
        user_history.append(entry.to_dict())
        
        # Keep only last max_entries
        if len(user_history) > self.max_entries:
            user_history = user_history[-self.max_entries:]
        
        self._save_user_history(user_id, user_history)
        
        return entry
    
    def get_watch_history(self, user_id: str, limit: int = 100) -> List[WatchHistoryEntry]:
        """Get user's watch history"""
        history = self._get_user_history(user_id)
        # Return most recent entries first
        return [WatchHistoryEntry.from_dict(entry) for entry in history[-limit:][::-1]]
    
    def get_total_watched_hours(self, user_id: str) -> float:
        """Calculate total watched hours"""
        history = self._get_user_history(user_id)
        total_seconds = sum(entry.get('duration_seconds', 0) for entry in history)
        return round(total_seconds / 3600, 2)
    
    def get_watch_stats_by_type(self, user_id: str) -> Dict[str, Dict]:
        """Get statistics grouped by content type"""
        history = self._get_user_history(user_id)
        stats = {}
        
        for entry in history:
            content_type = entry.get('content_type', 'unknown')
            if content_type not in stats:
                stats[content_type] = {
                    'count': 0,
                    'total_seconds': 0,
                    'avg_duration': 0
                }
            
            stats[content_type]['count'] += 1
            stats[content_type]['total_seconds'] += entry.get('duration_seconds', 0)
        
        # Calculate averages
        for content_type in stats:
            count = stats[content_type]['count']
            if count > 0:
                stats[content_type]['avg_duration'] = round(
                    stats[content_type]['total_seconds'] / count, 2
                )
        
        return stats
    
    def clear_watch_history(self, user_id: str) -> int:
        """Clear user's watch history"""
        history_file = self.history_dir / f"{user_id}_history.json"
        if history_file.exists():
            history_file.unlink()
            return 1
        return 0
    
    def _get_user_history(self, user_id: str) -> List[Dict]:
        """Load user's watch history"""
        history_file = self.history_dir / f"{user_id}_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_user_history(self, user_id: str, history: List[Dict]) -> None:
        """Save user's watch history"""
        history_file = self.history_dir / f"{user_id}_history.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")


class UserManager:
    """Manage users and their statistics"""
    
    def __init__(self, users_dir: Path, history_dir: Path):
        self.users_dir = users_dir
        self.users_dir.mkdir(parents=True, exist_ok=True)
        self.history_tracker = WatchHistoryTracker(history_dir)
        
        # In-memory user cache
        self.users: Dict[str, Dict] = {}
        self.user_stats: Dict[str, UserStats] = {}
        self.subscriber_features: Dict[str, List[SubscriberFeature]] = {}
        
        self._load_users()
    
    def create_user(self, username: str, email: str, role: UserRole = UserRole.FREE) -> str:
        """Create new user"""
        user_id = str(uuid.uuid4())
        
        user_data = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "role": role.value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "is_active": True,
            "subscription_expires": None if role == UserRole.FREE else (
                datetime.now() + timedelta(days=365)
            ).isoformat()
        }
        
        self.users[user_id] = user_data
        self.user_stats[user_id] = UserStats(user_id=user_id)
        self.subscriber_features[user_id] = self._get_default_features(role)
        
        self._save_users()
        
        return user_id
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_stats(self, user_id: str) -> Optional[UserStats]:
        """Get user statistics"""
        return self.user_stats.get(user_id)
    
    def record_watch_activity(self, user_id: str, video_id: str,
                            duration_seconds: int, content_type: str,
                            stream_id: Optional[str] = None) -> bool:
        """Record watch activity"""
        if user_id not in self.users:
            return False
        
        try:
            # Add to watch history
            self.history_tracker.add_watch_entry(
                user_id, video_id, duration_seconds, content_type, stream_id
            )
            
            # Update stats
            stats = self.user_stats[user_id]
            stats.watch_history_entries += 1
            total_hours = self.history_tracker.get_total_watched_hours(user_id)
            stats.total_watched_hours = total_hours
            stats.last_activity_timestamp = datetime.now().isoformat()
            stats.updated_at = datetime.now().isoformat()
            
            self._save_users()
            return True
        except Exception as e:
            print(f"Error recording watch activity: {e}")
            return False
    
    def record_upload(self, user_id: str, content_type: str) -> bool:
        """Record upload activity"""
        if user_id not in self.users:
            return False
        
        try:
            stats = self.user_stats[user_id]
            
            if content_type == "video":
                stats.videos_uploaded += 1
            elif content_type == "stream":
                stats.streams_created += 1
            elif content_type == "image":
                stats.images_uploaded += 1
            
            stats.last_activity_timestamp = datetime.now().isoformat()
            stats.updated_at = datetime.now().isoformat()
            
            self._save_users()
            return True
        except Exception as e:
            print(f"Error recording upload: {e}")
            return False
    
    def record_interaction(self, user_id: str, interaction_type: str) -> bool:
        """Record user interaction (like, comment, share)"""
        if user_id not in self.users:
            return False
        
        try:
            stats = self.user_stats[user_id]
            stats.total_interactions += 1
            stats.last_activity_timestamp = datetime.now().isoformat()
            stats.updated_at = datetime.now().isoformat()
            
            self._save_users()
            return True
        except Exception as e:
            print(f"Error recording interaction: {e}")
            return False
    
    def use_subscriber_feature(self, user_id: str, feature: SubscriberFeature) -> bool:
        """Record subscriber feature usage"""
        if user_id not in self.subscriber_features:
            return False
        
        if feature in self.subscriber_features[user_id]:
            stats = self.user_stats[user_id]
            stats.subscriber_features_used += 1
            stats.last_activity_timestamp = datetime.now().isoformat()
            stats.updated_at = datetime.now().isoformat()
            
            self._save_users()
            return True
        
        return False
    
    def upgrade_subscription(self, user_id: str, role: UserRole, days: int = 365) -> bool:
        """Upgrade user subscription"""
        if user_id not in self.users:
            return False
        
        try:
            user = self.users[user_id]
            user['role'] = role.value
            user['subscription_expires'] = (
                datetime.now() + timedelta(days=days)
            ).isoformat()
            user['updated_at'] = datetime.now().isoformat()
            
            self.subscriber_features[user_id] = self._get_default_features(role)
            
            self._save_users()
            return True
        except Exception as e:
            print(f"Error upgrading subscription: {e}")
            return False
    
    def get_all_users_stats(self) -> Dict[str, UserStats]:
        """Get all user statistics"""
        return self.user_stats.copy()
    
    def get_active_users(self) -> List[Dict]:
        """Get all active users"""
        return [user for user in self.users.values() if user.get('is_active', True)]
    
    def get_subscribers(self) -> List[Dict]:
        """Get all subscriber users"""
        return [
            user for user in self.users.values()
            if user.get('role') in ['subscriber', 'premium']
        ]
    
    def _get_default_features(self, role: UserRole) -> List[SubscriberFeature]:
        """Get features based on role"""
        if role == UserRole.FREE:
            return []
        elif role == UserRole.SUBSCRIBER:
            return [
                SubscriberFeature.PRIORITY_UPLOAD,
                SubscriberFeature.HD_STREAMING,
                SubscriberFeature.AD_FREE,
                SubscriberFeature.CUSTOM_PLAYLISTS
            ]
        elif role == UserRole.PREMIUM:
            return [
                SubscriberFeature.CUSTOM_BRANDING,
                SubscriberFeature.PRIORITY_UPLOAD,
                SubscriberFeature.ADVANCED_ANALYTICS,
                SubscriberFeature.HD_STREAMING,
                SubscriberFeature.AD_FREE,
                SubscriberFeature.EARLY_ACCESS,
                SubscriberFeature.CUSTOM_PLAYLISTS,
                SubscriberFeature.BULK_OPERATIONS
            ]
        else:  # ADMIN
            return list(SubscriberFeature)
    
    def _save_users(self):
        """Persist users and stats"""
        try:
            # Save user data
            users_file = self.users_dir / "users.json"
            with open(users_file, 'w') as f:
                json.dump(self.users, f, indent=2)
            
            # Save stats
            stats_file = self.users_dir / "user_stats.json"
            stats_data = {
                user_id: stats.to_dict()
                for user_id, stats in self.user_stats.items()
            }
            with open(stats_file, 'w') as f:
                json.dump(stats_data, f, indent=2)
            
            # Save subscriber features
            features_file = self.users_dir / "subscriber_features.json"
            features_data = {
                user_id: [f.value for f in features]
                for user_id, features in self.subscriber_features.items()
            }
            with open(features_file, 'w') as f:
                json.dump(features_data, f, indent=2)
        
        except Exception as e:
            print(f"Error saving users: {e}")
    
    def _load_users(self):
        """Load users and stats"""
        try:
            # Load user data
            users_file = self.users_dir / "users.json"
            if users_file.exists():
                with open(users_file, 'r') as f:
                    self.users = json.load(f)
            
            # Load stats
            stats_file = self.users_dir / "user_stats.json"
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    stats_data = json.load(f)
                    self.user_stats = {
                        user_id: UserStats.from_dict(data)
                        for user_id, data in stats_data.items()
                    }
            
            # Create missing stats
            for user_id in self.users:
                if user_id not in self.user_stats:
                    self.user_stats[user_id] = UserStats(user_id=user_id)
            
            # Load subscriber features
            features_file = self.users_dir / "subscriber_features.json"
            if features_file.exists():
                with open(features_file, 'r') as f:
                    features_data = json.load(f)
                    self.subscriber_features = {
                        user_id: [SubscriberFeature(f) for f in features]
                        for user_id, features in features_data.items()
                    }
            
            # Create missing features
            for user_id, user in self.users.items():
                if user_id not in self.subscriber_features:
                    role = UserRole(user.get('role', 'free'))
                    self.subscriber_features[user_id] = self._get_default_features(role)
        
        except Exception as e:
            print(f"Error loading users: {e}")
