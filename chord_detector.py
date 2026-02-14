"""
Chord Detector Module
Intelligent chord recognition system for MIDI note sequences
"""

import logging
from typing import List, Dict, Optional, Tuple


class ChordDetector:
    """Detects and identifies chords from MIDI notes"""
    
    # Chord patterns defined as semitone intervals from root
    CHORD_PATTERNS = {
        # Triads
        'maj': [0, 4, 7],           # Major
        'min': [0, 3, 7],           # Minor
        'dim': [0, 3, 6],           # Diminished
        'aug': [0, 4, 8],           # Augmented
        'sus2': [0, 2, 7],          # Suspended 2nd
        'sus4': [0, 5, 7],          # Suspended 4th
        
        # Seventh chords
        '7': [0, 4, 7, 10],         # Dominant 7th
        'maj7': [0, 4, 7, 11],      # Major 7th
        'min7': [0, 3, 7, 10],      # Minor 7th
        'dim7': [0, 3, 6, 9],       # Diminished 7th
        'ø7': [0, 3, 6, 10],        # Half-diminished 7th
        'mMaj7': [0, 3, 7, 11],     # Minor-Major 7th
        
        # Extended chords
        '9': [0, 4, 7, 10, 14],     # 9th (dominant 9th)
        'maj9': [0, 4, 7, 11, 14],  # Major 9th
        'min9': [0, 3, 7, 10, 14],  # Minor 9th
        '11': [0, 4, 7, 10, 14, 17], # 11th
        '13': [0, 4, 7, 10, 14, 17, 21], # 13th
        'add9': [0, 4, 7, 14],      # Add 9
        'add11': [0, 4, 7, 17],     # Add 11
        
        # Power chord
        '5': [0, 7],                # Power chord (root + fifth)
    }
    
    # Full names for display
    CHORD_FULL_NAMES = {
        'maj': 'Major',
        'min': 'Minor',
        'dim': 'Diminished',
        'aug': 'Augmented',
        'sus2': 'Suspended 2nd',
        'sus4': 'Suspended 4th',
        '7': 'Dominant 7th',
        'maj7': 'Major 7th',
        'min7': 'Minor 7th',
        'dim7': 'Diminished 7th',
        'ø7': 'Half-Diminished 7th',
        'mMaj7': 'Minor-Major 7th',
        '9': '9th',
        'maj9': 'Major 9th',
        'min9': 'Minor 9th',
        '11': '11th',
        '13': '13th',
        'add9': 'Add 9',
        'add11': 'Add 11',
        '5': 'Power Chord',
    }
    
    NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    def __init__(self):
        """Initialize chord detector"""
        pass
    
    def note_to_semitone(self, note_name: str) -> int:
        """
        Convert note name to semitone value (0-11).
        
        Args:
            note_name: Note name with octave (e.g., "C4", "A#5")
            
        Returns:
            Semitone value (0-11, where C=0)
        """
        # Extract note without octave
        note_only = note_name.rstrip('0123456789-')
        
        if note_only in self.NOTE_NAMES:
            return self.NOTE_NAMES.index(note_only)
        
        # Handle flats (convert to sharps)
        flat_to_sharp = {
            'Db': 'C#', 'Eb': 'D#', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'
        }
        
        if note_only in flat_to_sharp:
            return self.NOTE_NAMES.index(flat_to_sharp[note_only])
        
        return 0  # Default to C if unknown
    
    def midi_to_semitone(self, midi_number: int) -> int:
        """
        Convert MIDI number to semitone value (0-11).
        
        Args:
            midi_number: MIDI note number (0-127)
            
        Returns:
            Semitone value (0-11)
        """
        return midi_number % 12
    
    def normalize_intervals(self, intervals: List[int]) -> List[int]:
        """
        Normalize intervals to be within one octave and sorted.
        
        Args:
            intervals: List of intervals in semitones
            
        Returns:
            Normalized intervals
        """
        # Reduce all intervals to within one octave
        normalized = sorted(set([i % 12 for i in intervals]))
        return normalized
    
    def detect_chord(self, notes: List[Dict]) -> Optional[Dict]:
        """
        Detect chord from a list of notes.
        
        Args:
            notes: List of note dictionaries with 'note_name' and 'midi_number'
            
        Returns:
            Chord information dictionary or None if not a chord
        """
        if len(notes) < 2:
            return None
        
        # Extract MIDI numbers and sort
        midi_numbers = sorted([note['midi_number'] for note in notes])
        
        # Get the bass note (lowest note)
        bass_midi = midi_numbers[0]
        bass_note = notes[0]['note_name']
        
        # Convert to semitone intervals relative to bass note
        intervals = [midi - bass_midi for midi in midi_numbers]
        normalized_intervals = self.normalize_intervals(intervals)
        
        # Try to match chord patterns
        chord_info = self._match_chord_pattern(normalized_intervals, bass_midi)
        
        if chord_info:
            # Add bass note information
            chord_info['bass_note'] = bass_note
            chord_info['notes'] = [note['note_name'] for note in notes]
            
            return chord_info
        
        return None
    
    def _match_chord_pattern(self, intervals: List[int], bass_midi: int) -> Optional[Dict]:
        """
        Match intervals to known chord patterns.
        
        Args:
            intervals: Normalized intervals
            bass_midi: MIDI number of bass note
            
        Returns:
            Chord information or None
        """
        # First pass: Check root positions only (rotation = 0)
        for quality, pattern in self.CHORD_PATTERNS.items():
            rotated_pattern = self._get_intervals_from_rotation(pattern, 0)
            
            if sorted(rotated_pattern) == sorted(intervals):
                root_note = self.NOTE_NAMES[bass_midi % 12]
                
                return {
                    'root': root_note,
                    'quality': quality,
                    'full_name': f"{root_note} {self.CHORD_FULL_NAMES[quality]}",
                    'display_name': f"{root_note}{quality}" if quality == '5' else f"{root_note} {quality}",
                    'pattern': pattern,
                    'root_offset': 0,
                    'inversion': 0,
                    'type': 'chord' if len(intervals) >= 3 else 'interval'
                }
        
        # Second pass: Check inversions (rotation > 0)
        for quality, pattern in self.CHORD_PATTERNS.items():
            for rotation in range(1, len(pattern)):
                rotated_pattern = self._get_intervals_from_rotation(pattern, rotation)
                
                if sorted(rotated_pattern) == sorted(intervals):
                    # Calculate root offset
                    bass_interval = pattern[rotation]
                    root_offset = (12 - bass_interval) % 12
                    
                    root_midi = (bass_midi + root_offset) % 12
                    root_note = self.NOTE_NAMES[root_midi]
                    
                    return {
                        'root': root_note,
                        'quality': quality,
                        'full_name': f"{root_note} {self.CHORD_FULL_NAMES[quality]}",
                        'display_name': f"{root_note}{quality}" if quality == '5' else f"{root_note} {quality}",
                        'pattern': pattern,
                        'root_offset': root_offset,
                        'inversion': rotation,
                        'type': 'chord' if len(intervals) >= 3 else 'interval'
                    }
        
        return None
    
    def _get_intervals_from_rotation(self, pattern: List[int], rotation: int) -> List[int]:
        """
        Get intervals when a chord is in a specific inversion.
        
        Args:
            pattern: Original chord pattern (e.g., [0, 4, 7] for major)
            rotation: Which note is in the bass (0 = root position)
            
        Returns:
            Intervals from the bass note
        """
        if rotation == 0:
            # Root position - return normalized pattern
            return self.normalize_intervals(pattern)
        
        # For inversions, we need to recalculate intervals
        # Example: C major [0, 4, 7] in 1st inversion (E in bass)
        # E is at position 1 (interval 4), so we subtract 4 from all:
        # [0-4, 4-4, 7-4] = [-4, 0, 3]
        # Then normalize: [0, 3, 8] (E, G, C)
        
        bass_interval = pattern[rotation]
        new_intervals = []
        
        for interval in pattern:
            new_interval = (interval - bass_interval) % 12
            new_intervals.append(new_interval)
        
        return sorted(set(new_intervals))
    
    def _rotate_pattern(self, pattern: List[int], rotation: int) -> List[int]:
        """
        Rotate a chord pattern for inversion checking.
        
        Args:
            pattern: Original chord pattern
            rotation: Number of positions to rotate
            
        Returns:
            Rotated pattern with intervals adjusted
        """
        if rotation >= len(pattern):
            rotation = rotation % len(pattern)
        
        # Rotate and adjust intervals
        rotated = pattern[rotation:] + pattern[:rotation]
        # Subtract the first interval from all to make it start at 0
        offset = rotated[0]
        adjusted = [interval - offset for interval in rotated]
        
        return adjusted
    
    def _calculate_inversion(self, intervals: List[int], pattern: List[int]) -> int:
        """
        Calculate which inversion the chord is in.
        
        Args:
            intervals: Actual intervals
            pattern: Original chord pattern
            
        Returns:
            Inversion number (0 = root, 1 = first, 2 = second, etc.)
        """
        normalized_intervals = self.normalize_intervals(intervals)
        
        for rotation in range(len(pattern)):
            rotated = self._rotate_pattern(pattern, rotation)
            if self.normalize_intervals(rotated) == normalized_intervals:
                return rotation
        
        return 0
    
    def classify_notes(self, notes: List[Dict]) -> Dict:
        """
        Classify a group of notes as chord, interval, or single note.
        
        Args:
            notes: List of note dictionaries
            
        Returns:
            Classification with detailed information
        """
        if len(notes) == 0:
            return {
                'type': 'empty',
                'display_name': '',
                'notes': []
            }
        
        if len(notes) == 1:
            return {
                'type': 'note',
                'display_name': notes[0]['note_name'],
                'full_name': notes[0]['note_name'],
                'notes': [notes[0]['note_name']],
                'root': notes[0]['note_name'].rstrip('0123456789-'),
            }
        
        # Try to detect as chord
        chord_info = self.detect_chord(notes)
        
        if chord_info:
            chord_info['timestamp'] = notes[0].get('timestamp', 0)
            chord_info['relative_time'] = notes[0].get('relative_time', 0)
            return chord_info
        
        # If no chord detected, return as interval or note group
        note_names = [note['note_name'] for note in notes]
        return {
            'type': 'interval' if len(notes) == 2 else 'notes',
            'display_name': ' + '.join(note_names),
            'full_name': ' and '.join(note_names),
            'notes': note_names,
            'timestamp': notes[0].get('timestamp', 0),
            'relative_time': notes[0].get('relative_time', 0),
        }
