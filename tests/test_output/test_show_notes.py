#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
from output.show_notes import ShowNotes

class TestShowNotes(unittest.TestCase):
    """Test suite for ShowNotes class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_model = Mock()
        self.mock_model.generate_content.return_value = Mock(text="Test response")
        self.show_notes = ShowNotes(self.mock_model)
        
    def test_initialization(self):
        """Test ShowNotes initialization."""
        self.assertIsInstance(self.show_notes._templates, dict)
        self.assertIn('en', self.show_notes._templates)
        
    def test_generate_notes_basic(self):
        """Test basic notes generation."""
        transcript = "Test transcript content"
        notes = self.show_notes.generate_notes(transcript, sections=['summary'])
        
        self.assertIsInstance(notes, dict)
        self.assertIn('summary', notes)
        self.assertEqual(notes['summary'], "Test response")
        
    def test_generate_notes_invalid_language(self):
        """Test error handling for invalid language."""
        with self.assertRaises(ValueError):
            self.show_notes.generate_notes("Test", language='invalid')
            
    def test_format_notes(self):
        """Test notes formatting."""
        notes = {
            'summary': 'Test summary',
            'key_moments': 'Test moments'
        }
        formatted = self.show_notes.format_notes(notes)
        
        self.assertIn("# Show Notes", formatted)
        self.assertIn("## Summary", formatted)
        self.assertIn("## Key Moments", formatted)
        
if __name__ == '__main__':
    unittest.main()