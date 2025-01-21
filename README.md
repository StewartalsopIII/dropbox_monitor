# 🎙️ Dropbox Audio Processing Suite

This repository contains two powerful audio processing systems that automatically transcribe and analyze audio files:

## 🔄 Systems Overview

### 1. 📞 Zoom Recording Monitor (dropbox_monitor.py)
- 🎯 **Purpose**: Automatically processes Zoom recording files
- 📁 **Watches**: Specific Zoom recordings folder
- 🎤 **Format**: Handles .m4a files from Zoom
- 📝 **Output**: Transcripts and content analysis

### 2. 🎵 General Audio Monitor (audio_monitor.py)
- 🎯 **Purpose**: Processes any supported audio file
- 🎨 **Formats**: Supports .wav, .mp3, .m4a
- 📁 **Structure**: Creates transcripts alongside original files
- 🤖 **AI-Powered**: Uses Google's Gemini Pro for transcription

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

3. Create a .env file with your Google API key:
```
GOOGLE_API_KEY=your_key_here
```

## 🛠️ Usage

### Zoom Recording Monitor
```bash
python dropbox_monitor.py
```
- Monitors Zoom recordings folder
- Creates organized transcript folders
- Generates analysis documents

### General Audio Monitor
```bash
python audio_monitor.py
```
- Drop any audio file (.wav, .mp3, .m4a) into the watched folder
- Creates a "transcripts" folder next to your audio
- Generates both transcript and analysis

## 📁 File Structure

### Zoom Monitor Output
```
Zoom Folder/
└── Meeting_Name/
    ├── Audio Record/
    │   └── recording.m4a
    └── transcript/
        ├── recording.m4a
        ├── recording.txt
        └── recording_analysis.md
```

### Audio Monitor Output
```
Audio Files/
├── my_audio.mp3
└── transcripts/
    ├── my_audio.txt
    └── my_audio_analysis.md
```

## 🤖 Features

### Transcription
- 📝 Full audio transcription
- 🎯 High accuracy with Gemini Pro
- 📊 Handles files up to 20MB

### Analysis
- 🎨 Speaking style analysis
- 🔍 Key themes identification
- 💡 Title suggestions
- 📊 Content breakdown

## 📝 Logs
- 📊 Detailed processing logs
- ⏱️ Timestamps for all operations
- 🚫 Error tracking and reporting
- 📈 File size and processing metrics

## ⚙️ Configuration
Both systems use:
- 🔑 Environment variables for API keys
- 📁 Configurable watch folders
- 🎚️ Customizable file handling
- 📊 Adjustable logging levels

## 🚨 Common Issues

### File Size Limits
- Maximum file size: 20MB
- For larger files, consider splitting audio

### Processing Time
- Varies with file size
- Network speed dependent
- Progress shown in logs

## 🤝 Contributing
Feel free to:
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests

## 📜 License
MIT License - feel free to use and modify!