#!/usr/bin/env python3

import os
import logging
import subprocess
from typing import Optional

def setup_logging(log_file: str = 'audio_processor.log'):
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def convert_to_wav(input_path: str, output_path: str) -> bool:
    """
    Convert audio to WAV format using ffmpeg.
    
    Args:
        input_path (str): Path to input audio file
        output_path (str): Path for output WAV file
        
    Returns:
        bool: True if conversion successful
        
    Raises:
        Exception: If ffmpeg conversion fails
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
            
        return True
        
    except Exception as e:
        logging.error(f"Error converting to WAV: {str(e)}")
        raise

def ensure_dir_exists(directory: str) -> None:
    """Ensure a directory exists, create if it doesn't."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes."""
    return os.path.getsize(file_path) / (1024 * 1024)