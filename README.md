# NoteFlow - MIDI Note Recorder

A desktop application for recording MIDI keyboard notes, designed specifically for music students and teachers. Record your practice sessions, visualize notes in real-time, detect chords automatically, and export your recordings to professionally formatted Word documents.

![NoteFlow](screenshots/noteflow-main.png)

## 🎵 Features

### Core Features
- **MIDI Device Connection**: Automatically detect and connect to MIDI keyboards
- **Visual Keyboard Display**: 61-key virtual keyboard (C1-C6) with real-time key highlighting
- **Note Recording**: Record note sequences with timestamps and velocity information
- **Real-time Display**: See notes appear instantly as you play them
- **Save & Load**: Save recordings to JSON format and reload them later
- **Word Export**: Export recordings to professionally formatted Word documents
- **User-Friendly Interface**: Clean, intuitive PyQt5 GUI

### 🎹 NEW: Intelligent Chord Recognition
- **Automatic Chord Detection**: Detects when 3+ notes are pressed simultaneously (within 50ms)
- **Comprehensive Chord Support**:
  - Triads: Major, Minor, Diminished, Augmented, Sus2, Sus4
  - Seventh Chords: Dominant 7th, Major 7th, Minor 7th, Dim7, Half-Dim7, Minor-Major 7th
  - Extended Chords: 9th, 11th, 13th, Add9, Add11
  - Power Chords: Root + Fifth
- **Inversion Detection**: Correctly identifies chord inversions (1st, 2nd, 3rd)
- **Cross-Octave Recognition**: Works across all octaves
- **Smart Display**: Shows "C maj" instead of "C E G" for recognized chords
- **Toggle On/Off**: Enable or disable chord detection with a checkbox

### 📄 NEW: Professional Music Sheet Export
- **Two-Column Layout**: 
  - Left Column: Chord progression tables with measure numbers
  - Right Column: Melody note sequences
- **Intelligent Section Detection**: Automatically splits recording into sections based on pauses
- **Customizable Export**:
  - Set recording title
  - Choose measures per line (2, 4, 8, 16)
  - Include/exclude chords or melody
  - Enable/disable section detection
- **Publication-Ready Output**: Professional Word document formatting

## 📋 Prerequisites

- **Python 3.8+** (tested with Python 3.12)
- **MIDI Keyboard** (optional - can test without hardware)
- **Operating System**: Windows, macOS, or Linux

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Dev4057/NoteFlow.git
   cd NoteFlow
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## 📖 Usage

### Connecting Your MIDI Keyboard

1. Connect your MIDI keyboard to your computer via USB
2. Launch NoteFlow
3. Select your MIDI device from the dropdown menu
4. Click **Connect**
5. The visual keyboard will activate

### Recording Notes

1. Ensure your MIDI keyboard is connected
2. **Enable/Disable Chord Detection**: Check or uncheck the "Enable Chord Detection" checkbox
3. Click **Start Recording**
4. Play notes on your keyboard - they will appear in real-time
5. Watch the visual keyboard highlight keys as you press them
6. **With Chord Detection**: When you play multiple notes simultaneously, they will be recognized as chords
7. Click **Stop Recording** when finished

### Using Chord Detection

The chord detection feature automatically identifies chords when you play 3 or more notes within 50ms:

**Supported Chord Types:**
- **Triads**: C maj, D min, B dim, C aug, G sus2, D sus4
- **Seventh Chords**: G7, Cmaj7, Dmin7, Bdim7, Bø7, CmMaj7
- **Extended**: C9, Cmaj9, Cmin9, C11, C13, Cadd9, Cadd11
- **Power Chords**: E5, A5 (root + fifth)

**Display Format:**
- Single notes: "C4", "E4", "G4"
- Chords: "[Chord: C maj]", "[Chord: G7]"
- Intervals: "[Interval: C4 + E4]"
- Inversions shown: "[Chord: C maj] (1st inversion)"

**Example Recording:**
```
1. [Chord: C maj] (0.00s)
2. [Chord: F maj] (1.23s)
3. [Chord: G7] (2.45s)
4. [Chord: C maj] (3.67s)
```

### Exporting to Music Sheet

1. After recording notes, click **Export as Music Sheet**
2. Configure export options:
   - **Recording Title**: Give your piece a name
   - **Measures per line**: Choose 2, 4, 8, or 16 measures
   - **Include chord progressions**: Left column with chord tables
   - **Include melody sequences**: Right column with note sequences
   - **Detect sections**: Automatically split by pauses (2+ seconds)
3. Click **OK** to export
4. The document will include:
   - Professional two-column layout
   - Chord progression tables (left)
   - Melody sequences (right)
   - Section numbering
   - Measure numbers

**Example Music Sheet Output:**
```
┌─────────────────────────┬─────────────────────────┐
│ CHORD PROGRESSIONS      │ MELODY SEQUENCES        │
├─────────────────────────┼─────────────────────────┤
│ Section 1:              │ Sequence 1:             │
│ ┌───┬───┬───┬───┐      │ [C maj] → [F maj] →     │
│ │ 1 │ 2 │ 3 │ 4 │      │ [G7] → [C maj]          │
│ ├───┼───┼───┼───┤      │                         │
│ │Cmaj│Fmaj│G7│Cmaj│    │ Sequence 2:             │
│ └───┴───┴───┴───┘      │ C4 → D4 → E4 → F4 → G4  │
└─────────────────────────┴─────────────────────────┘
```

