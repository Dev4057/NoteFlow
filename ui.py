"""
UI Module
PyQt5 GUI for NoteFlow application
"""

import sys
import os
import glob
import logging
from typing import Dict
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QComboBox, QTextEdit, QLabel, 
                              QMessageBox, QStatusBar, QFrame, QApplication,
                              QCheckBox, QDialog, QDialogButtonBox, QSpinBox,
                              QGroupBox)
from PyQt5.QtCore import QTimer, Qt, QDateTime
from PyQt5.QtGui import QPainter, QColor, QFont
from midi_handler import MIDIHandler
from note_recorder import NoteRecorder
from exporter import WordExporter
from music_sheet_exporter import MusicSheetExporter


class PianoKey:
    """Represents a single piano key"""
    def __init__(self, note_name: str, midi_number: int, is_black: bool, x: int, width: int):
        self.note_name = note_name
        self.midi_number = midi_number
        self.is_black = is_black
        self.x = x
        self.width = width
        self.is_pressed = False


class VisualKeyboard(QWidget):
    """Visual representation of a piano keyboard (61 keys, C1-C6)"""
    
    def __init__(self):
        super().__init__()
        self.keys = []
        self.pressed_keys = set()
        self.setup_keys()
        self.setMinimumHeight(120)
        
    def setup_keys(self):
        """Setup the 61 keys (C1 to C6)"""
        # 61 keys from C1 (MIDI 24) to C6 (MIDI 84)
        start_midi = 36  # C1
        end_midi = 96    # C6
        
        white_key_width = 20
        black_key_width = 12
        x_position = 0
        
        # Pattern of black keys in an octave (1 = has black key after, 0 = no black key)
        black_key_pattern = [1, 1, 0, 1, 1, 1, 0]  # C, D, E, F, G, A, B
        
        for midi_num in range(start_midi, end_midi + 1):
            note_index = midi_num % 12
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            octave = (midi_num // 12) - 2
            note_name = f"{note_names[note_index]}{octave}"
            
            # Check if this is a black key
            is_black = '#' in note_name
            
            if not is_black:
                # White key
                key = PianoKey(note_name, midi_num, False, x_position, white_key_width)
                self.keys.append(key)
                x_position += white_key_width
        
        # Now add black keys
        x_position = 0
        white_key_count = 0
        for midi_num in range(start_midi, end_midi + 1):
            note_index = midi_num % 12
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            octave = (midi_num // 12) - 2
            note_name = f"{note_names[note_index]}{octave}"
            
            is_black = '#' in note_name
            
            if is_black:
                # Black key positioned between white keys
                black_x = x_position - (black_key_width // 2)
                key = PianoKey(note_name, midi_num, True, black_x, black_key_width)
                self.keys.append(key)
            else:
                x_position += white_key_width
        
    def set_key_pressed(self, midi_number: int, pressed: bool):
        """Set a key as pressed or released"""
        if pressed:
            self.pressed_keys.add(midi_number)
        else:
            self.pressed_keys.discard(midi_number)
        self.update()
        
    def paintEvent(self, event):
        """Paint the keyboard"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        white_key_height = 100
        black_key_height = 60
        
        # Draw white keys first
        for key in self.keys:
            if not key.is_black:
                if key.midi_number in self.pressed_keys:
                    painter.setBrush(QColor(100, 150, 255))  # Blue when pressed
                else:
                    painter.setBrush(QColor(255, 255, 255))  # White
                
                painter.setPen(QColor(0, 0, 0))
                painter.drawRect(key.x, 0, key.width, white_key_height)
                
                # Add note label for C notes
                if 'C' in key.note_name and '#' not in key.note_name:
                    painter.setFont(QFont('Arial', 7))
                    painter.drawText(key.x + 2, white_key_height - 5, key.note_name)
        
        # Draw black keys on top
        for key in self.keys:
            if key.is_black:
                if key.midi_number in self.pressed_keys:
                    painter.setBrush(QColor(50, 100, 200))  # Darker blue when pressed
                else:
                    painter.setBrush(QColor(0, 0, 0))  # Black
                
                painter.setPen(QColor(0, 0, 0))
                painter.drawRect(key.x, 0, key.width, black_key_height)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.midi_handler = MIDIHandler()
        self.note_recorder = NoteRecorder()
        self.word_exporter = WordExporter()
        self.music_sheet_exporter = MusicSheetExporter()
        self.exports_dir = os.path.join(os.path.dirname(__file__), "exports")
        os.makedirs(self.exports_dir, exist_ok=True)
        
        self.setup_ui()
        self.setup_midi_callbacks()
        self.setup_timer()
        self.refresh_midi_devices()

    def _auto_filepath(self, extension: str) -> str:
        """Build an auto-generated file path in the exports folder."""
        timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_HHmmss")
        filename = f"recording_{timestamp}.{extension.lstrip('.')}"
        return os.path.join(self.exports_dir, filename)

    def _latest_file(self, extension: str):
        """Return the most recent file path with the given extension in exports."""
        pattern = os.path.join(self.exports_dir, f"*.{extension.lstrip('.')}")
        files = glob.glob(pattern)
        if not files:
            return None
        return max(files, key=os.path.getmtime)
        
    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("NoteFlow - MIDI Note Recorder")
        self.setGeometry(100, 100, 900, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # MIDI Connection Section
        connection_layout = QHBoxLayout()
        
        connection_label = QLabel("MIDI Device:")
        self.device_combo = QComboBox()
        self.device_combo.setMinimumWidth(200)
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.toggle_connection)
        
        refresh_button = QPushButton("Refresh Devices")
        refresh_button.clicked.connect(self.refresh_midi_devices)
        
        connection_layout.addWidget(connection_label)
        connection_layout.addWidget(self.device_combo)
        connection_layout.addWidget(self.connect_button)
        connection_layout.addWidget(refresh_button)
        connection_layout.addStretch()
        
        main_layout.addLayout(connection_layout)
        
        # Visual Keyboard
        keyboard_label = QLabel("Visual Keyboard (C1 - C6):")
        keyboard_label.setFont(QFont('Arial', 10, QFont.Bold))
        main_layout.addWidget(keyboard_label)
        
        self.visual_keyboard = VisualKeyboard()
        main_layout.addWidget(self.visual_keyboard)
        
        # Recording Controls
        recording_layout = QHBoxLayout()
        
        self.start_stop_button = QPushButton("Start Recording")
        self.start_stop_button.clicked.connect(self.toggle_recording)
        self.start_stop_button.setEnabled(False)
        
        self.clear_button = QPushButton("Clear Recording")
        self.clear_button.clicked.connect(self.clear_recording)
        
        self.chord_detection_checkbox = QCheckBox("Enable Chord Detection")
        self.chord_detection_checkbox.setChecked(True)
        self.chord_detection_checkbox.stateChanged.connect(self.toggle_chord_detection)
        
        recording_layout.addWidget(self.start_stop_button)
        recording_layout.addWidget(self.clear_button)
        recording_layout.addWidget(self.chord_detection_checkbox)
        recording_layout.addStretch()
        
        main_layout.addLayout(recording_layout)
        
        # Recorded Notes Display
        notes_label = QLabel("Recorded Notes:")
        notes_label.setFont(QFont('Arial', 10, QFont.Bold))
        main_layout.addWidget(notes_label)
        
        self.notes_text = QTextEdit()
        self.notes_text.setReadOnly(True)
        self.notes_text.setMinimumHeight(200)
        main_layout.addWidget(self.notes_text)
        
        # Export and Save/Load Controls
        file_layout = QHBoxLayout()
        
        self.export_button = QPushButton("Export to Word")
        self.export_button.clicked.connect(self.export_to_word)
        
        self.music_sheet_button = QPushButton("Export as Music Sheet")
        self.music_sheet_button.clicked.connect(self.export_music_sheet)
        
        self.save_button = QPushButton("Save Recording")
        self.save_button.clicked.connect(self.save_recording)
        
        self.load_button = QPushButton("Load Recording")
        self.load_button.clicked.connect(self.load_recording)
        
        file_layout.addWidget(self.export_button)
        file_layout.addWidget(self.music_sheet_button)
        file_layout.addWidget(self.save_button)
        file_layout.addWidget(self.load_button)
        file_layout.addStretch()
        
        main_layout.addLayout(file_layout)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Not connected to MIDI device")
        
    def setup_midi_callbacks(self):
        """Setup MIDI event callbacks"""
        self.midi_handler.set_note_on_callback(self.on_note_on)
        self.midi_handler.set_note_off_callback(self.on_note_off)
        
    def setup_timer(self):
        """Setup timer for polling MIDI messages"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_midi)
        self.timer.start(10)  # Poll every 10ms
        
    def refresh_midi_devices(self):
        """Refresh the list of available MIDI devices"""
        devices = self.midi_handler.get_available_devices()
        self.device_combo.clear()
        
        if devices:
            self.device_combo.addItems(devices)
        else:
            self.device_combo.addItem("No MIDI devices found")
            
    def toggle_connection(self):
        """Toggle MIDI device connection"""
        if self.midi_handler.is_connected():
            # Disconnect
            self.midi_handler.disconnect()
            self.connect_button.setText("Connect")
            self.start_stop_button.setEnabled(False)
            self.status_bar.showMessage("Disconnected from MIDI device")
        else:
            # Connect
            device_name = self.device_combo.currentText()
            if device_name and device_name != "No MIDI devices found":
                if self.midi_handler.connect(device_name):
                    self.connect_button.setText("Disconnect")
                    self.start_stop_button.setEnabled(True)
                    self.status_bar.showMessage(f"Connected to {device_name}")
                else:
                    QMessageBox.warning(self, "Connection Error", 
                                       f"Failed to connect to {device_name}")
                    self.status_bar.showMessage("Connection failed")
            else:
                QMessageBox.warning(self, "No Device", 
                                   "Please select a MIDI device")
                
    def toggle_recording(self):
        """Toggle recording state"""
        if self.note_recorder.is_recording:
            # Stop recording
            self.note_recorder.stop_recording()
            self.start_stop_button.setText("Start Recording")
            self.status_bar.showMessage("Recording stopped")
        else:
            # Start recording
            self.note_recorder.start_recording()
            self.start_stop_button.setText("Stop Recording")
            self.status_bar.showMessage("Recording...")
            
    def toggle_chord_detection(self, state):
        """Toggle chord detection on/off"""
        enabled = state == Qt.Checked
        self.note_recorder.set_chord_detection(enabled)
        status_msg = "Chord detection enabled" if enabled else "Chord detection disabled"
        self.status_bar.showMessage(status_msg, 3000)
    
    def clear_recording(self):
        """Clear the current recording"""
        reply = QMessageBox.question(self, "Clear Recording",
                                     "Are you sure you want to clear the recording?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.note_recorder.clear_recording()
            self.notes_text.clear()
            self.status_bar.showMessage("Recording cleared")
            
    def on_note_on(self, note_name: str, midi_number: int, velocity: int):
        """Handle note on event"""
        self.visual_keyboard.set_key_pressed(midi_number, True)
        self.note_recorder.add_note(note_name, midi_number, velocity)
        self.update_notes_display()
        
    def on_note_off(self, note_name: str, midi_number: int):
        """Handle note off event"""
        self.visual_keyboard.set_key_pressed(midi_number, False)
        
    def update_notes_display(self):
        """Update the notes display"""
        notes_text = self.note_recorder.get_notes_as_text()
        self.notes_text.setPlainText(notes_text)
        
        # Auto-scroll to bottom
        scrollbar = self.notes_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def poll_midi(self):
        """Poll for MIDI messages"""
        self.midi_handler.poll_messages()
        
    def export_music_sheet(self):
        """Export recording as music sheet with two-column layout"""
        try:
            logging.info("Music sheet export started")
            if self.note_recorder.get_note_count() == 0:
                QMessageBox.warning(self, "No Notes",
                                   "No notes to export. Please record some notes first.")
                return
            
            # Show export options dialog
            dialog = MusicSheetExportDialog(self)
            if dialog.exec_() != QDialog.Accepted:
                return
            
            options = dialog.get_options()
            
            # Generate filepath
            filepath = self._auto_filepath('.docx')
            filepath = filepath.replace('.docx', '_music_sheet.docx')
            logging.info("Music sheet export path chosen: %s", filepath)
            
            self.status_bar.showMessage("Exporting music sheet...")
            QApplication.processEvents()
            
            # Get events from recorder
            events = self.note_recorder.get_events()
            
            if self.music_sheet_exporter.export_to_music_sheet(events, filepath, options):
                self.status_bar.showMessage(f"Music sheet exported to {filepath}")
                logging.info("Music sheet export successful: %s", filepath)
                QMessageBox.information(self, "Export Successful",
                                       f"Music sheet exported to:\n{filepath}")
            else:
                QMessageBox.critical(self, "Export Failed",
                                    "Failed to export music sheet")
                self.status_bar.showMessage("Music sheet export failed")
                logging.error("Music sheet export failed for path: %s", filepath)
        except Exception as e:
            error_msg = str(e)
            logging.exception("Music sheet export error: %s", error_msg)
            QMessageBox.critical(self, "Export Error",
                                f"An error occurred during export:\n{error_msg}")
            self.status_bar.showMessage("Music sheet export error")
    
    def export_to_word(self):
        """Export recording to Word document"""
        try:
            logging.info("Export started")
            if self.note_recorder.get_note_count() == 0:
                QMessageBox.warning(self, "No Notes", 
                                   "No notes to export. Please record some notes first.")
                return
            
            filepath = self._auto_filepath('.docx')
            logging.info("Auto export path chosen: %s", filepath)
            
            self.status_bar.showMessage("Exporting...")
            QApplication.processEvents()
            
            notes = self.note_recorder.get_notes()
            duration = self.note_recorder.get_duration()
            
            if self.word_exporter.export_to_word(notes, filepath, duration):
                self.status_bar.showMessage(f"Exported to {filepath}")
                logging.info("Export successful: %s", filepath)
                QMessageBox.information(self, "Export Successful",
                                       f"Recording exported to:\n{filepath}")
            else:
                QMessageBox.critical(self, "Export Failed",
                                    "Failed to export recording to Word")
                self.status_bar.showMessage("Export failed")
                logging.error("Export failed for path: %s", filepath)
        except Exception as e:
            error_msg = str(e)
            logging.exception("Export error: %s", error_msg)
            QMessageBox.critical(self, "Export Error",
                                f"An error occurred during export:\n{error_msg}")
            self.status_bar.showMessage("Export error")
                
    def save_recording(self):
        """Save recording to JSON file"""
        try:
            logging.info("Save started")
            if self.note_recorder.get_note_count() == 0:
                QMessageBox.warning(self, "No Notes",
                                   "No notes to save. Please record some notes first.")
                return
            
            filepath = self._auto_filepath('.json')
            logging.info("Auto save path chosen: %s", filepath)
            
            self.status_bar.showMessage("Saving...")
            QApplication.processEvents()
            
            if self.note_recorder.save_to_file(filepath):
                self.status_bar.showMessage(f"Saved to {filepath}")
                logging.info("Save successful: %s", filepath)
                QMessageBox.information(self, "Save Successful",
                                       f"Recording saved to:\n{filepath}")
            else:
                QMessageBox.critical(self, "Save Failed",
                                    "Failed to save recording")
                self.status_bar.showMessage("Save failed")
                logging.error("Save failed for path: %s", filepath)
        except Exception as e:
            error_msg = str(e)
            logging.exception("Save error: %s", error_msg)
            QMessageBox.critical(self, "Save Error",
                                f"An error occurred while saving:\n{error_msg}")
            self.status_bar.showMessage("Save error")
                
    def load_recording(self):
        """Load recording from JSON file"""
        try:
            logging.info("Load started")
            filepath = self._latest_file('json')
            logging.info("Latest JSON file selected: %s", filepath)
            if not filepath:
                logging.info("No JSON files found to load")
                QMessageBox.information(self, "No Saved Recordings",
                                       "No saved recordings found in the exports folder.")
                return
            
            self.status_bar.showMessage("Loading...")
            QApplication.processEvents()
            
            if self.note_recorder.load_from_file(filepath):
                self.update_notes_display()
                self.status_bar.showMessage(f"Loaded from {filepath}")
                logging.info("Load successful: %s", filepath)
                QMessageBox.information(self, "Load Successful",
                                       f"Recording loaded from:\n{filepath}")
            else:
                QMessageBox.critical(self, "Load Failed",
                                    "Failed to load recording")
                self.status_bar.showMessage("Load failed")
                logging.error("Load failed for path: %s", filepath)
        except Exception as e:
            error_msg = str(e)
            logging.exception("Load error: %s", error_msg)
            QMessageBox.critical(self, "Load Error",
                                f"An error occurred while loading:\n{error_msg}")
            self.status_bar.showMessage("Load error")
                
    def closeEvent(self, event):
        """Handle window close event"""
        # Disconnect from MIDI device
        self.midi_handler.disconnect()
        event.accept()


class MusicSheetExportDialog(QDialog):
    """Dialog for configuring music sheet export options"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Music Sheet Export Options")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        
        # Title input
        title_group = QGroupBox("Recording Title")
        title_layout = QVBoxLayout()
        self.title_edit = QTextEdit()
        self.title_edit.setMaximumHeight(30)
        self.title_edit.setPlainText(f"Recording - {QDateTime.currentDateTime().toString('MMM dd, yyyy')}")
        title_layout.addWidget(self.title_edit)
        title_group.setLayout(title_layout)
        layout.addWidget(title_group)
        
        # Measures per line
        measures_group = QGroupBox("Layout Options")
        measures_layout = QVBoxLayout()
        
        measures_row = QHBoxLayout()
        measures_row.addWidget(QLabel("Measures per line:"))
        self.measures_spin = QSpinBox()
        self.measures_spin.setMinimum(2)
        self.measures_spin.setMaximum(16)
        self.measures_spin.setValue(4)
        measures_row.addWidget(self.measures_spin)
        measures_row.addStretch()
        measures_layout.addLayout(measures_row)
        
        measures_group.setLayout(measures_layout)
        layout.addWidget(measures_group)
        
        # Content options
        content_group = QGroupBox("Include in Export")
        content_layout = QVBoxLayout()
        
        self.include_chords_check = QCheckBox("Chord progressions (left column)")
        self.include_chords_check.setChecked(True)
        content_layout.addWidget(self.include_chords_check)
        
        self.include_melody_check = QCheckBox("Melody sequences (right column)")
        self.include_melody_check.setChecked(True)
        content_layout.addWidget(self.include_melody_check)
        
        self.detect_sections_check = QCheckBox("Detect sections (split by pauses)")
        self.detect_sections_check.setChecked(True)
        content_layout.addWidget(self.detect_sections_check)
        
        content_group.setLayout(content_layout)
        layout.addWidget(content_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def get_options(self) -> Dict:
        """Get the export options from the dialog"""
        return {
            'title': self.title_edit.toPlainText().strip(),
            'measures_per_line': self.measures_spin.value(),
            'include_chords': self.include_chords_check.isChecked(),
            'include_melody': self.include_melody_check.isChecked(),
            'detect_sections': self.detect_sections_check.isChecked(),
            'pause_threshold': 2.0
        }
