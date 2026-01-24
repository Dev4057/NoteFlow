"""
UI Module
PyQt5 GUI for NoteFlow application
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QPushButton, QComboBox, QTextEdit, QLabel, 
                              QFileDialog, QMessageBox, QStatusBar, QFrame)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter, QColor, QFont
from midi_handler import MIDIHandler
from note_recorder import NoteRecorder
from exporter import WordExporter


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
        start_midi = 24  # C1
        end_midi = 84    # C6
        
        white_key_width = 20
        black_key_width = 12
        x_position = 0
        
        # Pattern of black keys in an octave (1 = has black key after, 0 = no black key)
        black_key_pattern = [1, 1, 0, 1, 1, 1, 0]  # C, D, E, F, G, A, B
        
        for midi_num in range(start_midi, end_midi + 1):
            note_index = midi_num % 12
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            octave = (midi_num // 12) - 1
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
            octave = (midi_num // 12) - 1
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
        
        self.setup_ui()
        self.setup_midi_callbacks()
        self.setup_timer()
        self.refresh_midi_devices()
        
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
        
        recording_layout.addWidget(self.start_stop_button)
        recording_layout.addWidget(self.clear_button)
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
        
        self.save_button = QPushButton("Save Recording")
        self.save_button.clicked.connect(self.save_recording)
        
        self.load_button = QPushButton("Load Recording")
        self.load_button.clicked.connect(self.load_recording)
        
        file_layout.addWidget(self.export_button)
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
        
    def export_to_word(self):
        """Export recording to Word document"""
        if self.note_recorder.get_note_count() == 0:
            QMessageBox.warning(self, "No Notes", 
                               "No notes to export. Please record some notes first.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export to Word", "", "Word Documents (*.docx)")
        
        if filepath:
            if not filepath.endswith('.docx'):
                filepath += '.docx'
            
            notes = self.note_recorder.get_notes()
            duration = self.note_recorder.get_duration()
            
            if self.word_exporter.export_to_word(notes, filepath, duration):
                QMessageBox.information(self, "Export Successful",
                                       f"Recording exported to {filepath}")
                self.status_bar.showMessage(f"Exported to {filepath}")
            else:
                QMessageBox.critical(self, "Export Failed",
                                    "Failed to export recording to Word")
                
    def save_recording(self):
        """Save recording to JSON file"""
        if self.note_recorder.get_note_count() == 0:
            QMessageBox.warning(self, "No Notes",
                               "No notes to save. Please record some notes first.")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Recording", "", "JSON Files (*.json)")
        
        if filepath:
            if not filepath.endswith('.json'):
                filepath += '.json'
            
            if self.note_recorder.save_to_file(filepath):
                QMessageBox.information(self, "Save Successful",
                                       f"Recording saved to {filepath}")
                self.status_bar.showMessage(f"Saved to {filepath}")
            else:
                QMessageBox.critical(self, "Save Failed",
                                    "Failed to save recording")
                
    def load_recording(self):
        """Load recording from JSON file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Load Recording", "", "JSON Files (*.json)")
        
        if filepath:
            if self.note_recorder.load_from_file(filepath):
                self.update_notes_display()
                QMessageBox.information(self, "Load Successful",
                                       f"Recording loaded from {filepath}")
                self.status_bar.showMessage(f"Loaded from {filepath}")
            else:
                QMessageBox.critical(self, "Load Failed",
                                    "Failed to load recording")
                
    def closeEvent(self, event):
        """Handle window close event"""
        # Disconnect from MIDI device
        self.midi_handler.disconnect()
        event.accept()
