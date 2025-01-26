#!/usr/bin/env python3

import unittest
from speaker_diarizer import SpeakerDiarizer, SpeakerSegment
from typing import Dict, List

class TestSpeakerDiarizer(unittest.TestCase):
    def setUp(self):
        """Create a new diarizer instance before each test."""
        self.diarizer = SpeakerDiarizer()
        
    def test_basic_speaker_detection(self):
        """Test detection of basic speaker formats."""
        transcript = """
        Stewart: Hello everyone
        John: Hi Stewart
        """
        segments, mapping = self.diarizer.process_transcript(transcript)
        
        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0].speaker_id, "Stewart")
        self.assertEqual(segments[1].speaker_id, "John")
        
    def test_introduction_detection(self):
        """Test detection of speaker introductions."""
        transcript = """
        Hi, I'm Stewart Alsop, and today we're joined by
        Hello, this is John Smith here.
        """
        segments, mapping = self.diarizer.process_transcript(transcript)
        
        self.assertIn("stewart alsop", mapping)
        self.assertTrue(any('john smith' in key for key in mapping.keys()))
        self.assertEqual(mapping["stewart alsop"], "Stewart Alsop")
        
    def test_numbered_speaker_format(self):
        """Test handling of numbered speaker format."""
        transcript = """
        Speaker 1: First message
        Speaker 2: Second message
        Speaker 1: Third message
        """
        segments, mapping = self.diarizer.process_transcript(transcript)
        
        self.assertEqual(len(segments), 3)
        self.assertEqual(segments[0].speaker_id, "Speaker 1")
        self.assertEqual(segments[1].speaker_id, "Speaker 2")
        
    def test_timing_estimation(self):
        """Test that timing is estimated reasonably."""
        transcript = "Stewart: This is a five word sentence"
        segments, mapping = self.diarizer.process_transcript(transcript)
        
        self.assertEqual(len(segments), 1)
        segment = segments[0]
        self.assertEqual(segment.start_time, 0.0)
        self.assertGreater(segment.end_time, 0.0)
        self.assertEqual(segment.text, "This is a five word sentence")
        
    def test_metadata_formatting(self):
        """Test metadata generation from speaker mapping."""
        transcript = """
        Hi, I'm Stewart Alsop, welcome to the show.
        John: Thanks for having me.
        """
        segments, mapping = self.diarizer.process_transcript(transcript)
        metadata = self.diarizer.format_metadata(mapping)
        
        self.assertEqual(metadata["Host"], "Stewart Alsop")
        self.assertEqual(metadata["Guest"], "John")
        self.assertIn("Diarization Time", metadata)
        
    def test_unknown_speaker_handling(self):
        """Test handling of unknown speakers."""
        transcript = """
        Unknown: This is a test
        Speaker 1: Another test
        """
        segments, mapping = self.diarizer.process_transcript(transcript)
        
        self.assertEqual(len(segments), 2)
        self.assertTrue(all(segment.text for segment in segments))
        
    def test_empty_transcript(self):
        """Test handling of empty transcript."""
        segments, mapping = self.diarizer.process_transcript("")
        
        self.assertEqual(len(segments), 0)
        self.assertEqual(len(mapping), 0)

if __name__ == '__main__':
    unittest.main()