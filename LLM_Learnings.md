# LLM Implementation Learnings

## Audio Processing Insights

### File Size Management
- Gemini Pro has a 20MB file size limit
- Optimal chunk size is 15MB to allow overhead
- Natural speech breaks provide best chunking points

### API Behavior
- Response format is consistent for pure transcription
- Context window handles ~30 minutes of transcribed text
- Rate limits are per-minute, not per-request

### Quality Considerations
- Silence detection improves chunk boundaries
- Speaker transitions make good split points
- Metadata preservation is crucial for reassembly

## Design Decisions

### Why 15MB Chunks?
1. Provides 5MB safety margin under 20MB limit
2. Large enough for meaningful context
3. Small enough for quick processing
4. Handles typical 5-10 minutes of audio

### Chunking Strategy Choice
1. Using ffmpeg silence detection because:
   - Maintains conversation context
   - Avoids mid-word splits
   - Preserves audio quality
   - Industry-standard tool

### File Management Approach
1. Temporary files in dedicated folder
2. Cleanup after successful processing
3. Unique identifiers for parallel processing
4. Original file backup preserved

## Best Practices Discovered

### Audio Processing
- Always verify file integrity before chunking
- Use consistent audio format for chunks
- Maintain original quality settings
- Log chunk boundaries for debugging

### Transcription Quality
- Include overlap between chunks
- Verify speaker consistency
- Track timing information
- Validate reassembly points

### Error Handling
- Retry logic for API failures
- Partial results preservation
- Detailed error logging
- Recovery procedures

## Ongoing Observations

### Event Monitoring Insights
When using watchdog for file system monitoring, we discovered several critical insights about recursive monitoring:

1. The recursive flag in observer.schedule(event_handler, path, recursive=True) can cause infinite processing loops when:
   - The monitored directory contains subdirectories that are modified by the same process
   - New files are created in watched directories as part of the processing
   - The process creates new directories within the watched path

2. Practical Impact:
   - Creating transcript folders within the watched directory triggered new events
   - These events caused new processing attempts
   - Each attempt created nested "transcripts" folders
   - Led to paths like "transcripts/transcripts/file.txt"

3. Solution:
   - Removed recursive=True flag from observer.schedule()
   - This prevents monitoring of subdirectories
   - Processing now happens only in the root directory
   - Eliminates the infinite loop of event handling

4. Lessons Learned:
   - Always carefully consider the scope of file system monitoring
   - Be cautious with recursive monitoring when the process modifies the watched directory
   - Use absolute paths and proper path filtering
   - Implement clear boundaries between watched and output directories

These insights have significantly improved the stability and reliability of our audio processing system by preventing recursive processing loops and nested folder creation.

_(Add new learnings as we implement and test)_

## Transcription API Migration (2025-01-26)

### Initial Implementation Issue
1. Started with Google's Gemini API for transcription
   - Wrong tool for the job
   - Gemini is for generative AI, not speech-to-text
   - Would have led to unreliable transcriptions

### Migration to Speech-to-Text
1. Changed to Google Cloud Speech-to-Text
   - Proper API for audio transcription
   - Built-in speaker diarization support
   - Better handling of audio formats
   - More accurate for long-form content

2. Code Architecture Improvements
   - Separated speaker detection from transcription
   - Created dedicated speaker_diarizer.py
   - Pattern-based speaker identification remains useful
   - Maintained clean separation of concerns

3. Dependency Management
   - Removed google-generativeai dependency
   - Added google-cloud-speech
   - No changes needed to ffmpeg requirements
   - Virtual environment setup preserved

4. API Differences
   - Gemini used simple file upload
   - Speech-to-Text requires proper audio configs
   - Speaker diarization is built into API
   - Better chunk handling for large files

### Key Design Decisions
1. Why separate speaker_diarizer.py?
   - Works with both Speech-to-Text and text-based detection
   - Can enhance API's speaker detection
   - Maintains consistent speaker mapping
   - Easy to test independently

2. Audio Processing Strategy
   - Keep chunking for large files
   - Use API's native speaker detection
   - Fall back to pattern matching when needed
   - Preserve timing information

3. Error Handling
   - Better type validation
   - Specific error messages for credential issues
   - Clear logging of transcription status
   - Proper cleanup of temporary files

### Next Steps
1. Google Cloud Setup
   - Project creation
   - API enablement
   - Service account configuration
   - Local credential management

2. Testing Needed
   - Various audio formats
   - Different speaker scenarios
   - Large file handling
   - Error conditions

## Failed Migration to pyannote.audio (2025-01-25)

### What We Tried
1. Attempted to migrate from Vosk to pyannote.audio for speaker diarization
2. Updated code infrastructure with new package dependencies
3. Aimed to improve speaker identification accuracy

### Why It Failed
1. Dependencies Management Issues:
   - Failed to properly handle virtual environment setup
   - Torch installation complications on Apple Silicon
   - Complex dependency chain (torch -> pyannote.audio)
   - Didn't properly test environment setup before code changes

2. Migration Strategy Problems:
   - Replaced working code before validating new solution
   - Broke existing functionality without fallback plan
   - Didn't do staged rollout (keeping old code while testing new)
   - Failed to verify package compatibilities up front

3. Implementation Issues:
   - Didn't account for Apple Silicon-specific requirements
   - Assumed pip availability without checking environment
   - Made too many changes at once instead of incremental updates

### Lessons Learned
1. Environment First:
   - Always verify environment setup before code changes
   - Test package installations in isolation
   - Document specific environment requirements
   - Create test environment before production changes

2. Migration Best Practices:
   - Keep old implementation while testing new one
   - Use feature flags to switch between implementations
   - Test new code in parallel with old system
   - Plan rollback strategy before making changes

3. Platform Specifics:
   - Consider platform-specific package requirements (M1/M2)
   - Test on target architecture before deployment
   - Document platform-specific setup steps
   - Maintain separate requirements for different platforms

### Next Steps
1. Properly set up virtual environment first
2. Test torch installation for Apple Silicon
3. Validate pyannote.audio installation in isolation
4. Create parallel implementation without removing Vosk
5. Add feature flag to switch between implementations
6. Test both systems before final migration

## VOSK Implementation Failures (2025-01-24/25)

### Initial Attempts
1. Tried direct VOSK implementation:
   ```
   2025-01-25 13:31:38,402 - Starting monitoring of: /Users/.../Audio Test
   2025-01-25 13:31:38,403 - Waiting for new audio files...
   2025-01-25 13:31:38,677 - An error occurred: Vosk model not found. Please set VOSK_MODEL_PATH environment variable or provide model_path in constructor.
   ```
   - Even with model path set in .env
   - Even with model downloaded and extracted

2. Speaker Identification Issues:
   - Test file "Iván Vendrov.m4a" (89.21 MB) split into 36 chunks
   - Failed to identify speakers correctly
   - Default to "SPEAKER_0" and "SPEAKER_1" without proper mapping
   - Evidence in log:
   ```
   2025-01-24 18:36:39,110 - DEBUG - File duration: 3245.80s, MB/second: 0.0275
   2025-01-24 18:36:41,376 - DEBUG - Found 35 silence points
   2025-01-24 18:38:05,247 - DEBUG - Total size of chunks: 273.02 MB (Original: 89.21 MB)
   ```

3. Chunk Size Management Issues:
   - Original file inflated from 89.21 MB to 273.02 MB
   - Caused by WAV conversion and improper chunk management
   - Led to chunking strategy optimization attempts:
   ```
   2025-01-24 19:44:44,883 - Waiting for new audio files...
   2025-01-24 19:45:00,498 - Performing speaker diarization...
   2025-01-24 19:47:47,275 - Identified speakers: {'SPEAKER_0': 'Stewart Alsop', 'SPEAKER_1': 'Guest Speaker SPEAKER_1'}
   ```