### Exporting to Word

1. After recording notes, click **Export to Word**
2. Choose a location to save your .docx file
3. The document will include:
   - Recording date and time
   - Total duration
   - Note sequence (C4 → D4 → E4...)
   - Detailed table with timestamps and velocities

### Saving and Loading Recordings

- **Save**: Click **Save Recording** to save as JSON file
- **Load**: Click **Load Recording** to load a previous recording
- **Clear**: Click **Clear Recording** to start fresh

## 🎹 Visual Keyboard

The application displays a 61-key keyboard spanning 5 octaves (C1 to C6):
- White keys show note names at the bottom
- Keys highlight in **blue** when pressed
- Black keys appear in their natural positions
- Octave labels help with orientation

## 🏗️ Project Structure

```
NoteFlow/
├── main.py                    # Application entry point
├── midi_handler.py            # MIDI device connection and event handling
├── note_recorder.py           # Note recording with chord detection
├── chord_detector.py          # Intelligent chord recognition engine
├── ui.py                      # PyQt5 GUI and visual keyboard
├── exporter.py                # Standard Word document export
├── music_sheet_exporter.py    # Two-column music sheet export
├── test_chord_detector.py     # Unit tests for chord detection
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔧 Technical Details

### Chord Detection Algorithm

The chord detection system uses a sophisticated pattern matching algorithm:

1. **Time Windowing**: Notes pressed within 50ms are grouped together
2. **Interval Analysis**: Converts notes to semitone intervals (0-11)
3. **Pattern Matching**: Compares against 19 chord type patterns
4. **Inversion Detection**: Identifies root position and all inversions
5. **Priority System**: Prefers root position over inversions when ambiguous

**Example:**
- Input: C4, E4, G4 (MIDI 60, 64, 67)
- Intervals: [0, 4, 7] semitones
- Match: Major triad pattern [0, 4, 7]
- Output: "C maj" (root position)

**Inversions:**
- E4, G4, C5 → Intervals [0, 3, 8] → "C maj" (1st inversion)
- G3, C4, E4 → Intervals [0, 5, 9] → "C maj" (2nd inversion)

### Music Sheet Export Format

The exporter creates a professional two-column layout:
- **Left Column**: Chord progression tables with measure markers
- **Right Column**: Melody sequences showing note progressions
- **Section Detection**: Pauses > 2 seconds trigger new sections
- **Flexible Layout**: 2-16 measures per line
- **Word Format**: Uses python-docx for .docx generation

### MIDI Note Conversion
Notes are converted from MIDI numbers (0-127) to standard notation:
- MIDI 60 = C4 (Middle C)
- MIDI 24 = C1 (Lowest note displayed)
- MIDI 84 = C6 (Highest note displayed)

### Dependencies
- **mido**: MIDI I/O library
- **python-rtmidi**: Real-time MIDI backend
- **python-docx**: Word document generation
- **PyQt5**: GUI framework

## 🛠️ Troubleshooting

### No MIDI Devices Found
- Ensure your MIDI keyboard is properly connected
- Try unplugging and reconnecting the USB cable
- Click **Refresh Devices** after connecting
- Check that your keyboard is powered on

### Connection Failed
- Make sure the device isn't being used by another application
- Try selecting a different MIDI port if multiple are available
- Restart the application

### Chord Not Detected
- Ensure "Enable Chord Detection" checkbox is checked
- Play notes more simultaneously (within 50ms)
- Some note combinations may not match known chord patterns
- Try playing in root position first

### Export Issues
- Ensure you have write permissions to the selected directory
- Check that the file isn't open in Word during export
- Verify that python-docx is properly installed

### Music Sheet Export Shows Empty Sections
- Make sure you recorded with chord detection enabled
- Check that you have both notes and chords in your recording
- Try unchecking "Detect sections" to see all content in one section

## 🔮 Future Features

- ✅ **Chord Detection** (Implemented!)
- ✅ **Professional Music Sheet Export** (Implemented!)
- **Rhythm Analysis**: Detect note durations and tempo
- **Multiple Tracks**: Record separate tracks for different hands
- **Audio Playback**: Play back recorded notes with MIDI synthesis
- **PDF Export**: Export to PDF format
- **Custom Key Ranges**: Support for different keyboard sizes
- **Arpeggiation Detection**: Detect arpeggiated chords

## 📝 Testing Without Hardware

You can test the application without a physical MIDI keyboard:
1. Install a virtual MIDI device (e.g., loopMIDI on Windows)
2. Use MIDI sequencer software to send notes
3. Or explore the interface - most features work without MIDI input

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎓 Educational Use

NoteFlow is designed for music education:
- **Students**: Track your practice progress
- **Teachers**: Monitor student performances
- **Schools**: Document music class activities
- **Personal Use**: Keep a record of your musical ideas

## 💡 Tips

- Start with simple scales to get familiar with the interface
- Use the visual keyboard to verify correct note detection
- **Try chord progressions**: Play I-IV-V-I progressions to see chord detection in action
- **Experiment with inversions**: Play the same chord in different inversions
- Export recordings regularly to track your progress over time
- Save important recordings in JSON format for future reference
- Use the music sheet export for a professional presentation of your work
- **Practice sight-reading**: Export your playing as a music sheet and practice reading it back

---

**Built with ❤️ for music students and teachers**
