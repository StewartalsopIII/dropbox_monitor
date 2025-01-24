#!/usr/bin/env python3

import os
import logging
import subprocess
import tempfile
import shutil
from typing import List, Optional, Tuple
from pathlib import Path

class AudioChunker:
    """Handles splitting large audio files into processable chunks using ffmpeg."""
    
    def __init__(self, max_chunk_size_mb: float = 15.0, min_silence_duration: float = 1.0):
        """
        Initialize the AudioChunker.
        
        Args:
            max_chunk_size_mb (float): Maximum size of each chunk in MB
            min_silence_duration (float): Minimum duration of silence for split points in seconds
        """
        self.max_chunk_size_mb = max_chunk_size_mb
        self.min_silence_duration = min_silence_duration
        self.temp_dir: Optional[str] = None
        
    def needs_chunking(self, file_path: str) -> bool:
        """
        Check if a file needs to be split into chunks.
        
        Args:
            file_path (str): Path to the audio file
            
        Returns:
            bool: True if file size exceeds max chunk size
        """
        try:
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            return file_size_mb > self.max_chunk_size_mb
        except OSError as e:
            logging.error(f"Error checking file size: {str(e)}")
            raise
            
    def _create_temp_dir(self) -> str:
        """Create a temporary directory for storing chunks."""
        if not self.temp_dir:
            self.temp_dir = tempfile.mkdtemp(prefix='audio_chunks_')
        return self.temp_dir
        
    def _cleanup_temp_dir(self):
        """Remove temporary directory and its contents."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
            
    def _detect_silence_points(self, file_path: str) -> List[float]:
        """
        Detect silence points in audio file using ffmpeg silencedetect filter.
        
        Args:
            file_path (str): Path to the audio file
            
        Returns:
            List[float]: List of timestamps (in seconds) where silence occurs
        """
        try:
            command = [
                'ffmpeg',
                '-i', file_path,
                '-af', f'silencedetect=noise=-30dB:d={self.min_silence_duration}',
                '-f', 'null',
                '-'
            ]
            
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            _, stderr = process.communicate()
            stderr_output = stderr.decode()
            
            # Parse silence points from ffmpeg output
            silence_points = []
            for line in stderr_output.split('\n'):
                if 'silence_end' in line:
                    try:
                        time_str = line.split('silence_end: ')[1].split(' ')[0]
                        silence_points.append(float(time_str))
                    except (IndexError, ValueError):
                        continue
                        
            return sorted(silence_points)
            
        except Exception as e:
            logging.error(f"Error detecting silence points: {str(e)}")
            raise
            
    def _split_at_points(self, input_path: str, split_points: List[float]) -> List[str]:
        """
        Split audio file at specified points using ffmpeg.
        
        Args:
            input_path (str): Path to input audio file
            split_points (List[float]): List of timestamps to split at
            
        Returns:
            List[str]: List of paths to generated chunk files
        """
        chunk_paths = []
        temp_dir = self._create_temp_dir()
        file_stem = Path(input_path).stem
        
        try:
            # Add start and end points
            duration = self._get_audio_duration(input_path)
            points = [0] + split_points + [duration]
            
            # Create chunks
            for i in range(len(points) - 1):
                start = points[i]
                end = points[i + 1]
                
                output_path = os.path.join(temp_dir, f"{file_stem}_chunk_{i:03d}.wav")
                
                command = [
                    'ffmpeg',
                    '-i', input_path,
                    '-ss', str(start),
                    '-to', str(end),
                    '-c:a', 'pcm_s16le',  # Use same format as main converter
                    '-ar', '44100',
                    output_path,
                    '-y'
                ]
                
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                stdout, stderr = process.communicate()
                
                if process.returncode != 0:
                    raise Exception(f"FFmpeg error: {stderr.decode()}")
                    
                chunk_paths.append(output_path)
                
            return chunk_paths
            
        except Exception as e:
            self._cleanup_temp_dir()
            logging.error(f"Error splitting audio: {str(e)}")
            raise
            
    def _get_audio_duration(self, file_path: str) -> float:
        """
        Get duration of audio file in seconds using ffprobe.
        
        Args:
            file_path (str): Path to audio file
            
        Returns:
            float: Duration in seconds
        """
        try:
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
            
            if process.returncode != 0:
                raise Exception(f"FFprobe error: {stderr.decode()}")
                
            return float(stdout.decode().strip())
            
        except Exception as e:
            logging.error(f"Error getting audio duration: {str(e)}")
            raise
            
    def chunk_audio(self, file_path: str) -> Tuple[List[str], bool]:
        """
        Split audio file into chunks at silence points.
        
        Args:
            file_path (str): Path to input audio file
            
        Returns:
            Tuple[List[str], bool]: List of chunk file paths and whether chunking occurred
        """
        try:
            if not self.needs_chunking(file_path):
                return [file_path], False
                
            # Find silence points
            silence_points = self._detect_silence_points(file_path)
            
            # If no silence points found, split at regular intervals
            if not silence_points:
                duration = self._get_audio_duration(file_path)
                chunk_duration = (self.max_chunk_size_mb * 60) / 2  # Rough estimate
                silence_points = list(range(
                    int(chunk_duration), 
                    int(duration), 
                    int(chunk_duration)
                ))
            
            # Split the file
            chunk_paths = self._split_at_points(file_path, silence_points)
            
            return chunk_paths, True
            
        except Exception as e:
            self._cleanup_temp_dir()
            logging.error(f"Error chunking audio file: {str(e)}")
            raise
            
    def __enter__(self):
        """Context manager entry."""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        try:
            self._cleanup_temp_dir()
        except Exception as e:
            logging.error(f"Error cleaning up temp directory: {str(e)}")
        finally:
            # Ensure temp_dir is always reset
            self.temp_dir = None