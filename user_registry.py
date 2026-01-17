"""
User Registry - Persistent User Database with Login/Authentication
Handles user registration, authentication, and profile management
"""

import json
import hashlib
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Tuple
import streamlit as st


class UserRegistry:
    """Persistent user registry with login credentials"""
    
    def __init__(self, registry_path: Path = Path("data/users")):
        self.registry_path = registry_path
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.registry_path / "registry.json"
        self.users = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """Load user registry from disk"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading registry: {e}")
                return {}
        return {}
    
    def _save_registry(self) -> bool:
        """Save user registry to disk"""
        try:
            with open(self.registry_file, "w") as f:
                json.dump(self.users, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving registry: {e}")
            return False
    
    def _hash_password(self, password: str) -> str:
        """Hash password with SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """
        Register a new user
        Returns: (success: bool, message: str or user_id: str)
        """
        # Validation
        if not username or not email or not password:
            return False, "❌ All fields are required"
        
        if len(username) < 3:
            return False, "❌ Username must be at least 3 characters"
        
        if len(password) < 6:
            return False, "❌ Password must be at least 6 characters"
        
        # Check if username or email already exists
        for user_id, user_data in self.users.items():
            if user_data["username"].lower() == username.lower():
                return False, "❌ Username already taken"
            if user_data["email"].lower() == email.lower():
                return False, "❌ Email already registered"
        
        # Create new user
        user_id = str(uuid.uuid4())
        password_hash = self._hash_password(password)
        
        self.users[user_id] = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "role": "free",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "is_active": True,
            "last_login": None,
            "subscription_expires": None
        }
        
        if self._save_registry():
            return True, user_id
        else:
            return False, "❌ Error saving user"
    
    def login_user(self, username: str, password: str) -> Tuple[bool, str]:
        """
        Authenticate user login
        Returns: (success: bool, user_id: str or message: str)
        """
        if not username or not password:
            return False, "❌ Please enter username and password"
        
        password_hash = self._hash_password(password)
        
        # Search for user by username
        for user_id, user_data in self.users.items():
            if user_data["username"].lower() == username.lower():
                # Check password
                if user_data["password_hash"] == password_hash:
                    # Update last login
                    user_data["last_login"] = datetime.now().isoformat()
                    self._save_registry()
                    return True, user_id
                else:
                    return False, "❌ Invalid password"
        
        return False, "❌ User not found"
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        for user_id, user_data in self.users.items():
            if user_data["username"].lower() == username.lower():
                return user_data
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        for user_id, user_data in self.users.items():
            if user_data["email"].lower() == email.lower():
                return user_data
        return None
    
    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user profile"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        
        # Allowed fields to update
        allowed_fields = ["email", "role", "is_active", "subscription_expires"]
        
        for key, value in kwargs.items():
            if key in allowed_fields:
                user[key] = value
        
        user["updated_at"] = datetime.now().isoformat()
        return self._save_registry()
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Change user password"""
        if user_id not in self.users:
            return False, "❌ User not found"
        
        user = self.users[user_id]
        old_hash = self._hash_password(old_password)
        
        if user["password_hash"] != old_hash:
            return False, "❌ Incorrect current password"
        
        if len(new_password) < 6:
            return False, "❌ New password must be at least 6 characters"
        
        user["password_hash"] = self._hash_password(new_password)
        if self._save_registry():
            return True, "✅ Password changed successfully"
        else:
            return False, "❌ Error saving password"
    
    def delete_user(self, user_id: str) -> bool:
        """Delete user account"""
        if user_id in self.users:
            del self.users[user_id]
            return self._save_registry()
        return False
    
    def list_all_users(self) -> list:
        """Get all users (admin function)"""
        return list(self.users.values())
    
    def get_user_count(self) -> int:
        """Get total user count"""
        return len(self.users)
    
    def validate_user(self, user_id: str) -> bool:
        """Check if user exists and is active"""
        user = self.users.get(user_id)
        return user is not None and user.get("is_active", False)


# Initialize global registry
@st.cache_resource
def get_user_registry() -> UserRegistry:
    """Get or create user registry (cached)"""
    return UserRegistry(Path("data/users"))
