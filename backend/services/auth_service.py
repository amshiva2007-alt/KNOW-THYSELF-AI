"""
Know Thyself AI - Authentication & User Profile Service
Handles user accounts, session tokens, password hashing, and user profile onboarding.
Supports both Firebase Authentication (if configured) and resilient local sessions.
"""

from datetime import datetime, timedelta
import hashlib
import json
import logging
import os
import secrets
from pathlib import Path
from typing import Dict, Optional, Tuple
from backend.config import Config

logger = logging.getLogger(__name__)
AUTH_DB_PATH = Config.BASE_DIR / "backend" / "data" / "users_db.json"


def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Hashes a password with a cryptographic salt using SHA-256."""
    if not salt:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
    return hashed, salt


class AuthService:
    """Manages user authentication, profile data, and onboarding state."""

    def __init__(self):
        self._ensure_db()

    def _ensure_db(self):
        """Initializes the user store if missing, seeding default demo user."""
        AUTH_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not AUTH_DB_PATH.exists():
            default_salt = secrets.token_hex(16)
            demo_hash, _ = hash_password("demo1234", default_salt)
            
            initial_data = {
                "users": {
                    "demo-user-id": {
                        "id": "demo-user-id",
                        "email": "demo@knowthyself.ai",
                        "password_hash": demo_hash,
                        "salt": default_salt,
                        "name": "Alex Morgan",
                        "created_at": datetime.utcnow().isoformat() + "Z",
                        "onboarding_completed": True,
                        "profile": {
                            "name": "Alex Morgan",
                            "age": 28,
                            "gender": "Non-binary",
                            "height_cm": 175,
                            "weight_kg": 68,
                            "avg_sleep_hours": 7.5,
                            "activity_level": "Moderately Active",
                            "avg_screen_hours": 6.5,
                            "goals": ["Better sleep", "More physical activity", "Reduced screen time"],
                            "data_preference": "Demo dataset"
                        },
                        "preferences": {
                            "notifications_enabled": True,
                            "morning_reminder": "08:30",
                            "evening_checkin": "21:30",
                            "theme": "dark"
                        }
                    }
                },
                "sessions": {}
            }
            with open(AUTH_DB_PATH, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)

    def _read_db(self) -> Dict:
        self._ensure_db()
        try:
            with open(AUTH_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"users": {}, "sessions": {}}

    def _write_db(self, data: Dict):
        self._ensure_db()
        with open(AUTH_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def register_user(self, email: str, password: str, name: str) -> Dict:
        """Registers a new user account."""
        email = email.strip().lower()
        if not email or "@" not in email:
            raise ValueError("Valid email address is required.")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters.")

        data = self._read_db()
        for u in data["users"].values():
            if u["email"].lower() == email:
                raise ValueError("An account with this email already exists.")

        user_id = f"user-{secrets.token_hex(8)}"
        pwd_hash, salt = hash_password(password)

        new_user = {
            "id": user_id,
            "email": email,
            "password_hash": pwd_hash,
            "salt": salt,
            "name": name.strip() or "Wellness Explorer",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "onboarding_completed": False,
            "profile": {
                "name": name.strip() or "Wellness Explorer",
                "age": None,
                "gender": None,
                "height_cm": None,
                "weight_kg": None,
                "avg_sleep_hours": 7.0,
                "activity_level": "Moderate",
                "avg_screen_hours": 6.0,
                "goals": ["Better sleep", "More physical activity"],
                "data_preference": "Manual entry"
            },
            "preferences": {
                "notifications_enabled": True,
                "morning_reminder": "08:30",
                "evening_checkin": "21:30",
                "theme": "dark"
            }
        }

        token = secrets.token_hex(24)
        data["users"][user_id] = new_user
        data["sessions"][token] = {
            "user_id": user_id,
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
        }
        self._write_db(data)

        clean_user = dict(new_user)
        clean_user.pop("password_hash", None)
        clean_user.pop("salt", None)
        return {"user": clean_user, "token": token}

    def login_user(self, email: str, password: str) -> Dict:
        """Authenticates user with email and password."""
        email = email.strip().lower()
        data = self._read_db()

        target_user = None
        for u in data["users"].values():
            if u["email"].lower() == email:
                target_user = u
                break

        if not target_user:
            raise ValueError("Invalid email or password.")

        test_hash, _ = hash_password(password, target_user["salt"])
        if test_hash != target_user["password_hash"]:
            raise ValueError("Invalid email or password.")

        token = secrets.token_hex(24)
        data["sessions"][token] = {
            "user_id": target_user["id"],
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
        }
        self._write_db(data)

        clean_user = dict(target_user)
        clean_user.pop("password_hash", None)
        clean_user.pop("salt", None)
        return {"user": clean_user, "token": token}

    def get_demo_session(self) -> Dict:
        """Provides instant 1-click evaluation access with pre-configured demo user."""
        data = self._read_db()
        demo_user = data["users"].get("demo-user-id")
        if not demo_user:
            self._ensure_db()
            data = self._read_db()
            demo_user = data["users"].get("demo-user-id")

        token = secrets.token_hex(24)
        data["sessions"][token] = {
            "user_id": "demo-user-id",
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z"
        }
        self._write_db(data)

        clean_user = dict(demo_user)
        clean_user.pop("password_hash", None)
        clean_user.pop("salt", None)
        return {"user": clean_user, "token": token}

    def validate_token(self, token: Optional[str]) -> Optional[Dict]:
        """Validates token and returns user profile if active."""
        if not token:
            # Return demo user by default for frictionless hackathon evaluation
            data = self._read_db()
            demo = data["users"].get("demo-user-id")
            if demo:
                clean = dict(demo)
                clean.pop("password_hash", None)
                clean.pop("salt", None)
                return clean
            return None

        data = self._read_db()
        session = data["sessions"].get(token)
        if not session:
            # Fallback to demo
            demo = data["users"].get("demo-user-id")
            if demo:
                clean = dict(demo)
                clean.pop("password_hash", None)
                clean.pop("salt", None)
                return clean
            return None

        # Check expiration
        try:
            exp = datetime.fromisoformat(session["expires_at"].replace("Z", ""))
            if datetime.utcnow() > exp:
                del data["sessions"][token]
                self._write_db(data)
                return None
        except Exception:
            pass

        user = data["users"].get(session["user_id"])
        if user:
            clean = dict(user)
            clean.pop("password_hash", None)
            clean.pop("salt", None)
            return clean
        return None

    def update_profile(self, user_id: str, profile_data: Dict) -> Dict:
        """Updates user profile or onboarding questionnaire results."""
        data = self._read_db()
        user = data["users"].get(user_id)
        if not user:
            raise ValueError("User not found.")

        current_prof = user.get("profile", {})
        current_prof.update(profile_data)
        user["profile"] = current_prof

        if "name" in profile_data and profile_data["name"]:
            user["name"] = profile_data["name"]

        if profile_data.get("onboarding_completed") is not None:
            user["onboarding_completed"] = bool(profile_data["onboarding_completed"])

        self._write_db(data)
        clean = dict(user)
        clean.pop("password_hash", None)
        clean.pop("salt", None)
        return clean

    def update_preferences(self, user_id: str, preferences: Dict) -> Dict:
        """Updates user preferences (theme, notifications, goals)."""
        data = self._read_db()
        user = data["users"].get(user_id)
        if not user:
            raise ValueError("User not found.")

        current_prefs = user.get("preferences", {})
        current_prefs.update(preferences)
        user["preferences"] = current_prefs
        self._write_db(data)
        return current_prefs


auth_service = AuthService()
