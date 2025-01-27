#!/usr/bin/env python3

import unittest
from unittest.mock import Mock, patch, MagicMock

# Create module structure for mocks
import sys
from types import ModuleType

# Mock google cloud speech
mock_cloud = ModuleType('google.cloud')
mock_speech = ModuleType('google.cloud.speech')
sys.modules['google'] = ModuleType('google')
sys.modules['google.cloud'] = mock_cloud
sys.modules['google.cloud.speech'] = mock_speech
# Set up speech recognition mocks
class MockAudioEncoding:
    LINEAR16 = "LINEAR16"

class MockConfig:
    AudioEncoding = MockAudioEncoding
    def __init__(self, *args, **kwargs):
        self.encoding = kwargs.get('encoding')
        self.sample_rate_hertz = kwargs.get('sample_rate_hertz')
        self.language_code = kwargs.get('language_code')
        self.enable_speaker_diarization = kwargs.get('enable_speaker_diarization')
        self.diarization_speaker_count = kwargs.get('diarization_speaker_count')

mock_speech.SpeechClient = Mock
mock_speech.RecognitionAudio = Mock
mock_speech.RecognitionConfig = MockConfig

# Mock google generative AI
mock_genai = ModuleType('google.generativeai')
sys.modules['google.generativeai'] = mock_genai
mock_genai.configure = Mock()

class MockGenerativeModel(Mock):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.generate_content = Mock()

mock_genai.GenerativeModel = MockGenerativeModel
mock_genai.upload_file = Mock()
mock_genai.upload_file = Mock

# Now import the module under test
from processing.transcriber import TranscriptionService, CloudSpeechTranscriber, GeminiTranscriber
import google.generativeai as genai
from google.cloud import speech

class TestCloudSpeechTranscriber(unittest.TestCase):
    def setUp(self):
        self.transcriber = CloudSpeechTranscriber()
    
    @patch('processing.transcriber.speech.SpeechClient')
    def test_transcribe_audio_basic(self, mock_client_class):
        # Setup mock client
        mock_client = mock_client_class.return_value
        
        # Setup mock response
        mock_word = Mock()
        mock_word.speaker_tag = 1
        mock_word.word = "hello"
        
        mock_alternative = Mock()
        mock_alternative.words = [mock_word]
        
        mock_result = Mock()
        mock_result.alternatives = [mock_alternative]
        
        mock_response = Mock()
        mock_response.results = [mock_result]
        
        # Configure mock client
        mock_client.recognize.return_value = mock_response
        self.transcriber.client = mock_client  # Replace the client instance
        
        # Test transcription
        with patch('builtins.open', unittest.mock.mock_open(read_data=b'fake_audio_data')):
            result = self.transcriber.transcribe_audio("fake_path.wav")
        
        self.assertIn("Speaker 1: hello", result)
        
    @patch('processing.transcriber.speech.SpeechClient')
    def test_transcribe_audio_multiple_speakers(self, mock_client_class):
        # Setup mock client
        mock_client = mock_client_class.return_value
        
        # Setup mock words for multiple speakers
        mock_words = [
            Mock(speaker_tag=1, word="Hello"),
            Mock(speaker_tag=2, word="Hi"),
            Mock(speaker_tag=1, word="there"),
        ]
        
        mock_alternative = Mock()
        mock_alternative.words = mock_words
        
        mock_result = Mock()
        mock_result.alternatives = [mock_alternative]
        
        mock_response = Mock()
        mock_response.results = [mock_result]
        
        # Configure mock client
        mock_client.recognize.return_value = mock_response
        self.transcriber.client = mock_client  # Replace the client instance
        
        # Test transcription
        with patch('builtins.open', unittest.mock.mock_open(read_data=b'fake_audio_data')):
            result = self.transcriber.transcribe_audio("fake_path.wav")
        
        expected_lines = [
            "Speaker 1: Hello",
            "Speaker 2: Hi",
            "Speaker 1: there"
        ]
        for line in expected_lines:
            self.assertIn(line, result)

class TestGeminiTranscriber(unittest.TestCase):
    def setUp(self):
        self.transcriber = GeminiTranscriber()
    
    @patch('processing.transcriber.AudioChunker')
    def test_transcribe_single_file(self, mock_chunker_class):
        # Configure the transcriber's model mock
        mock_response = Mock()
        mock_response.text = "Speaker 1: Test transcription"
        self.transcriber.model.generate_content.return_value = mock_response
        
        # Setup chunker mock
        mock_chunker = mock_chunker_class.return_value
        mock_chunker.__enter__.return_value = mock_chunker
        mock_chunker.chunk_audio.return_value = (["fake_path.wav"], False)
        
        # Test transcription
        result = self.transcriber.transcribe_audio("fake_path.wav")
        
        self.assertEqual(result.strip(), "Speaker 1: Test transcription")
    
    @patch('processing.transcriber.AudioChunker')
    def test_transcribe_chunked_file(self, mock_chunker_class):
        # Configure responses for each chunk
        mock_responses = [
            Mock(text="Speaker 1: First chunk"),
            Mock(text="Speaker 1: Second chunk")
        ]
        self.transcriber.model.generate_content.side_effect = mock_responses
        
        # Setup chunker to return multiple chunks
        mock_chunker = mock_chunker_class.return_value
        mock_chunker.__enter__.return_value = mock_chunker
        mock_chunker.chunk_audio.return_value = (["chunk1.wav", "chunk2.wav"], True)
        
        # Test chunked transcription
        result = self.transcriber.transcribe_audio("large_file.wav")
        
        expected_text = "Speaker 1: First chunk\n\nSpeaker 1: Second chunk"
        self.assertEqual(result.strip(), expected_text)
    
    def test_extract_speakers(self):
        transcription = """
        Speaker 1: Hello there
        John: Hi everyone
        Speaker 1: How are you?
        """
        speakers = self.transcriber._extract_speakers(transcription)
        self.assertCountEqual(speakers, ["Speaker 1", "John"])

if __name__ == '__main__':
    unittest.main()