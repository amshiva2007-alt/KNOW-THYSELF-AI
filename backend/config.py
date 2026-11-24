"""
Know Thyself AI - Application Configuration
Handles environment variables and system settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Application configuration parameters."""
    BASE_DIR = BASE_DIR
    SECRET_KEY = os.getenv("SECRET_KEY", "know-thyself-ai-default-dev-secret-key-98213")
    DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")
    PORT = int(os.getenv("PORT", 5000))
    HOST = os.getenv("HOST", "0.0.0.0")

    # Google Gemini Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Firebase Firestore Configuration
    FIREBASE_CREDENTIALS_PATH = os.getenv("FIREBASE_CREDENTIALS_PATH", "config/firebase-service-account.json")
    FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "know-thyself-ai")

    # File paths
    LOCAL_DB_PATH = BASE_DIR / "backend" / "data" / "local_db.json"
    SAMPLE_DATA_PATH = BASE_DIR / "sample_data" / "wellness_demo.json"

    @classmethod
    def has_gemini_key(cls) -> bool:
        """Returns True if a real Gemini API key is configured."""
        return bool(cls.GEMINI_API_KEY and not cls.GEMINI_API_KEY.startswith("your_gemini_api_key"))

    @classmethod
    def has_firebase_credentials(cls) -> bool:
        """Returns True if valid Firebase credentials file exists."""
        cred_path = Path(cls.FIREBASE_CREDENTIALS_PATH)
        if not cred_path.is_absolute():
            cred_path = BASE_DIR / cred_path
        return cred_path.is_file()
