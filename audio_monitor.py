#!/usr/bin/env python3

import time
import os
import logging
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import google.generativeai as genai
import subprocess
from dotenv import load_dotenv
from title_analyzer import TitleAnalyzer
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('audio_processor.log'),
        logging.StreamHandler()
    ]
)

# Initialize Google AI
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

class AudioTranscriptionHandler(FileSystemEventHandler):
    def __init__(self):
        self.processing_files = set()
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.title_analyzer = TitleAnalyzer(self.model)
        
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
                
            # Check if file is supported audio format
            supported_formats = ('.wav', '.mp3', '.m4a')
            if not file_path.lower().endswith(supported_formats):
                return
                
            # Skip if we're already processing this file
            if file_path in self.processing_files:
                return
                
            # Add to processing set
            self.processing_files.add(file_path)
            
            try:
                # Wait a moment to ensure file is fully written
                time.sleep(1)
                self.process_audio_file(file_path)
            finally:
                # Always remove from processing set
                self.processing_files.remove(file_path)
                
        except Exception as e:
            logging.error(f"Error handling event for {event.src_path}: {str(e)}")

    def convert_to_wav(self, input_path, output_path):
        """Convert audio to WAV format using ffmpeg."""
        try:
            command = [
                'ffmpeg',
                '-i', input_path,
                '-acodec', 'pcm_s16le',
                '-ar', '44100',
                output_path,
                '-y'  # Overwrite output file if it exists
            ]
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"FFmpeg error: {stderr.decode()}")
                
            return True
            
        except Exception as e:
            logging.error(f"Error converting to WAV: {str(e)}")
            raise

    def transcribe_audio(self, wav_path):
        """Transcribe audio using Google Gemini Pro."""
        try:
            # Get file size
            file_size = os.path.getsize(wav_path)
            logging.info(f"Uploading audio file ({file_size / 1024 / 1024:.2f} MB)...")
            
            # Upload the file using the File API
            audio_file = genai.upload_file(wav_path)
            logging.info("Upload complete. Starting transcription...")
            
            # Create content parts using the file reference
            parts = [
                audio_file,
                "Please transcribe this audio. Provide ONLY the transcription, nothing else."
            ]
            
            # Generate transcription
            response = self.model.generate_content(parts)
            return response.text
            
        except Exception as e:
            if "Request payload size exceeds the limit" in str(e):
                logging.error(f"File is too large to process. Maximum size is 20MB.")
                logging.error(f"Consider splitting the audio file into smaller segments.")
            else:
                logging.error(f"Transcription error: {str(e)}")
            raise

    def process_audio_file(self, file_path):
        """Process a new audio file for transcription and analysis."""
        try:
            # Check if file still exists
            if not os.path.exists(file_path):
                return
                
            filename = os.path.basename(file_path)
            file_dir = os.path.dirname(file_path)
            file_size = os.path.getsize(file_path)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Create transcript folder
            transcript_folder = os.path.join(file_dir, "transcripts")
            if not os.path.exists(transcript_folder):
                os.makedirs(transcript_folder)
            
            # Define file paths
            audio_copy_path = os.path.join(transcript_folder, filename)
            wav_path = os.path.join(transcript_folder, f"{os.path.splitext(filename)[0]}.wav")
            transcript_path = os.path.join(transcript_folder, f"{os.path.splitext(filename)[0]}.txt")
            analysis_path = os.path.join(transcript_folder, f"{os.path.splitext(filename)[0]}_analysis.md")
            
            # Copy original audio file
            if not os.path.exists(audio_copy_path):
                shutil.copy2(file_path, audio_copy_path)
            
            # Convert to WAV if needed
            if not file_path.lower().endswith('.wav'):
                self.convert_to_wav(file_path, wav_path)
                wav_file_to_process = wav_path
            else:
                wav_file_to_process = file_path
            
            # Get transcription
            transcription = self.transcribe_audio(wav_file_to_process)
            
            # Save transcription
            with open(transcript_path, 'w') as f:
                f.write(transcription)
                
            # Generate and save title analysis
            analysis_text = self.title_analyzer.analyze_transcript(transcription)
            self.title_analyzer.save_analysis(analysis_text, analysis_path)
            
            # Clean up WAV file if we created it
            if os.path.exists(wav_path) and file_path != wav_path:
                os.remove(wav_path)
            
            logging.info(f"\n{'='*50}")
            logging.info(f"Audio file processed!")
            logging.info(f"File: {filename}")
            logging.info(f"Size: {file_size / 1024 / 1024:.2f} MB")
            logging.info(f"Time: {timestamp}")
            logging.info(f"Transcript saved to: {transcript_path}")
            logging.info(f"Analysis saved to: {analysis_path}")
            logging.info(f"{'='*50}\n")
                
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {str(e)}")

def monitor_folder(path):
    """Monitor a folder for new audio files."""
    if not os.path.exists(path):
        raise ValueError(f"The path {path} does not exist!")

    logging.info(f"Starting monitoring of: {path}")
    logging.info("Waiting for new audio files...")
    
    event_handler = AudioTranscriptionHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("\nStopping monitoring...")
        observer.stop()
        observer.join()
        logging.info("Monitoring stopped")

if __name__ == "__main__":
    # Your audio folder path
    AUDIO_PATH = "/Users/stewartalsop/Dropbox/Crazy Wisdom/Audio Files"
    
    try:
        monitor_folder(AUDIO_PATH)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
