#!/usr/bin/env python3

import os
import logging
import subprocess
import tempfile
import shutil
import math
from typing import List, Optional, Tuple
from pathlib import Path

class AudioChunker:
    """Handles splitting large audio files into processable chunks using ffmpeg."""
    
    def __init__(self, max_chunk_size_mb: float = 15.0, min_chunk_size_mb: float = 10.0, min_silence_duration: float = 1.0):
        """
        Initialize the AudioChunker.
        
        Args:
            max_chunk_size_mb (float): Maximum size of each chunk in MB
            min_chunk_size_mb (float): Minimum size of each chunk in MB
            min_silence_duration (float): Minimum duration of silence for split points in seconds
        """
        self.max_chunk_size_mb = max_chunk_size_mb
        self.min_chunk_size_mb = min_chunk_size_mb
        self.min_silence_duration = min_silence_duration
        self.temp_dir: Optional[str] = None
        self.bytes_per_second: Optional[float] = None
        
    def _estimate_chunk_size(self, duration: float, input_file: str) -> float:
        """
        Estimate chunk size based on input file's bitrate.
        
        Args:
            duration (float): Duration of chunk in seconds
            input_file (str): Path to input file for bitrate calculation
            
        Returns:
            float: Estimated size in MB
        """
        if not self.bytes_per_second:
            total_size = os.path.getsize(input_file)
            total_duration = self._get_audio_duration(input_file)
            self.bytes_per_second = total_size / total_duration
            
        return (duration * self.bytes_per_second) / (1024 * 1024)  # Convert to MB
        
    def _get_optimal_chunk_duration(self, input_file: str) -> float:
        """
        Calculate optimal chunk duration based on file's bitrate.
        
        Args:
            input_file (str): Path to input file
            
        Returns:
            float: Optimal chunk duration in seconds
        """
        # Initialize bytes_per_second if not already set
        if not self.bytes_per_second:
            total_size = os.path.getsize(input_file)
            total_duration = self._get_audio_duration(input_file)
            self.bytes_per_second = total_size / total_duration
        
        # Target 80% of max chunk size to leave room for variation
        target_size = self.max_chunk_size_mb * 0.8 * 1024 * 1024  # Convert to bytes
        return target_size / self.bytes_per_second
        
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
        logging.debug(f"\n=== Starting file split at {len(split_points)} points ===")
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
                
                # Keep original extension for chunks
                ext = os.path.splitext(input_path)[1]
                output_path = os.path.join(temp_dir, f"{file_stem}_chunk_{i:03d}{ext}")
                
                command = [
                    'ffmpeg',
                    '-i', input_path,
                    '-ss', str(start),
                    '-to', str(end),
                    '-c', 'copy',  # Preserve original codec
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
            logging.debug(f"\n=== Starting chunk_audio for {file_path} ===")
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            logging.debug(f"Input file size: {file_size_mb:.2f} MB")
            
            if not self.needs_chunking(file_path):
                logging.debug("File doesn't need chunking")
                return [file_path], False
                
            # Get original duration and calculate MB/s ratio
            duration = self._get_audio_duration(file_path)
            mb_per_second = file_size_mb / duration
            logging.debug(f"File duration: {duration:.2f}s, MB/second: {mb_per_second:.4f}")
            
            # Get optimal chunk duration
            optimal_duration = self._get_optimal_chunk_duration(file_path)
            logging.debug(f"Optimal chunk duration: {optimal_duration:.2f}s")
            
            # Find silence points
            silence_points = self._detect_silence_points(file_path)
            logging.debug(f"Found {len(silence_points)} silence points: {silence_points}")
            
            # If no silence points found, split at regular intervals
            if not silence_points:
                logging.debug(f"No silence points found. Using regular intervals.")
                silence_points = list(range(
                    int(optimal_duration), 
                    int(duration), 
                    int(optimal_duration)
                ))
                logging.debug(f"Created {len(silence_points)} regular intervals: {silence_points}")
            else:
                # Calculate optimal chunk duration based on MB/second ratio
                optimal_duration = self._get_optimal_chunk_duration(file_path)
                total_duration = self._get_audio_duration(file_path)
                
                # First, create evenly spaced target points that would give us ideal chunk sizes
                bytes_per_second = self.bytes_per_second
                target_size = (self.min_chunk_size_mb + self.max_chunk_size_mb) / 2  # Aim for middle
                target_duration = (target_size * 1024 * 1024) / bytes_per_second
                
                # Create target points
                target_points = []
                current_time = target_duration
                while current_time < total_duration:
                    target_points.append(current_time)
                    current_time += target_duration
                
                # Now find the closest silence points to our targets
                filtered_points = []
                last_point = 0
                
                for target in target_points:
                    # Find closest silence point to target
                    closest_point = None
                    min_distance = float('inf')
                    
                    for point in silence_points:
                        if point > last_point:  # Only look at points after our last split
                            distance = abs(point - target)
                            chunk_size = self._estimate_chunk_size(point - last_point, file_path)
                            
                            # Check if this point would create valid chunk sizes
                            if (chunk_size >= self.min_chunk_size_mb and 
                                chunk_size <= self.max_chunk_size_mb and 
                                distance < min_distance):
                                closest_point = point
                                min_distance = distance
                    
                    # If no valid silence point found, create one at target
                    if closest_point is None:
                        # Ensure the chunk size would be valid
                        chunk_size = self._estimate_chunk_size(target - last_point, file_path)
                        if chunk_size >= self.min_chunk_size_mb and chunk_size <= self.max_chunk_size_mb:
                            closest_point = target
                    
                    if closest_point is not None:
                        filtered_points.append(closest_point)
                        last_point = closest_point
                
                # Handle the final chunk
                final_duration = total_duration - (filtered_points[-1] if filtered_points else 0)
                final_size = self._estimate_chunk_size(final_duration, file_path)
                
                # If final chunk is too big, add additional split points
                if final_size > self.max_chunk_size_mb:
                    remaining_duration = final_duration
                    last_split = filtered_points[-1] if filtered_points else 0
                    
                    while remaining_duration > 0:
                        next_duration = min(target_duration, remaining_duration)
                        next_split = last_split + next_duration
                        
                        if next_split < total_duration:
                            filtered_points.append(next_split)
                        
                        remaining_duration -= next_duration
                        last_split = next_split
                # If final chunk is too small, merge it with previous chunk
                elif final_size < self.min_chunk_size_mb and filtered_points:
                    filtered_points.pop()  # Remove last split point
                
                silence_points = filtered_points
                logging.debug(f"Filtered to {len(silence_points)} optimal points: {silence_points}")
            
            # Split the file
            chunk_paths = self._split_at_points(file_path, silence_points)
            
            # Log chunk sizes
            total_size = 0
            for i, chunk_path in enumerate(chunk_paths):
                chunk_size_mb = os.path.getsize(chunk_path) / (1024 * 1024)
                chunk_duration = self._get_audio_duration(chunk_path)
                total_size += chunk_size_mb
                logging.debug(f"Chunk {i}: {chunk_size_mb:.2f} MB, Duration: {chunk_duration:.2f}s")
            
            logging.debug(f"Total size of chunks: {total_size:.2f} MB (Original: {file_size_mb:.2f} MB)")
            
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