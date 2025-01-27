#!/usr/bin/env python3

import os
import logging
import shutil
import subprocess
from typing import Optional, Tuple
from pathlib import Path

class AudioFileHandler:
    """Handles audio file operations and validation."""
    
    SUPPORTED_FORMATS = ('.wav', '.mp3', '.m4a')
    
    def __init__(self):
        """Initialize the AudioFileHandler."""
        self.processing_files = set()
        
    def is_valid_file(self, file_path: str) -> bool:
        """
        Check if a file is valid for processing.
        
        Args:
            file_path (str): Path to the file to check
            
        Returns:
            bool: True if file is valid for processing
        """
        if not os.path.exists(file_path):
            return False
            
        if file_path.endswith('.tmp'):
            return False
            
        if not file_path.lower().endswith(self.SUPPORTED_FORMATS):
            return False
            
        if file_path in self.processing_files:
            return False
            
        return True
        
    def get_transcript_paths(self, file_path: str) -> Tuple[str, str, str, str]:
        """
        Generate paths for transcript and related files.
        
        Args:
            file_path (str): Original audio file path
            
        Returns:
            Tuple containing:
            - transcript_folder: Path to folder containing transcripts
            - audio_copy_path: Path where audio file will be copied
            - wav_path: Path for WAV version of audio
            - transcript_path: Path for transcript file
            - analysis_path: Path for analysis file
        """
        filename = os.path.basename(file_path)
        file_dir = os.path.dirname(file_path)
        
        # Create transcript folder path
        transcript_folder = os.path.join(file_dir, "transcripts")
        if not os.path.exists(transcript_folder):
            os.makedirs(transcript_folder)
        
        # Generate file paths
        audio_copy_path = os.path.join(transcript_folder, filename)
        base_name = os.path.splitext(filename)[0]
        wav_path = os.path.join(transcript_folder, f"{base_name}.wav")
        transcript_path = os.path.join(transcript_folder, f"{base_name}.md")
        analysis_path = os.path.join(transcript_folder, f"{base_name}_analysis.md")
        
        return transcript_folder, audio_copy_path, wav_path, transcript_path, analysis_path
        
    def prepare_audio_file(self, file_path: str) -> Tuple[str, str]:
        """
        Prepare audio file for processing by copying and converting if needed.
        
        Args:
            file_path (str): Path to original audio file
            
        Returns:
            Tuple containing:
            - audio_copy_path: Path to copied audio file
            - wav_file_to_process: Path to WAV file for processing
        """
        # Prevent concurrent processing
        if file_path in self.processing_files:
            raise ValueError(f"File {file_path} is already being processed")
        
        self.processing_files.add(file_path)
        
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File {file_path} does not exist")
                
            # Get paths
            _, audio_copy_path, wav_path, _, _ = self.get_transcript_paths(file_path)
            
            # Copy original file if needed
            if not os.path.exists(audio_copy_path):
                shutil.copy2(file_path, audio_copy_path)
            
            # Convert to WAV if needed
            if not file_path.lower().endswith('.wav'):
                self.convert_to_wav(file_path, wav_path)
                wav_file_to_process = wav_path
            else:
                wav_file_to_process = file_path
                
            return audio_copy_path, wav_file_to_process
            
        except Exception as e:
            self.processing_files.discard(file_path)
            raise
            
    def convert_to_wav(self, input_path: str, output_path: str) -> None:
        """
        Convert audio to WAV format using ffmpeg.
        
        Args:
            input_path (str): Path to input audio file
            output_path (str): Path for output WAV file
        """
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
                
        except Exception as e:
            logging.error(f"Error converting to WAV: {str(e)}")
            raise
            
    def cleanup_processing(self, file_path: str, wav_path: Optional[str] = None) -> None:
        """
        Clean up after processing is complete.
        
        Args:
            file_path (str): Original file path
            wav_path (str, optional): Path to WAV file to clean up
        """
        self.processing_files.discard(file_path)
        
        if wav_path and os.path.exists(wav_path) and file_path != wav_path:
            try:
                os.remove(wav_path)
            except Exception as e:
                logging.error(f"Error cleaning up WAV file: {str(e)}")
