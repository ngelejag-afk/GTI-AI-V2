"""
GTI AI
Main Entry Point
Version 3.0
"""

from __future__ import annotations

from controller.gti_controller import GTIController


def main() -> None:
    """
    Start the GTI AI system.
    """

    controller = GTIController(
        simulation_mode=True,
        dashboard_host="0.0.0.0",
        dashboard_port=8000,
    )

    controller.start()


if __name__ == "__main__":
    main()
