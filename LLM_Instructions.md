# LLM Instructions for Audio Processing

## Transcription Guidelines

### Input Format
- Convert all audio to WAV format before processing
- Maintain 44.1kHz sample rate
- Use 16-bit PCM encoding
- Preserve original timestamps

### Chunking Instructions
When processing audio files:
1. Detect file size before processing
2. Split files larger than 15MB
3. Use silence detection for natural breaks
4. Maintain 2-second overlap between chunks

### Processing Directives
For each audio chunk:
```
Please transcribe this audio segment.
- Provide ONLY the transcription text
- Maintain consistent speaker labels
- Preserve timing information
- Flag any unclear segments
```

## Error Response Guidelines

### Retry Logic
- Attempt up to 3 retries for failed chunks
- Use exponential backoff between attempts
- Log each retry attempt and outcome
- Preserve partial results

### Quality Verification
Look for these indicators:
1. Speaker consistency across chunks
2. Natural sentence boundaries
3. Proper punctuation
4. Timing alignment

### Success Criteria
A successful transcription must:
1. Maintain conversation flow
2. Preserve speaker changes
3. Include all audible content
4. Handle background audio appropriately

## Special Handling Cases

### Multiple Speakers
- Maintain consistent speaker labels
- Track speaker transitions
- Note overlapping speech
- Preserve conversation dynamics

### Audio Quality Issues
When encountering poor audio:
1. Flag unclear segments
2. Note potential confidence issues
3. Suggest manual review if needed
4. Document quality concerns

### Metadata Preservation
Always maintain:
1. Original timestamps
2. Speaker information
3. Audio quality markers
4. Processing history

## Version History
- 2025-01-24: Initial instruction set
- _(Add updates as implementation progresses)_