### Discovered VOSK Limitations
1. Model Dependency Issues:
   - Required large model downloads
   - Inconsistent model path handling
   - Environment variable setup problems
   - Model quality vs. file size tradeoffs

2. Speaker Diarization Quality:
   - Poor speaker segmentation
   - Limited to binary speaker identification
   - No support for overlapping speech
   - Inconsistent results across different audio qualities

3. Resource Management:
   - Memory leaks in long-running processes
   - File size inflation during processing
   - Poor handling of large audio files
   - Inefficient chunk processing

### VOSK vs. pyannote.audio Tradeoffs
| Feature | VOSK | pyannote.audio |
|---------|------|----------------|
| Setup Complexity | Lower | Higher |
| Model Size | Smaller | Larger |
| Accuracy | Lower | Higher |
| Resource Usage | Lower | Higher |
| Speaker Count | Limited | Flexible |
| Platform Support | Better | Mixed |
| Documentation | Limited | Better |
| Commercial Use | Free | Licensed |

### Key Insights for Future Development
1. Model Management:
   - Need better model version control
   - Automated model download and setup
   - Platform-specific model paths
   - Fallback options for model failures

2. Audio Processing:
   - Implement proper WAV conversion strategy
   - Better chunk size management
   - Handle various audio formats properly
   - Maintain quality during processing

3. Error Handling:
   - Better error messages for setup issues
   - Graceful fallbacks for diarization failures
   - Handle environment misconfiguration
   - Provide clear setup instructions

## Audio Chunk Size Management (2025-01-24)

### Chunk Size Optimization Insights
1. Codec preservation is crucial:
   - Using `-c copy` in ffmpeg maintains original file size
   - Converting to uncompressed PCM (WAV) causes ~3x size inflation
   - Original codecs (like M4A) provide better size efficiency

2. Size estimation strategy:
   - Calculate bytes_per_second from original file
   - Use this ratio to predict chunk sizes before splitting
   - Target middle of allowed range (10-15MB) for optimal splits
   - Account for potential codec variations

3. Split point selection approach:
   - Create evenly spaced target points based on desired chunk size
   - Find closest silence points to these targets
   - Validate each potential split for size constraints
   - Handle edge cases (too small/large chunks) with merging

4. Key metrics discovered:
   - M4A files: ~0.0275 MB/second at standard quality
   - Optimal chunk duration: ~436 seconds for 12MB target
   - Natural silence points every 2-3 minutes
   - Size prediction accuracy within 2-3%

5. Validation improvements:
   - Log detailed size metrics for each chunk
   - Track both duration and size ratios
   - Verify total output size matches input
   - Monitor size distribution across chunks

These insights led to a more robust chunking system that:
- Maintains minimum chunk size (10MB)
- Generally stays under maximum (15MB)
- Preserves audio quality
- Uses natural break points
- Keeps original compression

## Transcript Formatting Implementation (2025-01-24)

### TranscriptFormatter Class Decision
We decided to create a dedicated TranscriptFormatter class because:
1. Separation of concerns - isolates formatting logic from file processing
2. Improves testability of formatting features
3. Makes future format changes more manageable
4. Can be reused across different monitoring scripts
5. Maintains clean, consistent formatting across all transcripts

### Implementation Progress (2025-01-24)
1. Created TranscriptFormatter class with comprehensive unit tests
2. Successfully integrated formatter into both monitor scripts
3. Enhanced metadata handling:
   - Audio monitor includes: file info, size, timestamp
   - Dropbox monitor adds: meeting name, file info, size, timestamp
4. Changed transcript extension from .txt to .md
5. Maintained backward compatibility with existing components

### Key Learnings from Task 1 Implementation
1. Breaking the formatter into a separate class proved valuable for:
   - Clean code organization
   - Easy testing of formatting logic
   - Simple integration into both monitor scripts
   
