"""
Note Recorder Module
Handles recording, storing, and managing MIDI notes with chord detection
"""

import json
import logging
import os
import time
from typing import List, Dict, Optional
from datetime import datetime
from chord_detector import ChordDetector


class NoteRecorder:
    """Records and manages MIDI note sequences with chord detection"""
    
    def __init__(self):
        self.notes: List[Dict] = []
        self.is_recording: bool = False
        self.recording_start_time: Optional[float] = None
        self.chord_detector = ChordDetector()
        self.chord_detection_enabled: bool = True
        self.chord_time_window: float = 0.05  # 50ms window for chord detection
        self.pending_notes: List[Dict] = []  # Notes waiting for chord analysis
        self.last_note_time: Optional[float] = None
        self.recorded_events: List[Dict] = []  # Chords and individual notes
        
    def start_recording(self):
        """Start recording notes"""
        self.is_recording = True
        self.recording_start_time = time.time()
        self.pending_notes.clear()
        self.last_note_time = None
        
    def stop_recording(self):
        """Stop recording notes"""
        # Process any pending notes before stopping
        if self.pending_notes:
            self._process_pending_notes(force=True)
        self.is_recording = False
        
    def clear_recording(self):
        """Clear all recorded notes"""
        self.notes.clear()
        self.recorded_events.clear()
        self.pending_notes.clear()
        self.recording_start_time = None
        self.last_note_time = None
        
    def set_chord_detection(self, enabled: bool):
        """Enable or disable chord detection"""
        self.chord_detection_enabled = enabled
        
    def add_note(self, note_name: str, midi_number: int, velocity: int):
        """
        Add a note to the recording with chord detection.
        
        Args:
            note_name: Note name with octave (e.g., "C4")
            midi_number: MIDI note number
            velocity: Note velocity (0-127)
        """
        if not self.is_recording:
            return
            
        timestamp = time.time()
        relative_time = timestamp - self.recording_start_time if self.recording_start_time else 0
        
        note_data = {
            'note_name': note_name,
            'midi_number': midi_number,
            'velocity': velocity,
            'timestamp': timestamp,
            'relative_time': relative_time
        }
        
        # Always add to raw notes list for backward compatibility
        self.notes.append(note_data)
        
        # Handle chord detection
        if self.chord_detection_enabled:
            # Check if this note is within the time window of pending notes
            if self.last_note_time is not None:
                time_diff = timestamp - self.last_note_time
                
                if time_diff > self.chord_time_window:
                    # Time window expired - process pending notes as a chord or individual notes
                    self._process_pending_notes()
            
            # Add to pending notes
            self.pending_notes.append(note_data)
            self.last_note_time = timestamp
        else:
            # No chord detection - add as individual note
            event = {
                'type': 'note',
                'display_name': note_name,
                'notes': [note_name],
                'timestamp': timestamp,
                'relative_time': relative_time
            }
            self.recorded_events.append(event)
    
    def _process_pending_notes(self, force: bool = False):
        """
        Process pending notes to detect chords or individual notes.
        
        Args:
            force: If True, process even if not enough time has passed
        """
        if not self.pending_notes:
            return
        
        # If only one note, it's definitely a single note
        if len(self.pending_notes) == 1:
            note = self.pending_notes[0]
            event = {
                'type': 'note',
                'display_name': note['note_name'],
                'notes': [note['note_name']],
                'timestamp': note['timestamp'],
                'relative_time': note['relative_time']
            }
            self.recorded_events.append(event)
        else:
            # Multiple notes - try to detect as chord
            classification = self.chord_detector.classify_notes(self.pending_notes)
            self.recorded_events.append(classification)
        
        # Clear pending notes
        self.pending_notes.clear()
        
    def get_notes(self) -> List[Dict]:
        """Get all recorded notes (raw notes list)"""
        return self.notes.copy()
    
    def get_events(self) -> List[Dict]:
        """Get all recorded events (chords and notes)"""
        return self.recorded_events.copy()
    
    def get_note_count(self) -> int:
        """Get number of recorded notes"""
        return len(self.notes)
    
    def get_duration(self) -> float:
        """
        Get total recording duration in seconds.
        
        Returns:
            Duration in seconds, or 0 if no notes recorded
        """
        if not self.notes:
            return 0.0
        return self.notes[-1]['relative_time']
    
    def get_notes_as_text(self) -> str:
        """
        Get recorded notes as formatted text.
        Uses chord detection if enabled.
        
        Returns:
            Formatted string of notes/chords
        """
        if not self.notes:
            return "No notes recorded"
        
        if self.chord_detection_enabled and self.recorded_events:
            # Display with chord detection
            lines = []
            for i, event in enumerate(self.recorded_events, 1):
                time_str = f"{event.get('relative_time', 0):.2f}s"
                event_type = event.get('type', 'note')
                display_name = event.get('display_name', '')
                
                if event_type == 'chord':
                    # Show chord with inversion info if present
                    full_name = event.get('full_name', display_name)
                    inversion = event.get('inversion', 0)
                    inv_str = f" ({self._get_inversion_name(inversion)})" if inversion > 0 else ""
                    lines.append(f"{i}. [Chord: {display_name}]{inv_str} ({time_str})")
                elif event_type == 'interval':
                    lines.append(f"{i}. [Interval: {display_name}] ({time_str})")
                else:
                    lines.append(f"{i}. {display_name} ({time_str})")
            
            return "\n".join(lines)
        else:
            # Original format without chord detection
            lines = []
            for i, note in enumerate(self.notes, 1):
                time_str = f"{note['relative_time']:.2f}s"
                velocity_str = f"vel:{note['velocity']}"
                lines.append(f"{i}. {note['note_name']} ({time_str}, {velocity_str})")
            
            return "\n".join(lines)
    
    def _get_inversion_name(self, inversion: int) -> str:
        """Get human-readable inversion name"""
        if inversion == 0:
            return "root position"
        elif inversion == 1:
            return "1st inversion"
        elif inversion == 2:
            return "2nd inversion"
        elif inversion == 3:
            return "3rd inversion"
        else:
            return f"{inversion}th inversion"
    
    def get_notes_sequence(self) -> str:
        """
        Get notes as a simple sequence.
        Uses chord display if chord detection is enabled.
        
        Returns:
            Note sequence string
        """
        if not self.notes:
            return ""
        
        if self.chord_detection_enabled and self.recorded_events:
            # Use chord-aware display
            sequence = []
            for event in self.recorded_events:
                display_name = event.get('display_name', '')
                event_type = event.get('type', 'note')
                
                if event_type == 'chord':
                    sequence.append(f"[{display_name}]")
                else:
                    sequence.append(display_name)
            
            return " → ".join(sequence)
        else:
            # Original simple sequence
            return " → ".join([note['note_name'] for note in self.notes])
    
    def detect_sections(self, pause_threshold: float = 2.0) -> List[List[Dict]]:
        """
        Detect sections in the recording based on pauses.
        
        Args:
            pause_threshold: Minimum pause duration (in seconds) to split sections
            
        Returns:
            List of sections, where each section is a list of events
        """
        if not self.recorded_events:
            return []
        
        sections = []
        current_section = []
        last_time = None
        
        for event in self.recorded_events:
            event_time = event.get('relative_time', 0)
            
            if last_time is not None:
                pause_duration = event_time - last_time
                
                if pause_duration > pause_threshold:
                    # Start new section
                    if current_section:
                        sections.append(current_section)
                    current_section = []
            
            current_section.append(event)
            last_time = event_time
        
        # Add the last section
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def save_to_file(self, filepath: str) -> bool:
        """
        Save recording to JSON file.
        
        Args:
            filepath: Path to save file
            
        Returns:
            True if successful, False otherwise
        """
        logging.info("save_to_file called for %s", filepath)
        try:
            # Ensure the directory exists
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                logging.info("Creating directory %s", directory)
                os.makedirs(directory)
            
            data = {
                'recording_date': datetime.now().isoformat(),
                'note_count': len(self.notes),
                'duration': self.get_duration(),
                'notes': self.notes,
                'events': self.recorded_events,
                'chord_detection_enabled': self.chord_detection_enabled
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            logging.info("Saved JSON to %s", filepath)
            
            return True
        except PermissionError:
            logging.exception("Permission denied writing %s", filepath)
            return False
        except Exception:
            logging.exception("Error saving recording to %s", filepath)
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """
        Load recording from JSON file.
        
        Args:
            filepath: Path to file to load
            
        Returns:
            True if successful, False otherwise
        """
        logging.info("load_from_file called for %s", filepath)
        try:
            if not os.path.exists(filepath):
                logging.error("File not found: %s", filepath)
                return False
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.notes = data.get('notes', [])
            self.recorded_events = data.get('events', [])
            self.chord_detection_enabled = data.get('chord_detection_enabled', True)
            logging.info("Loaded %d notes from %s", len(self.notes), filepath)
            return True
        except FileNotFoundError:
            logging.exception("File not found (race) %s", filepath)
            return False
        except PermissionError:
            logging.exception("Permission denied reading %s", filepath)
            return False
        except json.JSONDecodeError:
            logging.exception("Invalid JSON file %s", filepath)
            return False
        except Exception:
            logging.exception("Error loading recording from %s", filepath)
            return False
