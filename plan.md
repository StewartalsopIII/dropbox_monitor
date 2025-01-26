# Dropbox Monitor Reorganization Plan

## Overview

This plan outlines the reorganization of the Dropbox Monitor codebase into a cleaner pipeline architecture while maintaining all existing functionality. The reorganization will be performed incrementally with thorough validation at each step.

## Current Structure

```
dropbox_monitor/
├── audio_chunker.py
├── audio_monitor.py
├── debug_chunker.py
├── dropbox_monitor.py
├── speaker_diarizer.py
├── test_audio_chunker.py
├── test_speaker_diarizer.py
├── test_transcript_formatter.py
├── title_analyzer.py
└── transcript_formatter.py
```

## Target Structure

```
dropbox_monitor/
├── common/
│   ├── __init__.py
│   ├── config.py
│   └── utils.py
├── input/
│   ├── __init__.py
│   ├── file_handler.py
│   └── monitor.py
├── processing/
│   ├── __init__.py
│   ├── chunker.py
│   ├── diarizer.py
│   └── transcriber.py
├── output/
│   ├── __init__.py
│   ├── analyzer.py
│   └── formatter.py
└── tests/
    ├── __init__.py
    ├── test_input/
    ├── test_processing/
    └── test_output/
```

## Phase 1: Setup and Common Utilities
**Timeframe**: Day 1-2

### Task 1.1: Create Directory Structure
1. Create new directories while preserving existing files
2. Add __init__.py files
3. Update .gitignore for new structure
4. Create placeholder files

**Validation**:
- Directory structure matches target
- Git ignores appropriate files
- No functionality changes
- All tests pass

### Task 1.2: Extract Common Utilities
1. Create common/config.py
   - Move environment loading
   - Create shared configuration
   - Maintain backwards compatibility
2. Create common/utils.py
   - Move logging setup
   - Preserve existing log formats
3. Update imports in existing files

**Validation**:
- Environment variables load correctly
- Logging works as before
- All tests pass
- No changes to output

## Phase 2: Input Stage
**Timeframe**: Day 3-4

### Task 2.1: Create File Handler
1. Create input/file_handler.py
   - Move file system operations
   - Maintain existing file type support
   - Preserve validation checks
2. Update existing monitors to use new handler
3. Keep original files until validation complete

**Validation**:
- File detection works
- All supported formats process
- Error handling unchanged
- Tests pass

### Task 2.2: Unify Monitoring
1. Create input/monitor.py
   - Implement base monitor class
   - Preserve both monitoring strategies
   - Maintain existing event handling
2. Update main entry points

**Validation**:
- Both monitoring modes work
- Event handling unchanged
- Directory watching intact
- All tests pass

## Phase 3: Processing Stage
**Timeframe**: Day 5-6

### Task 3.1: Audio Processing
1. Create processing/chunker.py
   - Move AudioChunker class
   - Maintain chunk size logic
   - Preserve ffmpeg integration
2. Create processing/transcriber.py
   - Move transcription logic
   - Keep API integration intact
3. Create processing/diarizer.py
   - Move speaker detection
   - Preserve mapping logic

**Validation**:
- Chunking works as before
- Transcription quality unchanged
- Speaker detection accurate
- All tests pass

## Phase 4: Output Stage
**Timeframe**: Day 7-8

### Task 4.1: Output Processing
1. Create output/formatter.py
   - Move TranscriptFormatter
   - Preserve markdown formatting
2. Create output/analyzer.py
   - Move TitleAnalyzer
   - Maintain analysis pipeline

**Validation**:
- Output format unchanged
- Analysis quality maintained
- File organization preserved
- All tests pass

## Phase 5: Testing and Documentation
**Timeframe**: Day 9-10

### Task 5.1: Test Suite Organization
1. Move tests to new structure
2. Update import paths
3. Add integration tests
4. Preserve all test cases

**Validation**:
- All tests pass
- Coverage maintained
- No functionality changes

### Task 5.2: Documentation
1. Update README.md
2. Document new structure
3. Update configuration guide
4. Add migration notes

## Rollback Plan

Each phase has a specific rollback point:

1. **Before Phase 1**:
   - Full repository backup
   - Branch for each phase

2. **During Changes**:
   - Keep original files until validation
   - Use feature branches
   - Commit after each step

3. **Failure Response**:
   - Revert to last working commit
   - Restore from backup if needed
   - Document failure for future reference

## Success Criteria

- All existing functionality works exactly as before
- No changes to output format or quality
- All tests pass
- No new dependencies required
- Logging and error handling preserved
- File paths and monitoring unchanged

## Testing Procedure

1. Before each change:
   - Run full test suite
   - Process sample files
   - Save output samples

2. After each change:
   - Run tests again
   - Compare new output with samples
   - Verify logging and errors

3. Final validation:
   - Process all test files
   - Compare all outputs
   - Verify directory structure
   - Check git status

## Dependencies

- Python 3.8+
- ffmpeg
- All current pip packages
- Google Cloud credentials
- Test audio files

## Timeline

1. **Days 1-2**: Phase 1
2. **Days 3-4**: Phase 2
3. **Days 5-6**: Phase 3
4. **Days 7-8**: Phase 4
5. **Days 9-10**: Phase 5

## Notes

- No changes to core functionality
- Preserve all existing behaviors
- Keep working code unchanged
- Focus on organization only
- Document everything
- Test thoroughly
- Allow for easy rollback