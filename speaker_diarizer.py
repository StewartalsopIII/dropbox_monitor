#!/usr/bin/env python3

import re
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SpeakerSegment:
    """Represents a segment of speech by a speaker."""
    speaker_id: str
    start_time: float
    end_time: float
    text: str
    mapped_name: Optional[str] = None

class SpeakerDiarizer:
    """Handles speaker identification and diarization from transcript text."""
    
    def __init__(self):
        self.known_speakers = {
            "stewart": "Stewart Alsop",
            "stewart alsop": "Stewart Alsop",
            "stewart alsop iii": "Stewart Alsop",
            "host": "Stewart Alsop"
        }
        self.speaker_patterns = [
            r'^([A-Za-z\s]+):\s*(.+)$',  # Standard format: "Name: text"
            r'^Speaker\s+(\d+):\s*(.+)$',  # Numbered format: "Speaker 1: text"
            r'(?:Hi|Hello|Hey),?\s+(?:I\'m|this is)\s+([A-Za-z\s]+?)(?:,|\.|$|\s+and)',  # Introductions
            r'(?:Hi|Hello|Hey),?\s+([A-Za-z\s]+?)\s+here(?:\.|\s|$)'  # "Name here" format
        ]
    
    def process_transcript(self, transcript_text: str) -> Tuple[List[SpeakerSegment], Dict[str, str]]:
        """
        Process transcript text to identify speakers and their segments.
        
        Args:
            transcript_text: The raw transcript text
            
        Returns:
            Tuple containing:
            - List of SpeakerSegment objects
            - Dictionary mapping speaker IDs to names
        """
        # Initialize tracking
        segments: List[SpeakerSegment] = []
        speaker_mapping: Dict[str, str] = {}
        current_time = 0.0
        
        # First pass: Find introductions and explicit speaker names
        intro_names = self._find_introductions(transcript_text)
        speaker_mapping.update(self._normalize_speaker_names(intro_names))
        
        # Process each line of the transcript
        lines = transcript_text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for speaker patterns
            speaker_id, text = self._identify_speaker(line)
            if speaker_id:
                # Estimate timing (rough approximation)
                words = len(text.split())
                segment_duration = words * 0.3  # Rough estimate: 0.3 seconds per word
                
                segment = SpeakerSegment(
                    speaker_id=speaker_id,
                    start_time=current_time,
                    end_time=current_time + segment_duration,
                    text=text,
                    mapped_name=speaker_mapping.get(speaker_id.lower())
                )
                segments.append(segment)
                current_time += segment_duration
                
                # Update speaker mapping if not already known
                if speaker_id.lower() not in speaker_mapping:
                    normalized_name = self._normalize_speaker_name(speaker_id)
                    if normalized_name:
                        speaker_mapping[speaker_id.lower()] = normalized_name
        
        # If we haven't identified the host, add Stewart as the first speaker
        if not any(name == "Stewart Alsop" for name in speaker_mapping.values()):
            first_speaker = next(iter(speaker_mapping.values())) if speaker_mapping else None
            if first_speaker:
                speaker_mapping[first_speaker.lower()] = "Stewart Alsop"
        
        return segments, speaker_mapping
    
    def _find_introductions(self, text: str) -> List[str]:
        """Find speaker names from introduction patterns."""
        names = []
        for pattern in self.speaker_patterns[2:]:  # Use only introduction patterns
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                name = match.group(1).strip()
                if name.lower() not in ['i', 'me', 'everyone', 'everybody']:
                    # Convert to lowercase for consistent mapping
                    names.append(name.lower())
        return names
    
    def _identify_speaker(self, line: str) -> Tuple[Optional[str], str]:
        """
        Identify speaker and text from a line.
        Returns tuple of (speaker_id, text) or (None, original_line).
        """
        # Try each pattern
        for pattern in self.speaker_patterns[:2]:  # Use only speaker label patterns
            match = re.match(pattern, line)
            if match:
                # For numbered speakers, keep the "Speaker" prefix
                speaker_id = match.group(1).strip()
                if re.match(r'^\d+$', speaker_id):
                    speaker_id = f"Speaker {speaker_id}"
                return speaker_id, match.group(2).strip()
        
        return None, line
    
    def _normalize_speaker_names(self, names: List[str]) -> Dict[str, str]:
        """Convert list of names to normalized speaker mapping."""
        mapping = {}
        
        # First pass to identify full names
        for name in names:
            if 'stewart' in name.lower() and 'alsop' in name.lower():
                mapping['stewart alsop'] = 'Stewart Alsop'
                break
                
        # Second pass for other names
        for name in names:
            normalized = self._normalize_speaker_name(name)
            if normalized:
                name_key = name.lower()
                if name_key not in mapping:
                    mapping[name_key] = normalized
                    
        return mapping
    
    def _normalize_speaker_name(self, name: str) -> Optional[str]:
        """Normalize a speaker name, returns None if invalid."""
        name = name.lower().strip()
        
        # Remove common prefixes
        name = re.sub(r'^(this is|here|i\'m)\s+', '', name)
        
        # Check known speakers
        if name in self.known_speakers:
            return self.known_speakers[name]
        
        # Basic validation
        if len(name) < 2 or name in ['i', 'me', 'speaker']:
            return None
            
        # Proper case each word
        normalized = ' '.join(word.capitalize() for word in name.split())
        
        # Add to known speakers if it matches a pattern
        if 'stewart' in name.lower():
            self.known_speakers[name] = "Stewart Alsop"
            return "Stewart Alsop"
            
        return normalized
    
    def format_metadata(self, speaker_mapping: Dict[str, str]) -> Dict[str, str]:
        """Format speaker information for transcript metadata."""
        speakers = sorted(set(speaker_mapping.values()))
        return {
            "Host": next((name for name in speakers if "Stewart" in name), "Unknown Host"),
            "Guest": next((name for name in speakers if "Stewart" not in name), "Unknown Guest"),
            "Speakers": ", ".join(speakers),
            "Diarization Time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }