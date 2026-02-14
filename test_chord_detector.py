"""
Unit Tests for Chord Detector Module
"""

import unittest
from chord_detector import ChordDetector


class TestChordDetector(unittest.TestCase):
    """Test cases for ChordDetector class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = ChordDetector()
    
    def _create_notes(self, note_names, start_time=0.0):
        """Helper to create note dictionaries for testing"""
        notes = []
        for i, name in enumerate(note_names):
            # Extract note and octave
            note_only = name.rstrip('0123456789-')
            octave = int(name[-1]) if name[-1].isdigit() else 4
            
            # Calculate MIDI number
            note_index = self.detector.NOTE_NAMES.index(note_only) if note_only in self.detector.NOTE_NAMES else 0
            midi_number = (octave + 2) * 12 + note_index
            
            notes.append({
                'note_name': name,
                'midi_number': midi_number,
                'timestamp': start_time + (i * 0.01),
                'relative_time': i * 0.01,
                'velocity': 80
            })
        return notes
    
    def test_major_chord_root_position(self):
        """Test detection of major chord in root position"""
        notes = self._create_notes(['C4', 'E4', 'G4'])
        result = self.detector.detect_chord(notes)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['root'], 'C')
        self.assertEqual(result['quality'], 'maj')
        self.assertEqual(result['display_name'], 'C maj')
        self.assertEqual(result['inversion'], 0)
    
    def test_minor_chord_root_position(self):
        """Test detection of minor chord in root position"""
        notes = self._create_notes(['D4', 'F4', 'A4'])
        result = self.detector.detect_chord(notes)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['root'], 'D')
        self.assertEqual(result['quality'], 'min')
        self.assertEqual(result['display_name'], 'D min')
    
    def test_diminished_chord(self):
        """Test detection of diminished chord"""
        notes = self._create_notes(['B3', 'D4', 'F4'])
        result = self.detector.detect_chord(notes)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['root'], 'B')
        self.assertEqual(result['quality'], 'dim')
    
    def test_augmented_chord(self):
        """Test detection of augmented chord"""
        notes = self._create_notes(['C4', 'E4', 'G#4'])
        result = self.detector.detect_chord(notes)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['root'], 'C')
        self.assertEqual(result['quality'], 'aug')
    
    def test_suspended_2nd(self):
        """Test detection of sus2 chord"""
        notes = self._create_notes(['G4', 'A4', 'D5'])
        result = self.detector.detect_chord(notes)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['root'], 'G')
        self.assertEqual(result['quality'], 'sus2')
    
    def test_suspended_4th(self):
        """Test detection of sus4 chord"""
        notes = self._create_notes(['C4', 'F4', 'G4'])
        result = self.detector.detect_chord(notes)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['root'], 'C')
        self.assertEqual(result['quality'], 'sus4')
    
    def test_dominant_7th(self):
        """Test detection of dominant 7th chord"""
        notes = self._create_notes(['G4', 'B4', 'D5', 'F5'])
        result = self.detector.detect_chord(notes)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['root'], 'G')
        self.assertEqual(result['quality'], '7')
        self.assertEqual(result['display_name'], 'G 7')
    
    def test_major_7th(self):
        """Test detection of major 7th chord"""
        notes = self._create_notes(['C4', 'E4', 'G4', 'B4'])
        result = self.detector.detect_chord(notes)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['root'], 'C')
        self.assertEqual(result['quality'], 'maj7')
    
    def test_minor_7th(self):
        """Test detection of minor 7th chord"""
        notes = self._create_notes(['D4', 'F4', 'A4', 'C5'])
        result = self.detector.detect_chord(notes)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['root'], 'D')
        self.assertEqual(result['quality'], 'min7')
    
    def test_diminished_7th(self):
        """Test detection of diminished 7th chord"""
        notes = self._create_notes(['B3', 'D4', 'F4', 'G#4'])
        result = self.detector.detect_chord(notes)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['root'], 'B')
        self.assertEqual(result['quality'], 'dim7')
    
    def test_half_diminished_7th(self):
        """Test detection of half-diminished 7th chord"""
        notes = self._create_notes(['B3', 'D4', 'F4', 'A4'])
        result = self.detector.detect_chord(notes)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['root'], 'B')
        self.assertEqual(result['quality'], 'ø7')
    
    def test_power_chord(self):
        """Test detection of power chord (root + 5th)"""
        notes = self._create_notes(['E3', 'B3'])
        result = self.detector.detect_chord(notes)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['root'], 'E')
        self.assertEqual(result['quality'], '5')
        self.assertEqual(result['display_name'], 'E5')
    
    def test_chord_inversion_first(self):
        """Test detection of chord in first inversion"""
        # E-G-C is C Major in first inversion
        notes = self._create_notes(['E4', 'G4', 'C5'])
        result = self.detector.detect_chord(notes)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['root'], 'C')
        self.assertEqual(result['quality'], 'maj')
        self.assertGreater(result['inversion'], 0)  # Should be in inversion
    
    def test_chord_inversion_second(self):
        """Test detection of chord in second inversion"""
        # G-C-E is C Major in second inversion
        notes = self._create_notes(['G3', 'C4', 'E4'])
        result = self.detector.detect_chord(notes)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['root'], 'C')
        self.assertEqual(result['quality'], 'maj')
        self.assertGreater(result['inversion'], 0)
    
    def test_chord_different_octaves(self):
        """Test that chords work across different octaves"""
        # C3-E3-G3 should be same as C4-E4-G4
        notes1 = self._create_notes(['C3', 'E3', 'G3'])
        notes2 = self._create_notes(['C5', 'E5', 'G5'])
        
        result1 = self.detector.detect_chord(notes1)
        result2 = self.detector.detect_chord(notes2)
        
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertEqual(result1['quality'], result2['quality'])
        self.assertEqual(result1['root'], result2['root'])
    
    def test_add9_chord(self):
        """Test detection of add9 chord"""
        notes = self._create_notes(['C4', 'E4', 'G4', 'D5'])
        result = self.detector.detect_chord(notes)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['root'], 'C')
        self.assertEqual(result['quality'], 'add9')
    
    def test_classify_single_note(self):
        """Test classification of single note"""
        notes = self._create_notes(['C4'])
        result = self.detector.classify_notes(notes)
        
        self.assertEqual(result['type'], 'note')
        self.assertEqual(result['display_name'], 'C4')
    
    def test_classify_chord(self):
        """Test classification of chord"""
        notes = self._create_notes(['C4', 'E4', 'G4'])
        result = self.detector.classify_notes(notes)
        
        self.assertEqual(result['type'], 'chord')
        self.assertEqual(result['root'], 'C')
        self.assertEqual(result['quality'], 'maj')
    
    def test_classify_unknown_interval(self):
        """Test classification of unrecognized interval"""
        notes = self._create_notes(['C4', 'D4'])
        result = self.detector.classify_notes(notes)
        
        # Should return as interval since it doesn't match known patterns
        self.assertIn(result['type'], ['interval', 'notes'])
    
    def test_note_to_semitone(self):
        """Test note to semitone conversion"""
        self.assertEqual(self.detector.note_to_semitone('C4'), 0)
        self.assertEqual(self.detector.note_to_semitone('C#4'), 1)
        self.assertEqual(self.detector.note_to_semitone('D4'), 2)
        self.assertEqual(self.detector.note_to_semitone('E4'), 4)
        self.assertEqual(self.detector.note_to_semitone('G4'), 7)
        self.assertEqual(self.detector.note_to_semitone('A4'), 9)
        self.assertEqual(self.detector.note_to_semitone('B4'), 11)
    
    def test_midi_to_semitone(self):
        """Test MIDI to semitone conversion"""
        self.assertEqual(self.detector.midi_to_semitone(60), 0)  # C4
        self.assertEqual(self.detector.midi_to_semitone(61), 1)  # C#4
        self.assertEqual(self.detector.midi_to_semitone(62), 2)  # D4
        self.assertEqual(self.detector.midi_to_semitone(72), 0)  # C5


if __name__ == '__main__':
    unittest.main()
