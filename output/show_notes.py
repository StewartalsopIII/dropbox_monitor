#!/usr/bin/env python3

import logging
from datetime import datetime
from typing import Dict, List, Optional

class ShowNotes:
    """Generates bilingual show notes from transcript content."""
    
    def __init__(self, model):
        """
        Initialize ShowNotes generator.
        
        Args:
            model: An instance of the language model used for generation
        """
        self.model = model
        
        # Base templates for different sections
        self._templates = {
            'en': {
                'summary': """Create a concise summary of this podcast episode that:
                - Captures the main discussion points
                - Highlights key insights and takeaways
                - Preserves important context
                - Maintains the conversation's tone""",
                
                'key_moments': """Identify the key moments in this conversation including:
                - Important revelations or insights
                - Memorable quotes or exchanges
                - Significant topic transitions
                - Notable examples or analogies""",
                
                'guest_insights': """Analyze the guest's unique contributions:
                - Areas of expertise demonstrated
                - Key perspectives shared
                - Memorable stories or examples
                - Notable quotes worth highlighting""",
                
                'resources': """Extract all mentioned resources including:
                - Books, articles, or papers
                - Websites or online tools
                - People or organizations
                - Other relevant references""",
                
                'action_items': """Identify actionable takeaways including:
                - Specific recommendations
                - Tools or techniques to try
                - Further areas to explore
                - Next steps for listeners""",
                
                'timestamps': """Create a timestamped outline of the conversation:
                - Major topic changes
                - Key insights or revelations
                - Notable quotes or examples
                - Important transitions""",
                
                'questions': """Extract important questions including:
                - Direct questions asked
                - Implied questions raised
                - Areas for further exploration
                - Points of curiosity""",
                
                'themes': """Identify recurring themes including:
                - Major conceptual threads
                - Repeated ideas or phrases
                - Underlying patterns
                - Connecting narratives""",
                
                'quotables': """Find highly quotable moments that:
                - Capture key insights
                - Express ideas memorably
                - Demonstrate expertise
                - Inspire or provoke thought"""
            },
            'es': {
                # Spanish templates will mirror English but be added when needed
            }
        }
        
    def generate_notes(self, 
                      transcript_text: str,
                      sections: Optional[List[str]] = None,
                      language: str = 'en') -> Dict[str, str]:
        """
        Generate show notes from transcript text.
        
        Args:
            transcript_text (str): The transcript text to analyze
            sections (List[str], optional): List of sections to generate
            language (str): Target language ('en' or 'es')
            
        Returns:
            Dict[str, str]: Generated content by section
        """
        if language not in ['en', 'es']:
            raise ValueError("Language must be 'en' or 'es'")
            
        if not sections:
            sections = list(self._templates[language].keys())
            
        results = {}
        for section in sections:
            if section not in self._templates[language]:
                logging.warning(f"Unknown section requested: {section}")
                continue
                
            try:
                prompt = self._construct_prompt(section, transcript_text, language)
                response = self.model.generate_content(prompt)
                results[section] = response.text.strip()
            except Exception as e:
                logging.error(f"Error generating {section}: {str(e)}")
                results[section] = f"Error generating {section}"
                
        return results
    
    def _construct_prompt(self, section: str, transcript_text: str, language: str) -> List[str]:
        """
        Construct the prompt for a specific section.
        
        Args:
            section (str): The section to generate
            transcript_text (str): The transcript text
            language (str): Target language
            
        Returns:
            List[str]: List of prompt components
        """
        return [
            {
                "text": self._templates[language][section]
            },
            {
                "text": f"\nHere's the transcript to analyze:\n\n{transcript_text}"
            }
        ]
        
    def format_notes(self, notes: Dict[str, str], timestamp_format: str = '%H:%M:%S') -> str:
        """
        Format show notes as markdown.
        
        Args:
            notes (Dict[str, str]): Generated notes by section
            timestamp_format (str): Format for timestamps
            
        Returns:
            str: Formatted markdown text
        """
        formatted_parts = []
        
        # Add header
        formatted_parts.append("# Show Notes")
        formatted_parts.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Add each section
        for section, content in notes.items():
            if not content:
                continue
                
            # Convert section name to title
            title = section.replace('_', ' ').title()
            formatted_parts.append(f"## {title}")
            formatted_parts.append(content)
            formatted_parts.append("")  # Empty line between sections
            
        return "\n".join(formatted_parts)
        
    def save_notes(self, notes_text: str, output_path: str) -> bool:
        """
        Save show notes to a markdown file.
        
        Args:
            notes_text (str): The formatted notes text
            output_path (str): Path where to save the notes
            
        Returns:
            bool: True if save successful
        """
        try:
            with open(output_path, 'w') as f:
                f.write(notes_text)
            return True
        except Exception as e:
            logging.error(f"Error saving show notes: {str(e)}")
            return False