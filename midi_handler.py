"""
MIDI Handler Module
Handles MIDI device connection and event processing
"""

import mido
from typing import List, Optional, Callable


def midi_to_note(midi_number: int) -> str:
    """
    Convert MIDI note number to note name with octave.
    
    Args:
        midi_number: MIDI note number (0-127)
        
    Returns:
        Note name with octave (e.g., "C4", "A#5")
    """
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_number // 12) - 1
    note = notes[midi_number % 12]
    return f"{note}{octave}"


class MIDIHandler:
    """Handles MIDI input device connection and event processing"""
    
    def __init__(self):
        self.input_port: Optional[mido.ports.BaseInput] = None
        self.note_on_callback: Optional[Callable] = None
        self.note_off_callback: Optional[Callable] = None
        self.connected_device: Optional[str] = None
        
    def get_available_devices(self) -> List[str]:
        """
        Get list of available MIDI input devices.
        
        Returns:
            List of device names
        """
        try:
            return mido.get_input_names()
        except Exception as e:
            print(f"Error getting MIDI devices: {e}")
            return []
    
    def connect(self, device_name: str) -> bool:
        """
        Connect to a MIDI input device.
        
        Args:
            device_name: Name of the MIDI device to connect to
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Close existing connection if any
            self.disconnect()
            
            # Open new connection
            self.input_port = mido.open_input(device_name)
            self.connected_device = device_name
            return True
        except Exception as e:
            print(f"Error connecting to MIDI device '{device_name}': {e}")
            self.input_port = None
            self.connected_device = None
            return False
    
    def disconnect(self):
        """Disconnect from current MIDI device"""
        if self.input_port:
            try:
                self.input_port.close()
            except Exception as e:
                print(f"Error disconnecting MIDI device: {e}")
            finally:
                self.input_port = None
                self.connected_device = None
    
    def set_note_on_callback(self, callback: Callable):
        """
        Set callback function for note_on events.
        
        Args:
            callback: Function to call with (note_name, velocity) when note is pressed
        """
        self.note_on_callback = callback
    
    def set_note_off_callback(self, callback: Callable):
        """
        Set callback function for note_off events.
        
        Args:
            callback: Function to call with (note_name) when note is released
        """
        self.note_off_callback = callback
    
    def poll_messages(self):
        """
        Poll for MIDI messages and trigger callbacks.
        Should be called regularly to process incoming MIDI events.
        """
        if not self.input_port:
            return
        
        try:
            # Process all pending messages
            for msg in self.input_port.iter_pending():
                if msg.type == 'note_on' and msg.velocity > 0:
                    # Note pressed
                    note_name = midi_to_note(msg.note)
                    if self.note_on_callback:
                        self.note_on_callback(note_name, msg.note, msg.velocity)
                        
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    # Note released
                    note_name = midi_to_note(msg.note)
                    if self.note_off_callback:
                        self.note_off_callback(note_name, msg.note)
                        
        except Exception as e:
            print(f"Error polling MIDI messages: {e}")
    
    def is_connected(self) -> bool:
        """Check if currently connected to a MIDI device"""
        return self.input_port is not None
    
    def get_connected_device(self) -> Optional[str]:
        """Get name of currently connected device"""
        return self.connected_device
