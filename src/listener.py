"""Keystroke listener for typing rhythm tracking.

This module tracks keystroke timing metadata without logging actual text content.
"""

import csv
import time
from datetime import datetime
from pathlib import Path
from queue import Queue
from threading import Thread, Event
from typing import Optional

from pynput import keyboard

from .config import (
    DATA_RAW_DIR,
    BATCH_SIZE,
    FLUSH_INTERVAL_SECONDS,
    CSV_HEADER,
)


class TypingRhythmListener:
    """Lightweight keystroke timing tracker."""
    
    def __init__(self):
        self.event_queue = Queue()
        self.buffer = []
        self.last_key_time: Optional[float] = None
        self.listener: Optional[keyboard.Listener] = None
        self.flush_thread: Optional[Thread] = None
        self.stop_event = Event()
        self.current_date = datetime.now().date()
        self.current_file: Optional[Path] = None
        
    def _get_key_name(self, key) -> str:
        """Convert pynput key to string representation."""
        try:
            # Special keys
            if key == keyboard.Key.space:
                return "space"
            elif key == keyboard.Key.enter:
                return "enter"
            elif key == keyboard.Key.backspace:
                return "backspace"
            elif key == keyboard.Key.tab:
                return "tab"
            elif key == keyboard.Key.shift:
                return "shift"
            elif key == keyboard.Key.ctrl:
                return "ctrl"
            elif key == keyboard.Key.cmd:
                return "cmd"
            elif key == keyboard.Key.alt:
                return "alt"
            elif key == keyboard.Key.esc:
                return "esc"
            elif key == keyboard.Key.delete:
                return "delete"
            elif hasattr(key, 'char') and key.char:
                # Regular character
                return key.char.lower()
            else:
                # Unknown key
                return f"key_{key}"
        except AttributeError:
            return f"key_{key}"
    
    def _on_press(self, key):
        """Handle key press event."""
        try:
            current_time = time.time()
            timestamp = datetime.now().isoformat()
            
            # Calculate time since previous key
            time_since_previous_ms = 0.0
            if self.last_key_time is not None:
                time_since_previous_ms = (current_time - self.last_key_time) * 1000.0
            
            # Get key name
            key_name = self._get_key_name(key)
            is_backspace = 1 if key == keyboard.Key.backspace else 0
            
            # Add to buffer
            event = {
                "timestamp": timestamp,
                "key": key_name,
                "time_since_previous_ms": round(time_since_previous_ms, 2),
                "is_backspace": is_backspace,
            }
            
            self.buffer.append(event)
            self.last_key_time = current_time
            
            # Check if we need to flush
            if len(self.buffer) >= BATCH_SIZE:
                self._flush_buffer()
                
        except Exception as e:
            # Silently handle errors to avoid disrupting typing
            pass
    
    def _get_csv_file(self) -> Path:
        """Get CSV file path for current date."""
        today = datetime.now().date()
        
        # If date changed, update file
        if today != self.current_date:
            self.current_date = today
            self.current_file = None
        
        if self.current_file is None:
            filename = f"keystrokes_{today.isoformat()}.csv"
            self.current_file = DATA_RAW_DIR / filename
            
            # Create file with header if it doesn't exist
            if not self.current_file.exists():
                with open(self.current_file, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
                    writer.writeheader()
        
        return self.current_file
    
    def _flush_buffer(self):
        """Flush buffer to CSV file."""
        if not self.buffer:
            return
        
        try:
            csv_file = self._get_csv_file()
            
            # Append to CSV
            with open(csv_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
                writer.writerows(self.buffer)
            
            # Clear buffer
            self.buffer.clear()
            
        except Exception as e:
            # Silently handle errors
            pass
    
    def _periodic_flush(self):
        """Periodically flush buffer in background thread."""
        while not self.stop_event.is_set():
            self.stop_event.wait(FLUSH_INTERVAL_SECONDS)
            if not self.stop_event.is_set():
                self._flush_buffer()
    
    def start(self):
        """Start listening for keystrokes."""
        print("Starting typing rhythm tracker...")
        print("Press Ctrl+C to stop.")
        
        # Start keyboard listener
        self.listener = keyboard.Listener(on_press=self._on_press)
        self.listener.start()
        
        # Start periodic flush thread
        self.flush_thread = Thread(target=self._periodic_flush, daemon=True)
        self.flush_thread.start()
        
        try:
            # Keep main thread alive
            self.listener.join()
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop listening and flush remaining data."""
        print("\nStopping typing rhythm tracker...")
        
        # Signal stop
        self.stop_event.set()
        
        # Stop listener
        if self.listener:
            self.listener.stop()
        
        # Flush remaining buffer
        self._flush_buffer()
        
        print("Tracker stopped. Data saved.")


def main():
    """Main entry point."""
    listener = TypingRhythmListener()
    listener.start()


if __name__ == "__main__":
    main()

