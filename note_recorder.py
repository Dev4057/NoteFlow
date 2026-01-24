"""
Note Recorder Module
Handles recording, storing, and managing MIDI notes
"""

import json
import time
from typing import List, Dict, Optional
from datetime import datetime


class NoteRecorder:
    """Records and manages MIDI note sequences"""
    
    def __init__(self):
        self.notes: List[Dict] = []
        self.is_recording: bool = False
        self.recording_start_time: Optional[float] = None
        
    def start_recording(self):
        """Start recording notes"""
        self.is_recording = True
        self.recording_start_time = time.time()
        
    def stop_recording(self):
        """Stop recording notes"""
        self.is_recording = False
        
    def clear_recording(self):
        """Clear all recorded notes"""
        self.notes.clear()
        self.recording_start_time = None
        
    def add_note(self, note_name: str, midi_number: int, velocity: int):
        """
        Add a note to the recording.
        
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
        
        self.notes.append(note_data)
        
    def get_notes(self) -> List[Dict]:
        """Get all recorded notes"""
        return self.notes.copy()
    
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
        
        Returns:
            Formatted string of notes
        """
        if not self.notes:
            return "No notes recorded"
        
        lines = []
        for i, note in enumerate(self.notes, 1):
            time_str = f"{note['relative_time']:.2f}s"
            velocity_str = f"vel:{note['velocity']}"
            lines.append(f"{i}. {note['note_name']} ({time_str}, {velocity_str})")
        
        return "\n".join(lines)
    
    def get_notes_sequence(self) -> str:
        """
        Get notes as a simple sequence (e.g., "C4 → D4 → E4").
        
        Returns:
            Note sequence string
        """
        if not self.notes:
            return ""
        return " → ".join([note['note_name'] for note in self.notes])
    
    def save_to_file(self, filepath: str) -> bool:
        """
        Save recording to JSON file.
        
        Args:
            filepath: Path to save file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = {
                'recording_date': datetime.now().isoformat(),
                'note_count': len(self.notes),
                'duration': self.get_duration(),
                'notes': self.notes
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving recording to {filepath}: {e}")
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """
        Load recording from JSON file.
        
        Args:
            filepath: Path to file to load
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.notes = data.get('notes', [])
            return True
        except Exception as e:
            print(f"Error loading recording from {filepath}: {e}")
            return False
