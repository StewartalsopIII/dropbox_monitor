# Audio Processing Enhancement Plan

## Task 1: Convert Transcripts to Markdown Format
**Purpose**: Switch transcript output from .txt to .md format for better readability and formatting
**Steps**:
1. Update file extension handling:
   - Modify transcript_path creation in both monitor scripts
   - Change `.txt` extension to `.md`
   - Update relevant logging messages
2. Add markdown formatting:
   - Add metadata header section (timestamp, speakers, etc.)
   - Format speaker lines with markdown syntax
   - Handle emphasis and formatting markers

**Validation Criteria**:
- [ ] All new transcripts save as .md files
- [ ] Markdown formatting preserved in output
- [ ] Existing functionality remains intact
- [ ] Logging correctly reflects new file type

## Task 2: Implement Google Cloud Speaker Diarization
**Purpose**: Add speaker identification using Google Cloud Speech-to-Text API
**Steps**:
1. Set Up Google Cloud:
   - Create Google Cloud project 
   - Enable Speech-to-Text API
   - Set up authentication credentials
   - Install google-cloud-speech package

2. Create AudioDiarizer class:
   - Initialize with Google credentials
   - Implement long-running audio processing
   - Handle speaker diarization results
   - Add retry and error handling

3. Speaker Recognition Flow:
   - Upload audio to Google Cloud Storage
   - Configure diarization parameters
   - Process audio for speaker recognition
   - Parse diarization results
   - Map speaker labels to timestamps
   - Store speaker metadata

4. Integrate with AudioChunker:
   - Process audio before chunking
   - Associate speaker data with chunks
   - Update transcript formatting
   - Add speaker labels to output

**Validation Criteria**:
- [ ] Successful Google Cloud API integration
- [ ] Accurate speaker differentiation
- [ ] Proper timestamp alignment
- [ ] Clean speaker label formatting
- [ ] Error handling for API limits

## Testing Plan
1. Test different audio scenarios:
   - Various file sizes
   - Multiple speakers
   - Different introduction formats
   - Various recording qualities

2. Verify integration points:
   - Diarization accuracy
   - Chunking boundaries
   - Speaker consistency
   - Timing alignment

## Task 3: Fix Chunk Size Management
**Purpose**: Ensure consistent and properly sized chunks during audio splitting
**Steps**:
1. Revise silence point selection:
   - Calculate expected chunk sizes before splitting
   - Filter silence points to maintain max chunk size
   - Implement backup splitting if silence points create oversized chunks
   - Add size validation checks

2. Improve size estimation:
   - Create accurate audio duration to file size mapping
   - Calculate WAV file size based on audio parameters
   - Implement proper chunk size prediction
   - Add safety margin to prevent oversized chunks

3. Add validation layer:
   - Verify chunk sizes after splitting
   - Implement re-splitting for oversized chunks
   - Add logging for chunk size validation
   - Create size distribution metrics

**Validation Criteria**:
- [ ] All chunks maintain size under 15MB
- [ ] Chunks split at natural silence points when possible
- [ ] Accurate size prediction before splitting
- [ ] Detailed logging of chunk size distribution

## Success Metrics
1. Accurate speaker identification
2. Consistent markdown formatting
3. Clean file management
4. Preserved audio quality
5. Accurate progress reporting

## Implementation Notes
- Use pyannote.audio for diarization
- Maintain original audio quality
- Preserve all metadata
- Handle error cases gracefully

## Next Steps
1. Implement markdown conversion
2. Create AudioDiarizer class
3. Integrate with existing chunking
4. Add comprehensive testing