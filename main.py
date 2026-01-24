"""
NoteFlow - MIDI Note Recorder
Main application entry point
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui import MainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("NoteFlow")
    app.setOrganizationName("NoteFlow")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
