# NoteFlow - MIDI Note Recorder

A desktop application for recording MIDI keyboard notes, designed specifically for music students and teachers. Record your practice sessions, visualize notes in real-time, and export your recordings to Word documents.

![NoteFlow](screenshots/noteflow-main.png)

## 🎵 Features

- **MIDI Device Connection**: Automatically detect and connect to MIDI keyboards
- **Visual Keyboard Display**: 61-key virtual keyboard (C1-C6) with real-time key highlighting
- **Note Recording**: Record note sequences with timestamps and velocity information
- **Real-time Display**: See notes appear instantly as you play them
- **Save & Load**: Save recordings to JSON format and reload them later
- **Word Export**: Export recordings to professionally formatted Word documents
- **User-Friendly Interface**: Clean, intuitive PyQt5 GUI

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
2. Click **Start Recording**
3. Play notes on your keyboard - they will appear in real-time
4. Watch the visual keyboard highlight keys as you press them
5. Click **Stop Recording** when finished

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
├── main.py              # Application entry point
├── midi_handler.py      # MIDI device connection and event handling
├── note_recorder.py     # Note recording and storage
├── ui.py                # PyQt5 GUI and visual keyboard
├── exporter.py          # Word document export functionality
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🔧 Technical Details

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

### Export Issues
- Ensure you have write permissions to the selected directory
- Check that the file isn't open in Word during export
- Verify that python-docx is properly installed

## 🔮 Future Features (V2)

- **Chord Detection**: Automatically identify and label chords
- **Rhythm Analysis**: Detect note durations and tempo
- **Multiple Tracks**: Record separate tracks for different hands
- **Audio Playback**: Play back recorded notes with MIDI synthesis
- **PDF Export**: Export to PDF format
- **Custom Key Ranges**: Support for different keyboard sizes

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
- Export recordings regularly to track your progress over time
- Save important recordings in JSON format for future reference

---

**Built with ❤️ for music students and teachers**
