# 🎙️ Dropbox Audio Processing Suite

This repository contains a modular audio processing system that automatically transcribes and analyzes audio files.

## 🔄 Systems Overview

### Core Components
The system is organized into modular components:

- 📥 **Input**: File monitoring and handling
  - Watches folders for new audio files
  - Supports both Zoom recordings and general audio
  - Handles file validation and preprocessing

- 🔄 **Processing**: Audio analysis pipeline
  - Chunks large audio files
  - Manages transcription
  - Handles speaker diarization

- 📤 **Output**: Results formatting
  - Generates formatted transcripts
  - Creates content analysis
  - Organizes output files

### Monitor Types

1. 📞 **Zoom Recording Monitor**
   - Automatically processes Zoom recordings
   - Handles .m4a files from Zoom
   - Creates organized transcript folders

2. 🎵 **General Audio Monitor**
   - Processes any supported audio file (.wav, .mp3, .m4a)
   - Creates transcripts alongside original files
   - Uses Google's Gemini Pro for transcription

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- ffmpeg installed on your system
- Google API key for Gemini Pro

### Installation
1. Clone the repository:
```bash
git clone https://github.com/StewartalsopIII/dropbox_monitor.git
cd dropbox_monitor
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

3. Configure your environment:
   - Copy .env.example to .env
   - Add your Google API key
   - Customize watch folders if needed

## 📁 Project Structure

```
dropbox_monitor/
├── common/          # Shared utilities
│   ├── config.py    # Configuration management
│   └── utils.py     # Common helper functions
├── input/           # Input handling
│   ├── file_handler.py
│   └── monitor.py
├── processing/      # Audio processing
│   ├── chunker.py
│   ├── diarizer.py
│   └── transcriber.py
├── output/          # Result formatting
│   ├── analyzer.py
│   └── formatter.py
└── tests/           # Test suite
```

## 🛠️ Usage

### Command Line Interface
```bash
# For Zoom recordings
python -m input.monitor --mode=zoom --path=/path/to/zoom/folder

# For general audio files
python -m input.monitor --mode=audio --path=/path/to/audio/folder
```

### Output Structure

```
Watched Folder/
└── Meeting_Name/
    ├── Audio/
    │   └── recording.m4a
    └── Transcript/
        ├── recording.md
        └── analysis.md
```

## 🤖 Features

### Transcription
- 📝 Full audio transcription
- 🎯 High accuracy with Gemini Pro
- 📊 Handles files up to 20MB
- 🔄 Automatic chunking for large files

### Analysis
- 🎨 Speaking style analysis
- 🔍 Key themes identification
- 💡 Title suggestions
- 📊 Content breakdown

## ⚙️ Configuration

### Environment Variables
```bash
# Required
GOOGLE_API_KEY=your_api_key

# Optional
WATCH_FOLDER_ZOOM=/path/to/zoom/folder
WATCH_FOLDER_AUDIO=/path/to/audio/folder
MAX_CHUNK_SIZE_MB=15
MIN_SILENCE_DURATION=1.0
```

### Customization
- 🔧 See common/config.py for all options
- 📝 Logging configuration in common/utils.py
- 🎚️ Processing parameters in processing/chunker.py

## 🚨 Common Issues

### File Size Limits
- Maximum file size: 20MB
- Automatic chunking for larger files
- Configurable chunk sizes

### Processing Time
- Varies with file size
- Network speed dependent
- Progress shown in logs

### Common Errors
- "File in use": Wait for file to be fully written
- "API rate limit": Automatic retries implemented
- "Transcription failed": Check chunk sizes

## 🔄 Migration Guide

### From Previous Versions
1. Back up your existing configuration
2. Update your import statements if using as a library
3. Review new configuration options
4. Test with existing watch folders

### Breaking Changes
- New module structure requires updated imports
- Configuration now in common/config.py
- Enhanced error handling may change some behaviors

## 🤝 Contributing
- 📝 See CONTRIBUTING.md for guidelines
- 🐛 Report bugs via Issues
- 💡 Feature requests welcome
- 🧪 Run tests with pytest

## 📜 License
MIT License - feel free to use and modify!