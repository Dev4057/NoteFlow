"""
NoteFlow - MIDI Note Recorder
Main application entry point
"""

import logging
import os
import sys
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from ui import MainWindow


def _setup_logging():
    """Initialize file logging so crashes are captured."""
    log_path = os.path.join(os.path.dirname(__file__), "note_flow.log")
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    logging.info("=== NoteFlow session start ===")


def _exception_hook(exc_type, exc_value, exc_traceback):
    """Capture uncaught exceptions, log them, and show a dialog."""
    tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.error("Uncaught exception:\n%s", tb_str)
    try:
        QMessageBox.critical(
            None,
            "Unexpected Error",
            f"An unexpected error occurred. Details:\n\n{exc_value}\n\nSee note_flow.log for full trace.",
        )
    finally:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


def main():
    """Main application entry point"""
    _setup_logging()
    sys.excepthook = _exception_hook

    try:
        app = QApplication(sys.argv)

        # Set application metadata
        app.setApplicationName("NoteFlow")
        app.setOrganizationName("NoteFlow")

        # Create and show main window
        window = MainWindow()
        window.show()

        # Start event loop
        exit_code = app.exec_()
        logging.info("Qt event loop exited with code %s", exit_code)
        sys.exit(exit_code)

    except Exception:
        tb_str = traceback.format_exc()
        logging.error("Fatal error during startup:\n%s", tb_str)
        print(tb_str)
        QMessageBox.critical(None, "Startup Error", "NoteFlow could not start. Check note_flow.log.")
        sys.exit(1)


if __name__ == "__main__":
    main()
