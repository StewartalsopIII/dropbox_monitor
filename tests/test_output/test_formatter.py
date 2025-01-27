#!/usr/bin/env python3

import unittest
from datetime import datetime
from output.formatter import TranscriptFormatter

class TestTranscriptFormatter(unittest.TestCase):
    def setUp(self):
        """Create a new formatter instance before each test."""
        self.formatter = TranscriptFormatter()

    def test_basic_formatting(self):
        """Test basic transcript formatting without metadata."""
        raw_text = "Hello, this is a test."
        formatted = self.formatter.format_transcript(raw_text)
        
        self.assertIn("# Transcript", formatted)
        self.assertIn("**Generated**:", formatted)
        self.assertIn("Hello, this is a test.", formatted)

    def test_metadata_handling(self):
        """Test formatting with metadata."""
        metadata = {
            "File": "test.m4a",
            "Duration": "5:30",
            "Speakers": "John, Jane"
        }
        
        raw_text = "Test content"
        formatted = self.formatter.format_transcript(raw_text, metadata)
        
        for key, value in metadata.items():
            self.assertIn(f"**{key}**: {value}", formatted)

    def test_speaker_detection(self):
        """Test speaker line detection and formatting."""
        raw_text = """
Stewart: Welcome to the show
John: Thanks for having me
Some normal text
Stewart: Let's begin
"""
        formatted = self.formatter.format_transcript(raw_text)
        
        self.assertIn("**Stewart**:", formatted)
        self.assertIn("**John**:", formatted)
        self.assertIn("Some normal text", formatted)

    def test_empty_content(self):
        """Test handling of empty content."""
        formatted = self.formatter.format_transcript("")
        
        self.assertIn("# Transcript", formatted)
        self.assertIn("**Generated**:", formatted)

    def test_multiline_formatting(self):
        """Test formatting of multiline content."""
        raw_text = """
First line
Second line

Stewart: Multiple
lines of
dialog

John: Another response
"""
        formatted = self.formatter.format_transcript(raw_text)
        
        self.assertIn("First line", formatted)
        self.assertIn("Second line", formatted)
        self.assertIn("**Stewart**:", formatted)
        self.assertIn("**John**:", formatted)

if __name__ == '__main__':
    unittest.main()