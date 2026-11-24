"""
Know Thyself AI - Root Execution Script
Run with: python run.py
"""

import sys
from pathlib import Path

# Ensure root directory is on python path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from backend.app import create_app
from backend.config import Config
from backend.services.db_service import db

if __name__ == "__main__":
    app = create_app()
    db_status = db.get_database_status()

    print("\n" + "=" * 65)
    print("  🚀 KNOW THYSELF AI - WELLNESS INTELLIGENCE PLATFORM")
    print("  Tagline: 'Your Data. Your Intelligence.'")
    print("=" * 65)
    print(f"  • Local Web URL      : http://localhost:{Config.PORT}")
    print(f"  • Network Web URL    : http://127.0.0.1:{Config.PORT}")
    print(f"  • Database Mode      : {db_status.get('mode')} ({db_status.get('record_count')} days loaded)")
    print(f"  • Gemini AI Engine   : {'Enabled (Cloud API)' if Config.has_gemini_key() else 'Active (Built-in Heuristic AI)'}")
    print(f"  • Health Endpoint    : http://localhost:{Config.PORT}/api/health")
    print("=" * 65)
    print("  Press Ctrl+C to stop the server.\n")

    app.run(host=Config.HOST, port=Config.PORT, debug=False)
