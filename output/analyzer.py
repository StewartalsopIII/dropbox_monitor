#!/usr/bin/env python3

import logging
import os
from datetime import datetime

class TitleAnalyzer:
    """Analyzes transcripts to generate title variations and insights."""
    
    def __init__(self, model):
        """
        Initialize the TitleAnalyzer.
        
        Args:
            model: An instance of the language model used for analysis
        """
        self.model = model
        
    def analyze_transcript(self, transcript_text: str) -> str:
        """
        Analyze transcript and generate title variations.
        
        Args:
            transcript_text (str): The transcript text to analyze
            
        Returns:
            str: Formatted markdown analysis including titles and insights
        """
        # Construct the analysis prompt
        prompt = self._construct_analysis_prompt(transcript_text)
        
        # Generate analysis using the model
        response = self.model.generate_content(prompt)
        
        return self._format_markdown(response.text)
        
    def _construct_analysis_prompt(self, transcript_text: str) -> list:
        """
        Construct the prompt for transcript analysis.
        
        Args:
            transcript_text (str): The transcript text
            
        Returns:
            list: List of prompt components
        """
        return [
            {
                "text": """Analyze this podcast transcript and generate creative titles. 
                
Task 1 - First identify:
- Stewart's speaking style, tone, and patterns
- Key themes and narrative arcs
- Most memorable or surprising quotes
- Guest's expertise and unique contributions

Task 2 - Then generate 10 title variations that:
- Capture both substance and intrigue
- Balance clarity with creativity
- Vary in style (questions, quotes, metaphors)
- Reflect the authentic voice of the show

Provide your analysis in this markdown format:

# Episode Analysis

## Key Elements Identified

### Stewart's Style & Tone
[List key patterns and expressions]

### Core Themes
[List main themes and key discussions]

### Memorable Quotes
[List standout quotes with context]

### Guest Insights
[List expertise areas and unique contributions]

## Title Variations

1. [Title]
   - Drawing from: [elements used]
   - Appeal: [why it works]

[Continue for all 10 variations]"""
            },
            {
                "text": "Here's the transcript to analyze:\n\n" + transcript_text
            }
        ]
    
    def _format_markdown(self, analysis_text: str) -> str:
        """
        Ensure the analysis is properly formatted as markdown.
        
        Args:
            analysis_text (str): The raw analysis text
            
        Returns:
            str: Formatted markdown with timestamp
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"Analysis generated on: {timestamp}\n\n{analysis_text}"
        
    def save_analysis(self, analysis_text: str, output_path: str) -> bool:
        """
        Save the analysis to a markdown file.
        
        Args:
            analysis_text (str): The analysis text to save
            output_path (str): Path where to save the analysis
            
        Returns:
            bool: True if save successful, False otherwise
        """
        try:
            with open(output_path, 'w') as f:
                f.write(analysis_text)
            return True
        except Exception as e:
            logging.error(f"Error saving analysis: {str(e)}")
            return False