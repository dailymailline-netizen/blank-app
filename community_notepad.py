"""
Community Notepad - Collaborative note-taking with P2P sync support
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import uuid


class CommunityNotepad:
    """Manages collaborative notes with version tracking and peer sync"""
    
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.notes_dir = self.storage_path / "notes"
        self.notes_dir.mkdir(exist_ok=True)
        self.sync_log_file = self.storage_path / "sync_log.json"
    
    def create_note(self, title: str, content: str = "", tags: List[str] = None) -> str:
        """Create new collaborative note"""
        note_id = str(uuid.uuid4())
        note_data = {
            "id": note_id,
            "title": title,
            "content": content,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "version": 1,
            "contributors": ["system"],
            "is_shared": False,
            "last_sync": datetime.now().isoformat()
        }
        
        note_file = self.notes_dir / f"{note_id}.json"
        with open(note_file, 'w') as f:
            json.dump(note_data, f, indent=2)
        
        self._log_sync("note_created", note_id)
        return note_id
    
    def get_note(self, note_id: str) -> Optional[Dict]:
        """Retrieve note by ID"""
        note_file = self.notes_dir / f"{note_id}.json"
        try:
            if note_file.exists():
                with open(note_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error reading note: {e}")
        return None
    
    def update_note(self, note_id: str, content: str, contributor: str = "user") -> bool:
        """Update note content with version tracking"""
        note = self.get_note(note_id)
        if not note:
            return False
        
        try:
            note["content"] = content
            note["updated_at"] = datetime.now().isoformat()
            note["version"] += 1
            
            if contributor not in note.get("contributors", []):
                note["contributors"].append(contributor)
            
            note_file = self.notes_dir / f"{note_id}.json"
            with open(note_file, 'w') as f:
                json.dump(note, f, indent=2)
            
            self._log_sync("note_updated", note_id)
            return True
        except Exception as e:
            print(f"Error updating note: {e}")
            return False
    
    def delete_note(self, note_id: str) -> bool:
        """Delete note"""
        note_file = self.notes_dir / f"{note_id}.json"
        try:
            if note_file.exists():
                note_file.unlink()
                self._log_sync("note_deleted", note_id)
                return True
        except Exception as e:
            print(f"Error deleting note: {e}")
        return False
    
    def list_notes(self, shared_only: bool = False) -> List[Dict]:
        """List all notes, optionally filtered to shared only"""
        notes = []
        try:
            for note_file in self.notes_dir.glob("*.json"):
                with open(note_file, 'r') as f:
                    note = json.load(f)
                    if not shared_only or note.get("is_shared", False):
                        notes.append(note)
        except Exception as e:
            print(f"Error listing notes: {e}")
        
        return sorted(notes, key=lambda n: n.get("updated_at", ""), reverse=True)
    
    def share_note(self, note_id: str) -> bool:
        """Make note visible to community"""
        note = self.get_note(note_id)
        if not note:
            return False
        
        try:
            note["is_shared"] = True
            note["shared_at"] = datetime.now().isoformat()
            
            note_file = self.notes_dir / f"{note_id}.json"
            with open(note_file, 'w') as f:
                json.dump(note, f, indent=2)
            
            self._log_sync("note_shared", note_id)
            return True
        except Exception as e:
            print(f"Error sharing note: {e}")
            return False
    
    def unshare_note(self, note_id: str) -> bool:
        """Make note private"""
        note = self.get_note(note_id)
        if not note:
            return False
        
        try:
            note["is_shared"] = False
            
            note_file = self.notes_dir / f"{note_id}.json"
            with open(note_file, 'w') as f:
                json.dump(note, f, indent=2)
            
            self._log_sync("note_unshared", note_id)
            return True
        except Exception as e:
            print(f"Error unsharing note: {e}")
            return False
    
    def search_notes(self, query: str) -> List[Dict]:
        """Search notes by title, content, or tags"""
        all_notes = self.list_notes()
        query_lower = query.lower()
        
        results = []
        for note in all_notes:
            if (query_lower in note.get("title", "").lower() or
                query_lower in note.get("content", "").lower() or
                any(query_lower in tag.lower() for tag in note.get("tags", []))):
                results.append(note)
        
        return results
    
    def get_sync_history(self, limit: int = 100) -> List[Dict]:
        """Get recent synchronization history"""
        try:
            if self.sync_log_file.exists():
                with open(self.sync_log_file, 'r') as f:
                    logs = json.load(f)
                    return logs[-limit:]
        except Exception as e:
            print(f"Error reading sync history: {e}")
        return []
    
    def _log_sync(self, action: str, note_id: str):
        """Log synchronization event"""
        try:
            logs = []
            if self.sync_log_file.exists():
                with open(self.sync_log_file, 'r') as f:
                    logs = json.load(f)
            
            logs.append({
                "action": action,
                "note_id": note_id,
                "timestamp": datetime.now().isoformat(),
                "node": "local"
            })
            
            with open(self.sync_log_file, 'w') as f:
                json.dump(logs, f, indent=2)
        except Exception as e:
            print(f"Error logging sync: {e}")


class P2PPeerManager:
    """Manages peer-to-peer connections for note syncing"""
    
    def __init__(self, node_name: str, port: int):
        self.node_name = node_name
        self.port = port
        self.peers: Dict[str, Dict] = {}
        self.sync_queue = []
    
    def register_peer(self, peer_id: str, peer_address: str) -> bool:
        """Register a peer node"""
        try:
            self.peers[peer_id] = {
                "id": peer_id,
                "address": peer_address,
                "registered_at": datetime.now().isoformat(),
                "status": "online",
                "last_sync": None
            }
            print(f"Peer registered: {peer_id} @ {peer_address}")
            return True
        except Exception as e:
            print(f"Error registering peer: {e}")
            return False
    
    def unregister_peer(self, peer_id: str) -> bool:
        """Unregister a peer node"""
        try:
            if peer_id in self.peers:
                del self.peers[peer_id]
                return True
        except Exception as e:
            print(f"Error unregistering peer: {e}")
        return False
    
    def queue_sync(self, note_id: str, action: str):
        """Queue a note for sync to peers"""
        self.sync_queue.append({
            "note_id": note_id,
            "action": action,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_peers(self, status: str = None) -> List[Dict]:
        """Get list of peers, optionally filtered by status"""
        if status:
            return [p for p in self.peers.values() if p["status"] == status]
        return list(self.peers.values())
    
    def sync_to_peers(self, note_id: str, note_data: Dict) -> Dict[str, bool]:
        """Broadcast note to all connected peers"""
        results = {}
        for peer_id, peer_info in self.peers.items():
            try:
                # Simulate peer sync (would use actual P2P protocol like Bonjour/Avahi)
                results[peer_id] = True
                print(f"Synced {note_id} to peer {peer_id}")
            except Exception as e:
                print(f"Failed to sync to peer {peer_id}: {e}")
                results[peer_id] = False
        
        return results


class NotePadAnalytics:
    """Analytics tracking for community notepad"""
    
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.analytics_file = self.storage_path / "analytics.json"
    
    def record_event(self, event_type: str, note_id: str, user: str = "anonymous"):
        """Record user activity"""
        try:
            events = []
            if self.analytics_file.exists():
                with open(self.analytics_file, 'r') as f:
                    events = json.load(f)
            
            events.append({
                "type": event_type,
                "note_id": note_id,
                "user": user,
                "timestamp": datetime.now().isoformat()
            })
            
            with open(self.analytics_file, 'w') as f:
                json.dump(events, f, indent=2)
        except Exception as e:
            print(f"Error recording analytics: {e}")
    
    def get_stats(self) -> Dict:
        """Get notepad statistics"""
        try:
            if self.analytics_file.exists():
                with open(self.analytics_file, 'r') as f:
                    events = json.load(f)
                
                return {
                    "total_events": len(events),
                    "unique_users": len(set(e["user"] for e in events)),
                    "events_by_type": self._count_by_type(events),
                    "last_activity": events[-1]["timestamp"] if events else None
                }
        except Exception as e:
            print(f"Error getting stats: {e}")
        
        return {}
    
    def _count_by_type(self, events: List[Dict]) -> Dict[str, int]:
        """Count events by type"""
        counts = {}
        for event in events:
            event_type = event["type"]
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts
