#!/usr/bin/env python3

import time
import os
import shutil
from input.monitor import AudioMonitor
from datetime import datetime
from tqdm import tqdm

from common.config import Config, init_environment
from common.utils import setup_logging
from input.file_handler import AudioFileHandler
from output.formatter import TranscriptFormatter
from processing.diarizer import SpeakerDiarizer
from processing.transcriber import CloudSpeechTranscriber

# Initialize environment and logging
init_environment()
setup_logging('transcript_processor.log')

class TranscriptionHandler(FileSystemEventHandler):
    def __init__(self):
        self.transcript_formatter = TranscriptFormatter()
        self.speaker_diarizer = SpeakerDiarizer()
        self.file_handler = AudioFileHandler()
        self.transcriber = CloudSpeechTranscriber()
        
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
            
            # Only process m4a files in the "Audio Record" folder
            if not ('Audio Record' in file_path and file_path.endswith('.m4a')):
                return
                
            if not self.file_handler.is_valid_file(file_path):
                return
                
            try:
                # Wait a moment to ensure file is fully written
                time.sleep(1)
                self.process_audio_file(file_path)
            finally:
                self.file_handler.cleanup_processing(file_path)
                
        except Exception as e:
            logging.error(f"Error handling event for {event.src_path}: {str(e)}")


    def transcribe_audio(self, wav_path):
        """Transcribe audio using the configured transcription service."""
        try:
            # Get file size for logging
            file_size = os.path.getsize(wav_path)
            logging.info(f"Processing audio file ({file_size / 1024 / 1024:.2f} MB)...")
            
            # Use the transcription service
            return self.transcriber.transcribe_audio(wav_path)
            
        except Exception as e:
            logging.error(f"Transcription error: {str(e)}")
            raise

    def process_audio_file(self, file_path):
        """Process a new audio file for transcription and analysis."""
        try:
            # Prepare file and get paths
            audio_copy_path, wav_file_to_process = self.file_handler.prepare_audio_file(file_path)
            transcript_folder, _, wav_path, transcript_path, analysis_path = self.file_handler.get_transcript_paths(file_path)
            
            # Get metadata
            filename = os.path.basename(file_path)
            meeting_folder = os.path.dirname(os.path.dirname(file_path))
            file_size = os.path.getsize(file_path)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Get transcription
            transcription = self.transcribe_audio(wav_path)
            
            # Process speaker diarization
            segments, speaker_mapping = self.speaker_diarizer.process_transcript(transcription)
            speaker_metadata = self.speaker_diarizer.format_metadata(speaker_mapping)
            
            # Format and save transcription
            metadata = {
                "Meeting": os.path.basename(meeting_folder),
                "File": filename,
                "Size": f"{file_size / 1024 / 1024:.2f} MB",
                "Processed": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "speaker_mapping": speaker_mapping,
                **speaker_metadata
            }
            formatted_transcript = self.transcript_formatter.format_transcript(
                transcription, metadata)
            
            with open(transcript_path, 'w') as f:
                f.write(formatted_transcript)
                
            # Generate and save title analysis
            analysis_text = self.title_analyzer.analyze_transcript(transcription)
            self.title_analyzer.save_analysis(analysis_text, analysis_path)
            
            # Clean up temporary files
            self.file_handler.cleanup_processing(file_path, wav_path)
            
            logging.info(f"\n{'='*50}")
            logging.info(f"Audio file processed!")
            logging.info(f"Meeting: {os.path.basename(meeting_folder)}")
            logging.info(f"File: {filename}")
            logging.info(f"Size: {file_size / 1024 / 1024:.2f} MB")
            logging.info(f"Time: {timestamp}")
            logging.info(f"Transcript saved to: {transcript_path}")
            logging.info(f"Analysis saved to: {analysis_path}")
            logging.info(f"{'='*50}\n")
                
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {str(e)}")

if __name__ == "__main__":
    # Your Dropbox folder path
    DROPBOX_PATH = "/Users/stewartalsop/Dropbox/Crazy Wisdom/Beautifully Broken/Zoom Folder"
    
    try:
        handler = TranscriptionHandler()
        monitor = AudioMonitor(DROPBOX_PATH, handler)
        monitor.start(recursive=True)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")