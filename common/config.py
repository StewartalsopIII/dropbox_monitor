#!/usr/bin/env python3

import os
import logging
from dotenv import load_dotenv

def init_environment():
    """Initialize environment variables."""
    load_dotenv()
    
    # Required environment variables
    required_vars = ['GOOGLE_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

class Config:
    """Shared configuration settings."""
    
    # Audio Processing Settings
    SUPPORTED_FORMATS = ('.wav', '.mp3', '.m4a')
    MAX_CHUNK_SIZE_MB = 15.0
    MIN_CHUNK_SIZE_MB = 10.0
    MIN_SILENCE_DURATION = 1.0
    
    # Audio Conversion Settings
    AUDIO_SAMPLE_RATE = '44100'
    AUDIO_CODEC = 'pcm_s16le'
    
    # File System Settings
    TRANSCRIPT_FOLDER = "transcripts"
    TEMP_PREFIX = 'audio_chunks_'
    
    @staticmethod
    def get_google_api_key():
        """Get Google API key from environment."""
        return os.getenv('GOOGLE_API_KEY')