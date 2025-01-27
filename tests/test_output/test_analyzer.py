#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch
import tempfile
import os
from datetime import datetime
from output.analyzer import TitleAnalyzer

class MockResponse:
    def __init__(self, text):
        self.text = text

class TestTitleAnalyzer(unittest.TestCase):
    def setUp(self):
        """Create a new analyzer instance before each test."""
        self.mock_model = Mock()
        self.analyzer = TitleAnalyzer(self.mock_model)
        
    def test_analyze_transcript(self):
        """Test basic transcript analysis."""
        # Setup mock response
        mock_analysis = """# Episode Analysis
        
## Key Elements Identified
Test analysis content"""
        self.mock_model.generate_content.return_value = MockResponse(mock_analysis)
        
        # Test analysis
        transcript = "Test transcript content"
        result = self.analyzer.analyze_transcript(transcript)
        
        # Verify
        self.assertIn("Analysis generated on:", result)
        self.assertIn(mock_analysis, result)
        self.mock_model.generate_content.assert_called_once()
        
    def test_prompt_construction(self):
        """Test analysis prompt construction."""
        transcript = "Test transcript"
        prompt = self.analyzer._construct_analysis_prompt(transcript)
        
        # Verify prompt structure
        self.assertEqual(len(prompt), 2)
        self.assertIn("Analyze this podcast transcript", prompt[0]["text"])
        self.assertIn(transcript, prompt[1]["text"])
        
    def test_save_analysis(self):
        """Test saving analysis to file."""
        analysis_text = "Test analysis content"
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            # Test saving
            success = self.analyzer.save_analysis(analysis_text, tmp.name)
            self.assertTrue(success)
            
            # Verify content
            with open(tmp.name, 'r') as f:
                content = f.read()
                self.assertEqual(content, analysis_text)
                
        # Cleanup
        os.unlink(tmp.name)
        
    def test_save_analysis_error(self):
        """Test error handling when saving fails."""
        # Try to save to an invalid path
        success = self.analyzer.save_analysis("test", "/invalid/path/file.md")
        self.assertFalse(success)
        
    def test_markdown_formatting(self):
        """Test markdown formatting of analysis."""
        test_text = "Test analysis"
        formatted = self.analyzer._format_markdown(test_text)
        
        # Verify timestamp and content
        self.assertRegex(formatted, r"Analysis generated on: \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
        self.assertIn(test_text, formatted)

if __name__ == '__main__':
    unittest.main()