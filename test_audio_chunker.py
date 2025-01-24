#!/usr/bin/env python3

import unittest
import os
import shutil
import tempfile
import subprocess
from pathlib import Path
from audio_chunker import AudioChunker

class TestAudioChunker(unittest.TestCase):
    def setUp(self):
        """Create temporary directory and test files before each test."""
        self.test_dir = tempfile.mkdtemp(prefix='test_audio_chunker_')
        self.small_file = os.path.join(self.test_dir, 'small.wav')
        self.large_file = os.path.join(self.test_dir, 'large.wav')
        self.silence_file = os.path.join(self.test_dir, 'silence.wav')
        
        # Create test audio files
        self._create_test_files()
        
        # Initialize chunker with smaller chunk size for testing
        self.chunker = AudioChunker(max_chunk_size_mb=1.0)
        
    def tearDown(self):
        """Clean up temporary files after each test."""
        if hasattr(self, 'test_dir') and os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
            
    def _create_test_files(self):
        """Create test audio files of different sizes and patterns."""
        # Create 500KB file (small)
        self._create_audio_file(
            self.small_file,
            duration=5,
            content="sine=440"  # Simple sine wave
        )
        
        # Create 2MB file (large)
        self._create_audio_file(
            self.large_file,
            duration=20,
            content="sine=440"
        )
        
        # Create file with silence points
        self._create_audio_file(
            self.silence_file,
            duration=10,
            content="sine=440[s1];anullsrc=r=44100:cl=mono[s2];[s1][s2]concat=n=2:v=0:a=1"
        )
        
    def _create_audio_file(self, filename: str, duration: int, content: str):
        """Create a test audio file using ffmpeg."""
        command = [
            'ffmpeg',
            '-f', 'lavfi',  # Use libavfilter virtual input
            '-i', content,  # Audio content specification
            '-t', str(duration),  # Duration in seconds
            '-acodec', 'pcm_s16le',  # Same format as main converter
            '-ar', '44100',  # Same sample rate as main converter
            filename,
            '-y'  # Overwrite if exists
        ]
        
        try:
            subprocess.run(command, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error creating test audio file: {e.stderr.decode()}")
            
    def test_needs_chunking(self):
        """Test the needs_chunking method."""
        # Small file should not need chunking
        self.assertFalse(self.chunker.needs_chunking(self.small_file))
        
        # Large file should need chunking
        self.assertTrue(self.chunker.needs_chunking(self.large_file))
        
    def test_detect_silence_points(self):
        """Test silence point detection."""
        silence_points = self.chunker._detect_silence_points(self.silence_file)
        
        # Should detect at least one silence point
        self.assertGreater(len(silence_points), 0)
        
        # Silence points should be sorted
        self.assertEqual(silence_points, sorted(silence_points))
        
    def test_get_audio_duration(self):
        """Test audio duration detection."""
        # Test small file (5 seconds)
        duration = self.chunker._get_audio_duration(self.small_file)
        self.assertAlmostEqual(duration, 5.0, places=1)
        
        # Test large file (20 seconds)
        duration = self.chunker._get_audio_duration(self.large_file)
        self.assertAlmostEqual(duration, 20.0, places=1)
        
    def test_chunk_audio_small_file(self):
        """Test chunking with a file that doesn't need chunking."""
        chunk_paths, was_chunked = self.chunker.chunk_audio(self.small_file)
        
        # Should return original file path and False
        self.assertEqual(len(chunk_paths), 1)
        self.assertEqual(chunk_paths[0], self.small_file)
        self.assertFalse(was_chunked)
        
    def test_chunk_audio_large_file(self):
        """Test chunking with a file that needs chunking."""
        chunk_paths, was_chunked = self.chunker.chunk_audio(self.large_file)
        
        # Should create multiple chunks
        self.assertTrue(len(chunk_paths) > 1)
        self.assertTrue(was_chunked)
        
        # Each chunk should exist and be smaller than max size
        for chunk_path in chunk_paths:
            self.assertTrue(os.path.exists(chunk_path))
            chunk_size = os.path.getsize(chunk_path) / (1024 * 1024)  # Size in MB
            self.assertLessEqual(chunk_size, self.chunker.max_chunk_size_mb)
            
    def test_context_manager(self):
        """Test the context manager functionality."""
        with AudioChunker() as chunker:
            # Create some chunks
            chunk_paths, was_chunked = chunker.chunk_audio(self.large_file)
            temp_dir = chunker.temp_dir
            
            # Temp directory should exist
            self.assertTrue(os.path.exists(temp_dir))
            
            # Chunks should exist
            for path in chunk_paths:
                self.assertTrue(os.path.exists(path))
                
        # After context exit, temp directory should be cleaned up
        self.assertFalse(os.path.exists(temp_dir))
        
    def test_nonexistent_file(self):
        """Test handling of nonexistent files."""
        with self.assertRaises(Exception):
            self.chunker.chunk_audio("nonexistent.wav")
            
    def test_invalid_audio_file(self):
        """Test handling of invalid audio files."""
        # Create an invalid "audio" file
        invalid_file = os.path.join(self.test_dir, "invalid.wav")
        with open(invalid_file, 'w') as f:
            f.write("Not an audio file")
            
        with self.assertRaises(Exception):
            self.chunker.chunk_audio(invalid_file)

if __name__ == '__main__':
    unittest.main()
