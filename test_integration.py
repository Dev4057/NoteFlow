"""
Integration Tests for Chord Detection and Music Sheet Export
"""

import unittest
import os
import tempfile
from chord_detector import ChordDetector
from note_recorder import NoteRecorder
from music_sheet_exporter import MusicSheetExporter


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.recorder = NoteRecorder()
        self.detector = ChordDetector()
        self.exporter = MusicSheetExporter()
        self.temp_dir = tempfile.mkdtemp()
    
    def test_chord_detection_in_recorder(self):
        """Test that chord detection works when integrated with recorder"""
        # Start recording
        self.recorder.start_recording()
        
        # Add notes for C major chord (simultaneously)
        import time
        base_time = time.time()
        
        # Simulate C-E-G played together (within 50ms)
        with unittest.mock.patch('time.time', return_value=base_time):
            self.recorder.add_note('C4', 60, 80)
        
        with unittest.mock.patch('time.time', return_value=base_time + 0.01):
            self.recorder.add_note('E4', 64, 80)
        
        with unittest.mock.patch('time.time', return_value=base_time + 0.02):
            self.recorder.add_note('G4', 67, 80)
        
        # Wait for time window to expire and add another note
        with unittest.mock.patch('time.time', return_value=base_time + 0.1):
            self.recorder.add_note('A4', 69, 80)
        
        # Stop recording
        self.recorder.stop_recording()
        
        # Get events
        events = self.recorder.get_events()
        
        # Should have detected the chord and the single note
        self.assertEqual(len(events), 2)
        
        # First event should be a chord
        self.assertEqual(events[0]['type'], 'chord')
        self.assertEqual(events[0]['root'], 'C')
        self.assertEqual(events[0]['quality'], 'maj')
        
        # Second event should be a single note
        self.assertEqual(events[1]['type'], 'note')
        self.assertEqual(events[1]['display_name'], 'A4')
    
    def test_section_detection(self):
        """Test that section detection works correctly"""
        # Start recording
        self.recorder.start_recording()
        
        import time
        base_time = time.time()
        
        # Add first chord
        with unittest.mock.patch('time.time', return_value=base_time):
            self.recorder.add_note('C4', 60, 80)
            self.recorder.add_note('E4', 64, 80)
            self.recorder.add_note('G4', 67, 80)
        
        # Wait 50ms to process chord
        with unittest.mock.patch('time.time', return_value=base_time + 0.1):
            pass
        
        # Add second chord after a long pause (3 seconds)
        with unittest.mock.patch('time.time', return_value=base_time + 3.0):
            self.recorder.add_note('F4', 65, 80)
            self.recorder.add_note('A4', 69, 80)
            self.recorder.add_note('C5', 72, 80)
        
        self.recorder.stop_recording()
        
        # Detect sections
        sections = self.recorder.detect_sections(pause_threshold=2.0)
        
        # Should have 2 sections due to the long pause
        self.assertEqual(len(sections), 2)
        self.assertEqual(len(sections[0]), 1)  # First section has 1 chord
        self.assertEqual(len(sections[1]), 1)  # Second section has 1 chord
    
    def test_music_sheet_export_basic(self):
        """Test basic music sheet export functionality"""
        # Create some events manually
        events = [
            {
                'type': 'chord',
                'display_name': 'C maj',
                'full_name': 'C Major',
                'notes': ['C4', 'E4', 'G4'],
                'root': 'C',
                'quality': 'maj',
                'relative_time': 0.0
            },
            {
                'type': 'chord',
                'display_name': 'F maj',
                'full_name': 'F Major',
                'notes': ['F4', 'A4', 'C5'],
                'root': 'F',
                'quality': 'maj',
                'relative_time': 1.0
            },
            {
                'type': 'note',
                'display_name': 'G4',
                'notes': ['G4'],
                'relative_time': 2.0
            }
        ]
        
        # Export to temp file
        filepath = os.path.join(self.temp_dir, 'test_sheet.docx')
        
        options = {
            'title': 'Test Recording',
            'measures_per_line': 4,
            'include_chords': True,
            'include_melody': True,
            'detect_sections': False
        }
        
        result = self.exporter.export_to_music_sheet(events, filepath, options)
        
        # Check that export succeeded
        self.assertTrue(result)
        
        # Check that file was created
        self.assertTrue(os.path.exists(filepath))
        
        # Check file size is reasonable (not empty)
        file_size = os.path.getsize(filepath)
        self.assertGreater(file_size, 1000)  # Should be at least 1KB
    
    def test_recorder_display_with_chords(self):
        """Test that recorder displays chords correctly"""
        self.recorder.start_recording()
        
        import time
        base_time = time.time()
        
        # Add a chord
        with unittest.mock.patch('time.time', return_value=base_time):
            self.recorder.add_note('C4', 60, 80)
            self.recorder.add_note('E4', 64, 80)
            self.recorder.add_note('G4', 67, 80)
        
        # Force processing
        with unittest.mock.patch('time.time', return_value=base_time + 0.1):
            pass
        
        self.recorder.stop_recording()
        
        # Get display text
        display_text = self.recorder.get_notes_as_text()
        
        # Should contain chord information
        self.assertIn('Chord', display_text)
        self.assertIn('C maj', display_text)
        
        # Get sequence
        sequence = self.recorder.get_notes_sequence()
        self.assertIn('[C maj]', sequence)
    
    def test_chord_detection_disabled(self):
        """Test that chord detection can be disabled"""
        # Disable chord detection
        self.recorder.set_chord_detection(False)
        self.recorder.start_recording()
        
        import time
        base_time = time.time()
        
        # Add notes that would form a chord
        with unittest.mock.patch('time.time', return_value=base_time):
            self.recorder.add_note('C4', 60, 80)
            self.recorder.add_note('E4', 64, 80)
            self.recorder.add_note('G4', 67, 80)
        
        self.recorder.stop_recording()
        
        # Should have 3 individual notes, not a chord
        events = self.recorder.get_events()
        self.assertEqual(len(events), 3)
        for event in events:
            self.assertEqual(event['type'], 'note')


if __name__ == '__main__':
    unittest.main()