2. Testing before integration helped catch issues early:
   - Unit tests verified all formatting scenarios
   - Ensured consistent markdown output
   - Validated metadata handling
   
3. Maintaining existing functionality while adding new features:
   - Kept original audio processing intact
   - Only changed file extension and output format
   - Preserved all logging and error handling
   
4. Metadata handling improvements:
   - Different metadata for each monitor type
   - Consistent formatting across all outputs
   - Enhanced transcript searchability and organization

   ## Google Cloud Speech-to-Text Implementation (2025-01-26)

### Setup Process Completed
1. Created Google Cloud Project for audio transcription
2. Enabled Speech-to-Text API
3. Created service account with Cloud Speech Client role
4. Downloaded and securely stored credentials
5. Configured environment with GOOGLE_APPLICATION_CREDENTIALS

### Key Configuration Details
- Service Account: dropbox-audio-transcription
- Role: Cloud Speech Client (minimal permissions)
- Credentials stored in: ./credentials/service-account.json
- Environment variable set in .env file

### Best Practices Implemented
1. Secure credential storage:
   - Credentials in separate directory
   - Added to .gitignore
   - Using relative paths
2. Minimal permissions:
   - Used Cloud Speech Client role
   - Avoided administrator access
3. Environment Configuration:
   - Used existing .env file
   - Maintained separation of concerns

### Next Steps
1. Test transcription with sample audio
2. Implement error handling
3. Add retry logic for API calls
4. Update documentation

## Speaker Diarization Challenges (2025-01-26)

### Implementation Issues Discovered
1. Name Extraction Patterns:
   - Introduction patterns ("Hi, I'm [name]") are too rigid
   - Not all conversations have clear introductions
   - Names may be mentioned contextually rather than formally
   - Need more flexible pattern matching

2. Formatting Interference:
   - Markdown formatting (e.g., `****Stewart Alsop**`) breaks pattern matching
   - Text processing should handle various formatting artifacts
   - Need to strip formatting before pattern matching
   - Consider standardizing format before processing

3. Context Management:
   - Speaker identification lost between audio chunks
   - Context not properly maintained across file splits
   - Need better state management between chunks
   - Consider persistent speaker mapping across session

4. Configuration Limitations:
   - Pre-configured speaker lists too restrictive
   - Current approach only works for known host
   - Need dynamic speaker discovery
   - Consider machine learning for speaker identification

5. Technical Limitations:
   - Pure text-based approach insufficient
   - Missing audio-based voice differentiation
   - No way to handle overlapping speakers
   - Limited to sequential speaker identification

### Future Improvements
1. Pattern Matching:
   - Implement fuzzy matching for names
   - Add contextual name extraction
   - Support multiple name formats
   - Handle informal introductions

2. Context Handling:
   - Implement persistent speaker context
   - Add cross-chunk reference system
   - Maintain speaker history
   - Support session-level speaker mapping

3. Format Processing:
   - Add pre-processing for markdown cleanup
   - Standardize text format before analysis
   - Handle various text encodings
   - Add format-specific handlers

4. Speaker Management:
   - Implement dynamic speaker discovery
   - Add speaker verification system
   - Support unknown speaker handling
   - Allow manual speaker mapping correction

5. Audio Integration:
   - Consider hybrid text/audio approach
   - Add basic voice fingerprinting
   - Support speaker overlap detection
   - Implement voice-based verification

### Key Insights
1. Text-only diarization is insufficient for robust speaker identification
2. Need balance between pattern rigidity and flexibility
3. Context management crucial for accurate speaker tracking
4. Pre-configuration limits real-world usability
5. Format handling needs to be more robust

These learnings suggest moving towards a hybrid approach combining:
- Audio-based speaker differentiation
- Text-based name extraction
- Context-aware speaker tracking
- Flexible pattern matching
- Robust format handling