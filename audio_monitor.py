#!/usr/bin/env python3

import time
import os
import logging
import shutil
from watchdog.events import FileSystemEventHandler
from input.monitor import AudioMonitor
from datetime import datetime
import google.generativeai as genai
from tqdm import tqdm

from common.config import Config, init_environment
from common.utils import setup_logging
from input.file_handler import AudioFileHandler
from title_analyzer import TitleAnalyzer
from audio_chunker import AudioChunker
from transcript_formatter import TranscriptFormatter
from speaker_diarizer import SpeakerDiarizer

# Initialize environment and logging
init_environment()
setup_logging('audio_processor.log')

# Initialize Google AI
genai.configure(api_key=Config.get_google_api_key())

class AudioTranscriptionHandler(FileSystemEventHandler):
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.title_analyzer = TitleAnalyzer(self.model)
        self.transcript_formatter = TranscriptFormatter()
        self.speaker_diarizer = SpeakerDiarizer()
        self.file_handler = AudioFileHandler()
        
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
            
            # Check if file is valid for processing
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
        """
        Transcribe audio using Google Gemini Pro.
        Automatically handles file chunking for large files.
        """
        try:
            # Initialize chunker with 15MB max chunk size
            with AudioChunker(max_chunk_size_mb=15.0) as chunker:
                chunk_paths, was_chunked = chunker.chunk_audio(wav_path)
                
                if was_chunked:
                    logging.info(f"File split into {len(chunk_paths)} chunks for processing")
                    transcriptions = []
                    speaker_context = None
                    
                    # Process each chunk
                    for i, chunk_path in enumerate(chunk_paths):
                        logging.info(f"Processing chunk {i+1}/{len(chunk_paths)}...")
                        chunk_size = os.path.getsize(chunk_path) / (1024 * 1024)
                        logging.info(f"Chunk size: {chunk_size:.2f} MB")
                        
                        # Upload and transcribe the chunk
                        audio_file = genai.upload_file(chunk_path)
                        
                        # Add speaker context if available
                        prompt = ["Please transcribe this audio. Maintain existing speaker labels and formatting."]
                        if speaker_context and i > 0:
                            prompt.append(f"Previous speakers were: {', '.join(speaker_context)}")
                        
                        parts = [audio_file] + prompt
                        response = self.model.generate_content(parts)
                        transcription = response.text
                        
                        # Update speaker context from this chunk
                        segments, mapping = self.speaker_diarizer.process_transcript(transcription)
                        if mapping:
                            speaker_context = list(mapping.values())
                        
                        transcriptions.append(transcription)
                    
                    # Combine transcriptions with double newlines between chunks
                    return "\n\n".join(transcriptions)
                
                else:
                    # Process single file as before
                    file_size = os.path.getsize(wav_path)
                    logging.info(f"Uploading audio file ({file_size / 1024 / 1024:.2f} MB)...")
                    
                    audio_file = genai.upload_file(wav_path)
                    logging.info("Upload complete. Starting transcription...")
                    
                    parts = [
                        audio_file,
                        "Please transcribe this audio. Provide ONLY the transcription, nothing else."
                    ]
                    
                    response = self.model.generate_content(parts)
                    return response.text
            
        except Exception as e:
            logging.error(f"Transcription error: {str(e)}")
            raise

    def process_audio_file(self, file_path):
        """Process a new audio file for transcription and analysis."""
        try:
            if not os.path.exists(file_path):
                return
                
            # Prepare the audio file and get paths
            audio_copy_path, wav_file_to_process = self.file_handler.prepare_audio_file(file_path)
            transcript_folder, _, wav_path, transcript_path, analysis_path = self.file_handler.get_transcript_paths(file_path)
            
            # Get metadata
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Get transcription
            transcription = self.transcribe_audio(wav_file_to_process)
            
            # Process speaker diarization
            segments, speaker_mapping = self.speaker_diarizer.process_transcript(transcription)
            speaker_metadata = self.speaker_diarizer.format_metadata(speaker_mapping)
            
            # Format and save transcription
            metadata = {
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
            logging.info(f"File: {filename}")
            logging.info(f"Size: {file_size / 1024 / 1024:.2f} MB")
            logging.info(f"Time: {timestamp}")
            logging.info(f"Transcript saved to: {transcript_path}")
            logging.info(f"Analysis saved to: {analysis_path}")
            logging.info(f"{'='*50}\n")
                
        except Exception as e:
            logging.error(f"Error processing file {file_path}: {str(e)}")

if __name__ == "__main__":
    # Your audio folder path
    AUDIO_PATH = "/Users/stewartalsop/Dropbox/Crazy Wisdom/Business/Coding_Projects/2025/January/dropbox_monitor/Audio Test"
    
    try:
        handler = AudioTranscriptionHandler()
        monitor = AudioMonitor(AUDIO_PATH, handler)
        monitor.start()
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
