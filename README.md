# 🎵 YouTube MP3 Downloader API

This is a lightweight Flask-based API that downloads the audio of a YouTube video in high-quality MP3 format using `yt-dlp` and `aria2c`. It includes cookie authentication and efficient temporary file handling.

---

## 🚀 Features

- ✅ **Fast audio download** using `aria2c` and `yt-dlp`
- ✅ **MP3 conversion** with best audio quality (`--audio-quality 0`)
- ✅ **Temporary file cleanup**
- ✅ **Cookie authentication** support (e.g., for private videos)
- ✅ **Asynchronous processing**
- ✅ **Logging to file (`server.log`)**

---

## 📦 Requirements

Make sure the following tools are installed on your system:

- Python 3.8+
- `yt-dlp`
- `aria2`
- `ffmpeg`

Install Linux packages dependencies:
```bash
apt install aria2 ffmpeg
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

## 🧪 Client

To test the server locally, you can use the following `curl` command from a terminal:

```bash
curl -L "http://localhost:8080/download?videoId=dQw4w9WgXcQ" --output rickroll.mp3