import whisper
import os


def transcribe_audio(audio_path: str, model_size: str = "base") -> str:
    """
    Transcribe an audio file to text using OpenAI Whisper.

    Args:
        audio_path:  Path to the audio file (.wav, .mp3, .m4a, etc.)
        model_size:  Whisper model to use:
                     "tiny"   → fastest, least accurate
                     "base"   → good balance (recommended)
                     "small"  → more accurate, slower
                     "medium" → even better, needs more RAM
                     "large"  → best accuracy, slow

    Returns:
        Transcribed text as a string
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"\n📝 Loading Whisper '{model_size}' model...")
    model = whisper.load_model(model_size)

    print(f"🔄 Transcribing '{audio_path}'... (this may take a moment)")
    result = model.transcribe(audio_path)

    transcript = result["text"].strip()
    print("✅ Transcription complete.\n")
    return transcript
