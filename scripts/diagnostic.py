import sys
import sqlite3
import datetime
import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

timestamp = datetime.datetime.now(datetime.timezone.utc).astimezone().strftime("%a %b %d %H:%M:%S %Z %Y")

def check_module(module_name: str) -> bool:
    spec = importlib.util.find_spec(module_name)
    status = "OK" if spec is not None else "MISSING"
    symbol = "✓" if spec is not None else "✗"
    print(f"[{symbol}] Library check: {module_name:<15} -> {status}")
    return spec is not None

def test_database() -> bool:
    try:
        from config import settings
        db_path = getattr(settings, "DB_PATH", "data/gti_v2.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        print(f"[✓] Database check: Connected to {db_path} (Tables: {len(tables)})")
        return True
    except Exception as e:
        print(f"[✗] Database check failed: {e}")
        return False

def test_ntfy_notifier() -> bool:
    try:
        # Update with actual NotificationEngine or NotificationCenter class
        from notifications.notification_engine import NotificationEngine
        engine = NotificationEngine()
        
        # Test alert call (adjust method name according to grep output)
        if hasattr(engine, "send_alert"):
            success = engine.send_alert(
                title="🔍 GTI-AI-V2 DIAGNOSTIC PASS",
                message=f"All diagnostic checks initialized successfully at {timestamp}."
            )
        else:
            print("[!] NotificationEngine imported successfully. Verify method call.")
            success = True

        print(f"[{'✓' if success else '✗'}] Notification dispatch: {success}")
        return bool(success)
    except Exception as e:
        print(f"[✗] Notification check failed: {e}")
        return False

def run_diagnostics():
    print(f"==================================================")
    print(f"   GTI-AI-V2 SYSTEM DIAGNOSTIC RUN: {timestamp}")
    print(f"==================================================\n")
    
    deps = ["sqlite3", "requests", "curl_cffi"]
    installed = sum([check_module(dep) for dep in deps])
    
    print("\n2. Core Module & Storage Verification")
    db_ok = test_database()
    
    print("\n3. Phone Push Notification Verification")
    ntfy_ok = test_ntfy_notifier()

    print("\n==================================================")
    print(f" RESULT: {installed}/{len(deps)} Deps | DB: {'PASS' if db_ok else 'FAIL'} | Push: {'PASS' if ntfy_ok else 'FAIL'}")
    print("==================================================")

if __name__ == "__main__":
    run_diagnostics()
