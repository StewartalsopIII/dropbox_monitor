#!/usr/bin/env python3

from datetime import datetime
from typing import List, Optional, Dict

class TranscriptFormatter:
    """Handles formatting of transcript text into markdown format."""
    
    def __init__(self):
        """Initialize the TranscriptFormatter."""
        self.metadata = {}
        
    def format_transcript(self, 
                         raw_text: str, 
                         metadata: Optional[Dict] = None) -> str:
        """
        Convert raw transcript text to formatted markdown.
        
        Args:
            raw_text (str): Raw transcript text
            metadata (Dict, optional): Additional metadata like speakers, file info
            
        Returns:
            str: Formatted markdown text
        """
        if metadata:
            self.metadata = metadata
            
        # Build the formatted transcript
        formatted_parts = []
        
        # Add header with metadata
        formatted_parts.extend(self._create_header())
        
        # Format the main content
        formatted_parts.extend(self._format_content(raw_text))
        
        # Join all parts with double newlines
        return "\n\n".join(formatted_parts)
    
    def _create_header(self) -> List[str]:
        """Create the markdown header with metadata."""
        header_parts = ["# Transcript"]
        
        # Add timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        header_parts.append(f"**Generated**: {timestamp}")
        
        # Add any additional metadata
        for key, value in self.metadata.items():
            header_parts.append(f"**{key}**: {value}")
            
        return header_parts
    
    def _format_content(self, content: str) -> List[str]:
        """Format the main transcript content."""
        formatted_lines = []
        
        # Split into lines and process each
        lines = content.strip().split('\n')
        
        current_speaker = None
        for line in lines:
            if not line.strip():
                continue
                
            # Try to detect speaker patterns
            if ':' in line:
                speaker, text = line.split(':', 1)
                speaker = speaker.strip()
                text = text.strip()
                
                # Check if this is a new speaker
                if speaker != current_speaker:
                    current_speaker = speaker
                    # Add extra line before new speaker except at start
                    if formatted_lines:
                        formatted_lines.append("")
                        
                # Format with speaker name in bold
                if speaker in self.metadata.get("speaker_mapping", {}):
                    mapped_name = self.metadata["speaker_mapping"][speaker]
                    formatted_lines.append(f"**{mapped_name}**: {text}")
                else:
                    formatted_lines.append(f"**{speaker}**: {text}")
            else:
                formatted_lines.append(line)
        
        return formatted_lines