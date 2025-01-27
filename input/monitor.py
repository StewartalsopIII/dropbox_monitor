#!/usr/bin/env python3

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import os
import time
from abc import ABC, abstractmethod

class BaseAudioHandler(FileSystemEventHandler, ABC):
    """Base handler for audio file processing."""
    
    def __init__(self):
        self.processing_files = set()
        
    def on_created(self, event):
        if event.is_directory:
            return
        self._handle_event(event)

    def on_modified(self, event):
        if event.is_directory:
            return
        self._handle_event(event)

    def _handle_event(self, event):
        try:
            file_path = event.src_path
            
            # Skip temporary files
            if file_path.endswith('.tmp'):
                return
                
            # Skip if already processing
            if file_path in self.processing_files:
                return
                
            # Validate file type
            if not self._is_valid_file(file_path):
                return
                
            # Add to processing set
            self.processing_files.add(file_path)
            
            try:
                # Wait for file to be fully written
                time.sleep(1)
                self.process_audio_file(file_path)
            finally:
                # Always remove from processing set
                self.processing_files.remove(file_path)
                
        except Exception as e:
            logging.error(f"Error handling event for {event.src_path}: {str(e)}")

    @abstractmethod
    def _is_valid_file(self, file_path: str) -> bool:
        """Validate if file should be processed."""
        pass

    @abstractmethod
    def process_audio_file(self, file_path: str):
        """Process the audio file."""
        pass

class AudioMonitor:
    """Handles monitoring directory for audio files."""
    
    def __init__(self, path: str, handler: BaseAudioHandler):
        self.path = path
        self.handler = handler
        self.observer = None
        
    def start(self, recursive: bool = False):
        """Start monitoring the directory."""
        if not os.path.exists(self.path):
            raise ValueError(f"The path {self.path} does not exist!")

        logging.info(f"Starting monitoring of: {self.path}")
        logging.info("Waiting for new audio files...")
        
        self.observer = Observer()
        self.observer.schedule(self.handler, self.path, recursive=recursive)
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
            
    def stop(self):
        """Stop monitoring."""
        if self.observer:
            logging.info("\nStopping monitoring...")
            self.observer.stop()
            self.observer.join()
            logging.info("Monitoring stopped")