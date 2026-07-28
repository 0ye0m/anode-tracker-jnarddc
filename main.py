"""
Main entry point for the Anode Tracking System.
Initializes and runs the GUI application.
"""

import sys

from config import config
from gui.app import AnodeTrackerApp


def main():
    """Main function to start the application."""
    try:
        app = AnodeTrackerApp(config)
        app.run()
    except KeyboardInterrupt:
        print("\nApplication terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()