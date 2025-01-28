#!/usr/bin/env python3

import os
import shutil
from input.file_handler import AudioFileHandler

def test_file_handler():
    # Initialize handler
    handler = AudioFileHandler()
    
    # Test file path
    test_file = "Audio Test/test_files/Audio Record/Iván Vendrov.m4a"
    
    print(f"\nTesting file handler with: {test_file}")
    print("=" * 50)
    
    # Test 1: File validation
    print("\n1. Testing file validation...")
    is_valid = handler.is_valid_file(test_file)
    print(f"File is valid: {is_valid}")
    
    # Test 2: Path generation
    print("\n2. Testing path generation...")
    transcript_folder, audio_copy, wav_path, transcript_path, analysis_path = handler.get_transcript_paths(test_file)
    print(f"Transcript folder: {transcript_folder}")
    print(f"Audio copy path: {audio_copy}")
    print(f"WAV path: {wav_path}")
    print(f"Transcript path: {transcript_path}")
    print(f"Analysis path: {analysis_path}")
    
    # Test 3: File preparation
    print("\n3. Testing file preparation...")
    try:
        audio_copy_path, wav_file = handler.prepare_audio_file(test_file)
        print(f"Audio copy created: {os.path.exists(audio_copy_path)}")
        print(f"WAV file created: {os.path.exists(wav_file)}")
        
        # Test 4: Cleanup
        print("\n4. Testing cleanup...")
        handler.cleanup_processing(test_file, wav_file)
        print(f"WAV file cleaned up: {not os.path.exists(wav_file)}")
        print(f"Audio copy preserved: {os.path.exists(audio_copy_path)}")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
    
    print("\nTest complete!")

if __name__ == "__main__":
    test_file_handler()