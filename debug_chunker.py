#!/usr/bin/env python3

import os
import logging
import subprocess
from audio_chunker import AudioChunker

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chunker_debug.log'),
        logging.StreamHandler()
    ]
)

def verify_ffmpeg_command(input_file: str, start: float, end: float, output_file: str):
    """Test an ffmpeg command and log its behavior."""
    try:
        command = [
            'ffmpeg',
            '-i', input_file,
            '-ss', str(start),
            '-to', str(end),
            '-c:a', 'pcm_s16le',
            '-ar', '44100',
            output_file,
            '-y'
        ]
        
        logging.debug(f"Executing ffmpeg command: {' '.join(command)}")
        
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        logging.debug(f"FFmpeg stdout: {stdout.decode()}")
        logging.debug(f"FFmpeg stderr: {stderr.decode()}")
        
        if os.path.exists(output_file):
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            duration = get_audio_duration(output_file)
            logging.debug(f"Output file size: {size_mb:.2f} MB")
            logging.debug(f"Output duration: {duration:.2f}s")
            logging.debug(f"MB per second: {size_mb/duration:.4f}")
            return True
    except Exception as e:
        logging.error(f"FFmpeg command failed: {str(e)}")
        return False

def get_audio_duration(file_path: str) -> float:
    """Get duration of audio file using ffprobe."""
    command = [
        'ffprobe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        file_path
    ]
    
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    stdout, stderr = process.communicate()
    return float(stdout.decode().strip())

def test_chunking(file_path: str):
    """Test the chunking process on a file."""
    logging.info(f"\n=== Testing chunking for {file_path} ===")
    
    # Get original file info
    orig_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    orig_duration = get_audio_duration(file_path)
    mb_per_second = orig_size_mb / orig_duration
    
    logging.info(f"Original file size: {orig_size_mb:.2f} MB")
    logging.info(f"Original duration: {orig_duration:.2f}s")
    logging.info(f"MB per second: {mb_per_second:.4f}")
    
    # Test with different chunk sizes
    chunker = AudioChunker(max_chunk_size_mb=15.0)
    chunk_paths, was_chunked = chunker.chunk_audio(file_path)
    
    if was_chunked:
        total_size = 0
        for path in chunk_paths:
            size = os.path.getsize(path) / (1024 * 1024)
            total_size += size
        
        logging.info(f"Total size of chunks: {total_size:.2f} MB")
        logging.info(f"Size difference: {(total_size - orig_size_mb):.2f} MB")

if __name__ == "__main__":
    # Test the chunker with the problematic file
    test_file = "/Users/stewartalsop/Dropbox/Crazy Wisdom/Business/Coding_Projects/2025/January/dropbox_monitor/Audio Test/Iván Vendrov.m4a"
    test_chunking(test_file)