#!/usr/bin/env python3

from abc import ABC, abstractmethod
from typing import Optional, List
import logging
import importlib.util
from processing.chunker import AudioChunker
from common.config import Config

# Try to import Google Cloud Speech
try:
    from google.cloud import speech
except ImportError:
    speech = None

# Try to import Google Generative AI
try:
    import google.generativeai as genai
except ImportError:
    genai = None

class TranscriptionService(ABC):
    """Abstract base class for transcription services."""
    
    @abstractmethod
    def transcribe_audio(self, wav_path: str) -> str:
        """
        Transcribe audio from the given WAV file path.
        
        Args:
            wav_path: Path to the WAV file to transcribe
            
        Returns:
            str: The transcribed text
        """
        pass

class CloudSpeechTranscriber(TranscriptionService):
    """Google Cloud Speech-to-Text transcription service."""
    
    def __init__(self):
        if speech is None:
            raise ImportError("google-cloud-speech package is required for CloudSpeechTranscriber")
        self.client = speech.SpeechClient()
        
    def transcribe_audio(self, wav_path: str) -> str:
        """Transcribe audio using Google Cloud Speech-to-Text."""
        try:
            # Read the audio file
            with open(wav_path, 'rb') as audio_file:
                content = audio_file.read()
            
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=44100,
                language_code="en-US",
                enable_speaker_diarization=True,
                diarization_speaker_count=2  # Assumes 2 speakers for meeting
            )
            
            # Perform the transcription
            response = self.client.recognize(config=config, audio=audio)
            
            # Process speaker diarization
            transcript = []
            for result in response.results:
                alternative = result.alternatives[0]
                
                # Extract speaker tags
                for word in alternative.words:
                    speaker_tag = word.speaker_tag
                    speaker = f"Speaker {speaker_tag}"
                    content = word.word
                    
                    # Start new line for new speaker
                    if not transcript or not transcript[-1].startswith(f"{speaker}:"):
                        transcript.append(f"{speaker}: {content}")
                    else:
                        transcript[-1] += f" {content}"
            
            return "\n".join(transcript)
            
        except Exception as e:
            logging.error(f"Cloud Speech transcription error: {str(e)}")
            raise

class GeminiTranscriber(TranscriptionService):
    """Google Gemini Pro transcription service with automatic chunking."""
    
    def __init__(self, max_chunk_size_mb: float = 15.0):
        """
        Initialize the Gemini transcriber.
        
        Args:
            max_chunk_size_mb: Maximum chunk size in megabytes
        """
        if genai is None:
            raise ImportError("google-generativeai package is required for GeminiTranscriber")
        genai.configure(api_key=Config.get_google_api_key())
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.max_chunk_size_mb = max_chunk_size_mb
        
    def transcribe_audio(self, wav_path: str) -> str:
        """
        Transcribe audio using Google Gemini Pro.
        Automatically handles file chunking for large files.
        """
        try:
            # Initialize chunker
            with AudioChunker(max_chunk_size_mb=self.max_chunk_size_mb) as chunker:
                chunk_paths, was_chunked = chunker.chunk_audio(wav_path)
                
                if was_chunked:
                    logging.info(f"File split into {len(chunk_paths)} chunks for processing")
                    transcriptions = []
                    speaker_context = None
                    
                    # Process each chunk
                    for i, chunk_path in enumerate(chunk_paths):
                        transcription = self._transcribe_chunk(chunk_path, i+1, len(chunk_paths), speaker_context)
                        
                        # Update speaker context for next chunk if needed
                        if transcription:
                            speaker_context = self._extract_speakers(transcription)
                        
                        transcriptions.append(transcription)
                    
                    # Combine transcriptions with double newlines between chunks
                    return "\n\n".join(transcriptions)
                
                else:
                    # Process single file
                    return self._transcribe_chunk(wav_path)
            
        except Exception as e:
            logging.error(f"Gemini transcription error: {str(e)}")
            raise
            
    def _transcribe_chunk(self, 
                         chunk_path: str, 
                         chunk_num: Optional[int] = None, 
                         total_chunks: Optional[int] = None,
                         speaker_context: Optional[List[str]] = None) -> str:
        """
        Transcribe a single audio chunk.
        
        Args:
            chunk_path: Path to the audio chunk
            chunk_num: Current chunk number (if processing multiple chunks)
            total_chunks: Total number of chunks (if processing multiple chunks)
            speaker_context: List of speaker names from previous chunks
            
        Returns:
            str: Transcribed text from the chunk
        """
        try:
            # Log progress if processing multiple chunks
            if chunk_num and total_chunks:
                logging.info(f"Processing chunk {chunk_num}/{total_chunks}...")
            
            # Upload the audio
            audio_file = genai.upload_file(chunk_path)
            
            # Prepare prompt
            prompt = ["Please transcribe this audio. Maintain existing speaker labels and formatting."]
            if speaker_context and chunk_num and chunk_num > 1:
                prompt.append(f"Previous speakers were: {', '.join(speaker_context)}")
            
            # Generate transcription
            parts = [audio_file] + prompt
            response = self.model.generate_content(parts)
            return response.text.strip()
            
        except Exception as e:
            logging.error(f"Error transcribing chunk {chunk_path}: {str(e)}")
            return ""
            
    def _extract_speakers(self, transcription: str) -> List[str]:
        """Extract speaker names from transcription for context in next chunk."""
        speakers = set()
        for line in transcription.split('\n'):
            if ':' in line:
                speaker = line.split(':', 1)[0].strip()
                if speaker:
                    speakers.add(speaker)
        return list(speakers)