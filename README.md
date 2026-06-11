# NeuroFM

![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)
![Radio](https://img.shields.io/badge/project-radio%20streaming-purple)
![AI Generated](https://img.shields.io/badge/code-AI%20assisted-lightgrey)

NeuroFM is a self-hosted Python radio automation system with a live Icecast stream and a web dashboard. It automatically plays music, injects voice segments, handles scheduled news breaks, and exposes a real-time “Now Playing” interface.

---

# ✨ Features

* 24/7 automated radio streaming
* Icecast integration (MP3 streaming via FFmpeg)
* Day / Night mode switching (normal & chill playlists)
* Automatic shuffled music queue
* TTS / voice segment injection between songs
* Scheduled news playback
* Live web dashboard (Flask)
* Real-time “Now Playing” state system (`status.json`)
* Simple browser-based player UI

---

# 🧠 System Overview

NeuroFM runs two main components:

### 🎧 radio.py

* Handles audio playback
* Streams audio to Icecast using FFmpeg
* Manages playlists, queue system, TTS, and news
* Updates `status.json` for live state tracking

### 🌐 dashboard.py

* Flask web server
* Displays live stream player
* Shows current song / mode
* Highlights schedule (07:00–19:00 / 19:00–07:00)
* Streams audio via proxy endpoint

---

## 📁 Project Structure

```text
neurofm/
├── radio.py
├── dashboard.py
├── config.json (not uploaded)
├── config.example.json
├── requirements.txt
├── LICENSE
├── README.md
├── status.json
│
├── music/
├── chill_music/
├── neuro_tts/
│
└── assets/
```

---

# ⚙️ Installation

## 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## 2. Install FFmpeg

NeuroFM requires FFmpeg for audio processing.

Download:
[https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

Make sure it is available in your system PATH.

---

## 3. Install & setup Icecast

NeuroFM streams audio to an Icecast server.

Example configuration:

* Host: `localhost:8000`
* Mount: `/neurofm`
* Username: `source`
* Password: set in config.json

---

# ⚙️ Configuration

Copy the example config:

config.example.json → config.json

Then edit:

```json
{
  "icecast": {
    "host": "localhost:8000",
    "username": "source",
    "password": "your_password_here",
    "mount": "/neurofm"
  },
  "folders": {
    "normal_music": "music",
    "chill_music": "chill_music",
    "tts": "neuro_tts"
  },
  "news": {
    "enabled": true,
    "url": "https://video.news.sky.com/snr/news/snrnews.mp3",
    "minute": 30
  }
}
```

---

# 🚀 Running the system

## Start radio engine

```bash
python radio.py
```

## Start dashboard

```bash
python dashboard.py
```

Then open:

```
http://127.0.0.1:5000
```

---

# 📊 Dashboard Features

The web UI shows:

* 🎵 Live “Now Playing”
* 🎧 Stream player
* 🌙 Schedule highlight system
* 📡 Live audio stream via `/neurofm`

Schedule:

* 07:00 – 19:00 → Main Music
* 19:00 – 07:00 → Chill Mode

---

# 📡 State System

NeuroFM writes live data to:

```
status.json
```

Example:

```json
{
  "mode": "normal",
  "artist": "Billie Eilish",
  "title": "CHIHIRO",
  "file": "Billie Eilish - CHIHIRO.mp3"
}
```

This can be used for:

* OBS overlays
* custom dashboards
* external integrations

---

# 🎵 Supported Audio Formats

* .mp3
* .wav
* .ogg

---

# ⚠️ Requirements

* Python 3.9+
* FFmpeg installed
* Icecast server running
* Proper folder setup for music and TTS files

---

# 📌 Notes

* This is a self-hosted streaming system
* Do not expose Icecast credentials publicly
* Designed for continuous 24/7 operation
* Dashboard and radio engine must run together for full functionality

---

# 📜 License

This project is licensed under the MIT License.

