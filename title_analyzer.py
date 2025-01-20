import logging
import os
from datetime import datetime

class TitleAnalyzer:
    def __init__(self, model):
        self.model = model
        
    def analyze_transcript(self, transcript_text):
        """Analyze transcript and generate title variations."""
        # Construct the analysis prompt
        prompt = self._construct_analysis_prompt(transcript_text)
        
        # Generate analysis using the model
        response = self.model.generate_content(prompt)
        
        return self._format_markdown(response.text)
        
    def _construct_analysis_prompt(self, transcript_text):
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
    
    def _format_markdown(self, analysis_text):
        """Ensure the analysis is properly formatted as markdown."""
        # The model should already return markdown, but we can add any additional
        # formatting or cleanup here if needed
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"Analysis generated on: {timestamp}\n\n{analysis_text}"
        
    def save_analysis(self, analysis_text, output_path):
        """Save the analysis to a markdown file."""
        try:
            with open(output_path, 'w') as f:
                f.write(analysis_text)
            return True
        except Exception as e:
            logging.error(f"Error saving analysis: {str(e)}")
            return False