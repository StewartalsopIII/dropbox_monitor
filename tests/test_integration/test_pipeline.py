#!/usr/bin/env python3

import unittest
import os
import tempfile
import shutil
from pathlib import Path
import subprocess

from processing.chunker import AudioChunker
from processing.transcriber import AudioTranscriber
from processing.diarizer import SpeakerDiarizer
from output.formatter import TranscriptFormatter
from output.analyzer import TitleAnalyzer
from input.file_handler import AudioFileHandler

class TestAudioProcessingPipeline(unittest.TestCase):
    def setUp(self):
        """Set up test environment with temporary directories and test files."""
        self.test_dir = tempfile.mkdtemp(prefix='test_pipeline_')
        self.input_dir = os.path.join(self.test_dir, 'input')
        self.output_dir = os.path.join(self.test_dir, 'output')
        
        os.makedirs(self.input_dir)
        os.makedirs(self.output_dir)
        
        # Create a test audio file
        self.test_audio = os.path.join(self.input_dir, 'test.wav')
        self._create_test_audio()
        
        # Initialize components
        self.file_handler = AudioFileHandler()
        self.chunker = AudioChunker()
        self.transcriber = AudioTranscriber()
        self.diarizer = SpeakerDiarizer()
        self.formatter = TranscriptFormatter()
        
    def tearDown(self):
        """Clean up temporary files."""
        shutil.rmtree(self.test_dir)
        
    def _create_test_audio(self):
        """Create a test WAV file with speech-like content."""
        command = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', 'sine=frequency=440:duration=5',
            '-acodec', 'pcm_s16le',
            '-ar', '44100',
            self.test_audio,
            '-y'
        ]
        subprocess.run(command, check=True, capture_output=True)
        
    def test_full_pipeline(self):
        """Test the complete audio processing pipeline."""
        # Step 1: File Detection and Validation
        self.assertTrue(
            self.file_handler.is_valid_audio(self.test_audio),
            "File handler should recognize test audio"
        )
        
        # Step 2: Chunking (if needed)
        chunks, was_chunked = self.chunker.chunk_audio(self.test_audio)
        self.assertIsInstance(chunks, list, "Chunking should return a list")
        
        # Step 3: Transcription
        transcription = None
        for chunk in chunks:
            chunk_trans = self.transcriber.transcribe(chunk)
            if transcription is None:
                transcription = chunk_trans
            else:
                transcription += "\n" + chunk_trans
        
        self.assertIsNotNone(transcription, "Transcription should not be None")
        
        # Step 4: Speaker Diarization
        segments, speaker_mapping = self.diarizer.process_transcript(transcription)
        self.assertIsInstance(segments, list, "Diarization should return segments")
        self.assertIsInstance(speaker_mapping, dict, "Should return speaker mapping")
        
        # Step 5: Formatting
        metadata = {
            "File": os.path.basename(self.test_audio),
            "Speakers": ", ".join(speaker_mapping.values())
        }
        formatted_transcript = self.formatter.format_transcript(
            transcription, metadata)
        
        self.assertIsInstance(
            formatted_transcript,
            str,
            "Formatter should return string"
        )
        
        # Step 6: Verify Output
        output_path = os.path.join(
            self.output_dir,
            Path(self.test_audio).stem + ".md"
        )
        
        with open(output_path, 'w') as f:
            f.write(formatted_transcript)
            
        self.assertTrue(
            os.path.exists(output_path),
            "Output file should be created"
        )
        
        # Verify file contents
        with open(output_path, 'r') as f:
            content = f.read()
            self.assertIn("# Transcript", content)
            self.assertIn(metadata["File"], content)
            
    def test_error_handling(self):
        """Test error handling throughout the pipeline."""
        # Test invalid file
        invalid_file = os.path.join(self.input_dir, "invalid.wav")
        with open(invalid_file, 'w') as f:
            f.write("Not an audio file")
            
        with self.assertRaises(Exception):
            self.file_handler.is_valid_audio(invalid_file)
            
        # Test missing file
        missing_file = os.path.join(self.input_dir, "missing.wav")
        with self.assertRaises(FileNotFoundError):
            self.chunker.chunk_audio(missing_file)

if __name__ == '__main__':
    unittest.main()