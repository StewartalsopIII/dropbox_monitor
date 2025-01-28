# Configuration Guide

This document provides detailed information about configuring and customizing the Dropbox Audio Processing Suite.

## Environment Variables

### Required Variables
```bash
# Google API key for transcription services
GOOGLE_API_KEY=your_api_key_here
```

### Optional Variables
```bash
# Watch folder paths (defaults to current directory if not set)
WATCH_FOLDER_ZOOM=/path/to/zoom/recordings
WATCH_FOLDER_AUDIO=/path/to/audio/files

# Log configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=audio_processor.log
```

## Audio Processing Configuration

The following settings can be found in `common/config.py`:

### Chunk Size Settings
```python
MAX_CHUNK_SIZE_MB = 15.0  # Maximum size of audio chunks
MIN_CHUNK_SIZE_MB = 10.0  # Minimum size of audio chunks
```

- **MAX_CHUNK_SIZE_MB**: Maximum size of each audio chunk (15MB recommended for API limits)
- **MIN_CHUNK_SIZE_MB**: Minimum size to maintain context (10MB recommended)

### Audio Format Settings
```python
SUPPORTED_FORMATS = ('.wav', '.mp3', '.m4a')  # Supported audio formats
AUDIO_SAMPLE_RATE = '44100'                   # Audio sample rate
AUDIO_CODEC = 'pcm_s16le'                     # Audio codec for processing
```

### Silence Detection
```python
MIN_SILENCE_DURATION = 1.0  # Minimum duration of silence for split points
```

- Adjusting this value affects how audio files are split:
  - Lower values: More split points, smaller chunks
  - Higher values: Fewer split points, larger chunks

## File System Configuration

### Directory Structure
```python
TRANSCRIPT_FOLDER = "transcripts"  # Name of transcript output folder
TEMP_PREFIX = 'audio_chunks_'      # Prefix for temporary files
```

### Output Organization
- Transcripts are stored in a "transcripts" folder next to the source audio
- Analysis files use the same base name with "_analysis.md" suffix
- Temporary files are automatically cleaned up after processing

## Logging Configuration

### Log Levels
- **DEBUG**: Detailed processing information
- **INFO**: General processing status
- **WARNING**: Potential issues that don't stop processing
- **ERROR**: Issues that prevent successful processing
- **CRITICAL**: System-level issues

### Log Format
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('audio_processor.log'),
        logging.StreamHandler()
    ]
)
```

## Performance Tuning

### Chunk Size Optimization
- Default 15MB chunks work well for most cases
- Reduce for faster processing but more API calls
- Increase for better context but slower processing

### Silence Detection
- Default 1.0s silence works well for speech
- Increase for music or continuous audio
- Decrease for quick-paced conversations

## API Integration

### Google Cloud Setup
1. Create a project in Google Cloud Console
2. Enable required APIs
3. Create service account and download key
4. Set GOOGLE_API_KEY in .env file

### Rate Limits
- Monitor API usage in Google Cloud Console
- Adjust chunk sizes if hitting rate limits
- Implement retry logic if needed

## Error Handling

### Common Issues
1. **File in Use**
   - Temporary files not cleaned up
   - Solution: Check temp directory
   
2. **API Errors**
   - Rate limits exceeded
   - Network issues
   - Solution: Check API key and quotas

3. **Processing Errors**
   - Audio format issues
   - Insufficient disk space
   - Solution: Verify prerequisites

## Advanced Configuration

### Custom Processing Pipeline
You can modify the processing pipeline by:
1. Subclassing base components
2. Implementing custom processors
3. Registering new components

### Example: Custom Chunk Size Calculator
```python
from processing.chunker import AudioChunker

class CustomChunker(AudioChunker):
    def _get_optimal_chunk_duration(self, input_file: str) -> float:
        # Custom logic here
        pass
```

## Migration Notes

### From Previous Versions
1. Update .env file with new variables
2. Review chunking settings
3. Update any custom integrations

### Breaking Changes
- New configuration structure
- Enhanced error handling
- Modified output organization