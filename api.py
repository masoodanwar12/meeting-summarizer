from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import subprocess
from transcriber import transcribe_audio
from summarizer import summarize_transcript
from tts import summary_to_audio

app = FastAPI(title="Meeting Summarizer API")

# ── Allow frontend to connect ──────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def convert_to_wav(input_path: str) -> str:
    """Convert any audio format to WAV using ffmpeg"""
    if input_path.endswith(".wav"):
        return input_path
    wav_path = input_path.rsplit(".", 1)[0] + ".wav"
    subprocess.run([
        "ffmpeg", "-i", input_path, wav_path, "-y"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return wav_path

# ── Route 1: Health check ──────────────────────────────────────
@app.get("/")
def home():
    return {"status": "Meeting Summarizer API is running!"}

# ── Route 2: Summarize audio ───────────────────────────────────
@app.post("/summarize")
async def summarize(file: UploadFile = File(...), tts: bool = False):

    # Save uploaded audio
    audio_path = f"uploaded_{file.filename}"
    with open(audio_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Convert to WAV if needed (m4a, mp3, etc)
    wav_path = convert_to_wav(audio_path)

    # Transcribe
    transcript = transcribe_audio(wav_path, model_size="base")
    if not transcript.strip():
        return JSONResponse({"error": "Transcript is empty"}, status_code=400)

    # Summarize
    summary = summarize_transcript(transcript)

    # TTS (optional)
    audio_url = None
    if tts:
        summary_to_audio(
            text=summary["summary"],
            output_path="meeting_summary.wav",
            lang="en",
            speaker_wav=wav_path,
        )
        audio_url = "/download/meeting_summary.wav"

    # Cleanup uploaded files
    os.remove(audio_path)
    if wav_path != audio_path and os.path.exists(wav_path):
        os.remove(wav_path)

    return {
        "transcript": transcript,
        "summary": summary["raw"],
        "audio_url": audio_url
    }

# ── Route 3: Download audio ────────────────────────────────────
@app.get("/download/{filename}")
def download(filename: str):
    if os.path.exists(filename):
        return FileResponse(filename, media_type="audio/wav")
    return JSONResponse({"error": "File not found"}, status_code=404)