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
- Using natural break points improves transcription quality
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
- Track timing information
- Validate reassembly points

### Error Handling
- Retry logic for API failures
- Partial results preservation
- Detailed error logging
- Recovery procedures

## Event Monitoring Insights
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