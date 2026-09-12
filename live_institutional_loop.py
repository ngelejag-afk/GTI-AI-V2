from __future__ import annotations

import time

import run_institutional_scan

SCAN_INTERVAL = 60


def main() -> None:
    print("=" * 60)
    print("GTI-AI-V2 INSTITUTIONAL LIVE LOOP")
    print("Mode: READ-ONLY")
    print("Trading: DISABLED")
    print(f"Scan interval: {SCAN_INTERVAL}s")
    print("=" * 60)

    while True:
        started = time.time()

        try:
            run_institutional_scan.main()
        except KeyboardInterrupt:
            print("\nInstitutional live loop stopped.")
            break
        except Exception as exc:
            print(
                f"LIVE LOOP ERROR: "
                f"{type(exc).__name__}: {exc}"
            )

        elapsed = time.time() - started
        sleep_for = max(1, SCAN_INTERVAL - int(elapsed))
        print(f"Next institutional scan in {sleep_for}s...")

        try:
            time.sleep(sleep_for)
        except KeyboardInterrupt:
            print("\nInstitutional live loop stopped.")
            break


if __name__ == "__main__":
    main()
