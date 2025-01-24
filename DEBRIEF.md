# Audio Processing System Issues Debrief

## Core Issues Identified

### 1. Recursive Event Triggering
**Location**: [audio_monitor.py](audio_monitor.py) and [dropbox_monitor.py](dropbox_monitor.py)
```python
def _handle_event(self, event):
    # Problem: Creates new files that trigger new events
    transcript_folder = os.path.join(file_dir, "transcripts")
```

The event handler watches for both file creation and modification, but also creates new files in a watched directory. This creates a potential infinite loop:
1. Original file processed → creates transcript files
2. New transcript files trigger new events
3. Process attempts to create more transcript folders
4. Cycle continues

### 2. Nested Folder Creation
**Evidence**: From transcript_processor.log:
```
Transcript saved to: .../transcripts/transcripts/Iván Vendrov.txt
```

The nested folder issue appears due to multiple processing attempts of the same file. This creates paths like:
- /transcripts/Iván Vendrov.txt (first attempt)
- /transcripts/transcripts/Iván Vendrov.txt (second attempt)
- And so on...

### 3. Incomplete Cleanup
**Location**: [audio_chunker.py](audio_chunker.py)
```python
def __exit__(self, exc_type, exc_val, exc_tb):
    """Context manager exit with cleanup."""
    try:
        self._cleanup_temp_dir()
    except Exception as e:
        logging.error(f"Error cleaning up temp directory: {str(e)}")
```

While cleanup is implemented, there are scenarios where temporary files might not be properly cleaned:
- Exception during processing
- Early termination
- Race conditions during multi-file processing

### 4. Race Conditions
**Location**: Both monitor files
```python
self.processing_files = set()
# ...
if file_path in self.processing_files:
    return
```

The current implementation might miss edge cases:
- Different path representations for the same file
- Nested paths not being caught
- Concurrent processing attempts

## Recommended Fixes

1. **Event Handler Modification**
   - Add path filtering to ignore events in transcript folders
   - Use absolute paths for comparison
   - Implement proper event debouncing

2. **Folder Structure**
   - Use a single, flat transcript folder structure
   - Implement proper path normalization
   - Add validation to prevent nested folder creation

3. **Cleanup Process**
   - Add cleanup on start to remove stale temporary files
   - Implement proper error recovery
   - Add periodic cleanup checks

4. **Process Management**
   - Implement proper file locking
   - Add timeout mechanisms
   - Improve path comparison logic

## Implementation Priority

1. **Critical**
   - Fix event recursion issue
   - Prevent nested folder creation
   - Implement proper path filtering

2. **High**
   - Improve cleanup mechanisms
   - Add proper file locking
   - Implement timeout handling

3. **Medium**
   - Add monitoring safeguards
   - Improve error recovery
   - Enhance logging

## Next Steps

1. Modify the event handlers to properly filter paths
2. Implement proper cleanup mechanisms
3. Add safeguards against recursion
4. Test with various file sizes and conditions

## Testing Notes

Current issues have been observed with:
- Large files (>20MB)
- Multiple concurrent uploads
- Interrupted processing
- Network timeouts

## Additional Considerations

1. **Monitoring**
   - Add process monitoring
   - Implement health checks
   - Add automated cleanup jobs

2. **Recovery**
   - Add process recovery mechanisms
   - Implement partial file cleanup
   - Add transaction-like processing

3. **Logging**
   - Enhanced error logging
   - Process tracking
   - Performance metrics

This debrief is based on code analysis as of January 24, 2025. Please update the document as new issues are discovered or fixes are implemented.