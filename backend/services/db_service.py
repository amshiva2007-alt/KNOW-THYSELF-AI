"""
Know Thyself AI - Database Service
Provides unified access to Firebase Firestore with an automatic, resilient
local JSON datastore fallback for zero-friction local development.
"""

from datetime import datetime
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional
from backend.config import Config
from backend.data.sample_data import generate_30day_wellness_dataset

logger = logging.getLogger(__name__)


class DatabaseService:
    """Manages wellness record storage across Firestore and local JSON store."""

    def __init__(self):
        self.firestore_client = None
        self.use_firestore = False
        self._init_backend()

    def _init_backend(self):
        """Initializes Firebase Firestore if configured; otherwise logs local fallback."""
        if Config.has_firebase_credentials():
            try:
                import firebase_admin
                from firebase_admin import credentials, firestore

                cred_path = Path(Config.FIREBASE_CREDENTIALS_PATH)
                if not cred_path.is_absolute():
                    cred_path = Config.BASE_DIR / cred_path

                cred = credentials.Certificate(str(cred_path))
                if not firebase_admin._apps:
                    firebase_admin.initialize_app(cred, {
                        'projectId': Config.FIREBASE_PROJECT_ID
                    })
                self.firestore_client = firestore.client()
                self.use_firestore = True
                logger.info("Successfully connected to Firebase Firestore.")
                return
            except Exception as e:
                logger.warning(f"Firebase Firestore init failed: {e}. Falling back to local datastore.")

        # Local JSON database fallback
        self.use_firestore = False
        self._ensure_local_db_exists()

    def _ensure_local_db_exists(self):
        """Ensures the local JSON database exists and is populated with sample data."""
        Config.LOCAL_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not Config.LOCAL_DB_PATH.exists():
            if Config.SAMPLE_DATA_PATH.exists():
                with open(Config.SAMPLE_DATA_PATH, "r", encoding="utf-8") as sf:
                    data = json.load(sf)
            else:
                data = generate_30day_wellness_dataset()

            with open(Config.LOCAL_DB_PATH, "w", encoding="utf-8") as df:
                json.dump(data, df, indent=2)
            logger.info("Initialized local JSON database with 30-day wellness dataset.")

    def _read_local_db(self) -> List[Dict]:
        """Reads all records from local JSON database."""
        self._ensure_local_db_exists()
        try:
            with open(Config.LOCAL_DB_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading local db: {e}")
            return generate_30day_wellness_dataset()

    def _write_local_db(self, records: List[Dict]):
        """Writes records to local JSON database."""
        self._ensure_local_db_exists()
        with open(Config.LOCAL_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)

    def get_all_records(self, limit: Optional[int] = None) -> List[Dict]:
        """Retrieves wellness records ordered chronologically."""
        if self.use_firestore:
            try:
                coll = self.firestore_client.collection("wellness_records").order_by("date")
                if limit:
                    coll = coll.limit(limit)
                docs = coll.stream()
                return [d.to_dict() for d in docs]
            except Exception as e:
                logger.error(f"Firestore get_all_records error: {e}. Reading local db.")

        records = self._read_local_db()
        records.sort(key=lambda r: r.get("date", ""))
        if limit:
            return records[-limit:]
        return records

    def get_record_by_id(self, record_id: str) -> Optional[Dict]:
        """Retrieves a single record by its identifier."""
        if self.use_firestore:
            try:
                doc = self.firestore_client.collection("wellness_records").document(record_id).get()
                if doc.exists:
                    return doc.to_dict()
                return None
            except Exception as e:
                logger.error(f"Firestore get_record_by_id error: {e}")

        records = self._read_local_db()
        for r in records:
            if r.get("id") == record_id:
                return r
        return None

    def save_record(self, record: Dict) -> Dict:
        """Saves or updates a wellness record."""
        if "id" not in record or not record["id"]:
            date_str = record.get("date", datetime.now().strftime("%Y-%m-%d"))
            record["id"] = f"day-{date_str}"
        if "timestamp" not in record:
            record["timestamp"] = datetime.utcnow().isoformat() + "Z"

        if self.use_firestore:
            try:
                doc_ref = self.firestore_client.collection("wellness_records").document(record["id"])
                doc_ref.set(record)
                return record
            except Exception as e:
                logger.error(f"Firestore save_record error: {e}. Saving locally.")

        records = self._read_local_db()
        found = False
        for idx, r in enumerate(records):
            if r.get("id") == record["id"]:
                records[idx] = record
                found = True
                break
        if not found:
            records.append(record)

        records.sort(key=lambda r: r.get("date", ""))
        self._write_local_db(records)
        return record

    def reset_to_sample_data(self) -> List[Dict]:
        """Resets the dataset to fresh 30-day realistic sample data."""
        data = generate_30day_wellness_dataset()
        if self.use_firestore:
            try:
                batch = self.firestore_client.batch()
                for item in data:
                    ref = self.firestore_client.collection("wellness_records").document(item["id"])
                    batch.set(ref, item)
                batch.commit()
            except Exception as e:
                logger.warning(f"Could not batch reset Firestore: {e}")

        self._write_local_db(data)
        return data

    def get_database_status(self) -> Dict:
        """Returns metadata on current database connection mode."""
        records = self.get_all_records()
        return {
            "mode": "Firebase Firestore" if self.use_firestore else "Local Datastore (JSON)",
            "connected": True,
            "record_count": len(records),
            "firestore_configured": Config.has_firebase_credentials(),
            "latest_record_date": records[-1].get("date") if records else None
        }


# Singleton database instance
db = DatabaseService()
