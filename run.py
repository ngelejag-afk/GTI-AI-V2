"""
GTI AI
Runner
Version 2.0
"""

from __future__ import annotations

import time

from main import main


REFRESH_SECONDS = 60


def run() -> None:
    """
    Runs the GTI AI system continuously.
    """

    print("=" * 50)
    print(" GTI AI V2 RUNNER")
    print("=" * 50)

    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("\nGTI AI stopped.")
            break
        except Exception as error:
            print(f"System Error: {error}")

        print(f"\nRestarting in {REFRESH_SECONDS} seconds...")
        time.sleep(REFRESH_SECONDS)


if __name__ == "__main__":
    run()
