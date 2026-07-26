"""
GTI AI
Runner
Version 1.0
"""

import time

from main_ai import main


REFRESH_SECONDS = 60


def run() -> None:
    """
    Runs the AI continuously.
    """
    print("===================================")
    print(" GTI AI V4 RUNNER STARTED")
    print("===================================")

    while True:
        try:
            main()
        except Exception as error:
            print(f"ERROR: {error}")

        print(f"Waiting {REFRESH_SECONDS} seconds...\n")
        time.sleep(REFRESH_SECONDS)


if __name__ == "__main__":
    run()
