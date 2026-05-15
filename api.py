from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import subprocess
import threading
import webbrowser
import uvicorn

from transcriber import transcribe_audio
from summarizer import summarize_transcript
from tts import summary_to_audio

app = FastAPI(title="Meeting Summarizer API")

# ── Serve templates and static folders ────────────────────────
templates = Jinja2Templates(directory="templates")

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Route 1: Serve HTML frontend ──────────────────────────────
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ── Route 2: Health check ─────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "Meeting Summarizer API is running!"}


# ── Route 3: Favicon (suppress 404) ──────────────────────────
@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)


# ── Helper: Convert audio to WAV ──────────────────────────────
def convert_to_wav(input_path: str) -> str:
    if input_path.endswith(".wav"):
        return input_path
    wav_path = input_path.rsplit(".", 1)[0] + ".wav"
    result = subprocess.run(
        ["ffmpeg", "-i", input_path, wav_path, "-y"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg conversion failed: {result.stderr.decode()}")
    print(f"✅ Converted to WAV: {wav_path}")
    return wav_path


# ── Route 4: Summarize audio ──────────────────────────────────
@app.post("/summarize")
async def summarize(file: UploadFile = File(...), tts: bool = False):

    # Fix filename: remove spaces and special characters
    safe_filename = file.filename.replace(" ", "_").replace("(", "").replace(")", "")
    audio_path = f"uploaded_{safe_filename}"
    wav_path = None

    try:
        # Step 1: Save uploaded file
        with open(audio_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        print(f"💾 Saved uploaded file: {audio_path}")

        # Step 2: Convert to WAV if needed
        wav_path = convert_to_wav(audio_path)

        # Step 3: Transcribe
        transcript = transcribe_audio(wav_path, model_size="base")
        print(f"📋 Transcript length: {len(transcript)} chars")
        print(f"📋 Transcript preview: {repr(transcript[:200])}")

        if not transcript.strip():
            return JSONResponse(
                {"error": "Transcript is empty. Please record clearer audio."},
                status_code=400
            )

        # Step 4: Summarize
        summary = summarize_transcript(transcript)

        # Step 5: TTS — BEFORE cleanup so speaker_wav still exists
        audio_url = None
        if tts:
            print(f"🎤 Starting TTS with speaker_wav: {wav_path}")
            summary_to_audio(
                text=summary["summary"],
                output_path="meeting_summary.wav",
                lang="en",
                speaker_wav=wav_path,
            )
            audio_url = "/download/meeting_summary.wav"

        return {
            "transcript": transcript,
            "summary": summary["raw"],
            "audio_url": audio_url,
        }

    except Exception as e:
        print(f"❌ Error in /summarize: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

    finally:
        # Cleanup AFTER everything including TTS
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
        if wav_path and wav_path != audio_path and os.path.exists(wav_path):
            os.remove(wav_path)


# ── Route 5: Download audio ───────────────────────────────────
@app.get("/download/{filename}")
def download(filename: str):
    if os.path.exists(filename):
        return FileResponse(filename, media_type="audio/wav")
    return JSONResponse({"error": "File not found"}, status_code=404)


# ── Auto-open browser + run server ───────────────────────────
def open_browser():
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    print("🚀 Starting Meeting Summarizer...")
    print("🌐 Opening browser at http://127.0.0.1:8000")
    threading.Timer(1.5, open_browser).start()
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)