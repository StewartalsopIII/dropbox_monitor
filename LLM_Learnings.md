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
_(Add new learnings as we implement and test)_