# 🎙️ Meeting Summarizer

> Record or upload a meeting → get a transcript, AI summary, and the summary read back in your own cloned voice.

---

## ✨ Features

- 🎤 **Record audio** directly in the browser or upload a file (`.wav`, `.mp3`, `.m4a`, `.ogg`, `.webm`)
- 📝 **Transcription** using OpenAI Whisper (runs locally)
- 🤖 **AI Summary** via Groq — key points and action items extracted automatically
- 🔊 **Voice Cloning** using XTTS v2 — summary is spoken back in your own voice
- ⚡ Clean dark UI, no login required

---

## 🗂️ Project Structure

```
meeting/
├── api.py            # FastAPI backend
├── transcriber.py    # Whisper transcription
├── summarizer.py     # Groq summarization
├── tts.py            # XTTS voice cloning
├── main.py           # Entry point
├── recorder.py       # Audio recording helper
├── requirements.txt  # Python dependencies
├── .env              # API keys (not committed)
├── templates/
│   └── index.html    # Frontend UI
├── static/           # Static assets
└── README.md
```

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
pip install fastapi uvicorn python-multipart openai-whisper TTS torch groq
```

Also install **ffmpeg** on your system:

- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org) and add to PATH
- **macOS**: `brew install ffmpeg`
- **Ubuntu**: `sudo apt install ffmpeg`

### 2. Set your Groq API key

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_key_here
```

Or set it manually:

```bash
# Windows
set GROQ_API_KEY=your_key_here

# macOS/Linux
export GROQ_API_KEY=your_key_here
```

Get a free key at [console.groq.com](https://console.groq.com)

### 3. Start the API server

```bash
uvicorn api:app --reload
```

Server runs at `http://127.0.0.1:8000`

### 4. Open the frontend

Open your browser and go to:

```
http://127.0.0.1:8000
```

---

## 🔄 How It Works

```
Audio Input
    │
    ▼
Whisper (transcription)
    │
    ▼
Groq LLM (summarization)
    │
    ▼
XTTS v2 (voice cloning)
    │
    ▼
Playback in browser
```

---

## ⚙️ API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves frontend UI |
| `GET` | `/health` | Health check |
| `POST` | `/summarize?tts=true` | Upload audio, get transcript + summary + audio |
| `GET` | `/download/{filename}` | Download generated audio |

---

## 💡 Notes

- First run downloads the XTTS v2 model (~2GB) — this takes a few minutes
- Whisper runs on CPU by default (FP32 mode) — transcription may take 30–60s for long recordings
- Keep the terminal running while using the app
- Voice cloning works best with at least 6 seconds of clear speech

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, Vanilla JS |
| Backend | FastAPI (Python) |
| Transcription | OpenAI Whisper |
| Summarization | Groq (LLaMA) |
| Voice Cloning | Coqui XTTS v2 |
| Audio | ffmpeg |