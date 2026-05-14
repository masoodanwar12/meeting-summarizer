"""
tts.py - Text-to-Speech using XTTS v2 (Your Own Voice)
=======================================================
Converts text to audio using your cloned voice.
Requires: a WAV file (10-30 sec recording of your voice)
"""
import os
import torch
import numpy as np
from functools import partial
from scipy.io import wavfile
from scipy.signal import resample

# Patch torch.load to avoid weights_only error with XTTS
_original_torch_load = torch.load
torch.load = partial(_original_torch_load, weights_only=False)

from TTS.api import TTS

XTTS_SAMPLE_RATE = 22050


def _prepare_voice_wav(src_path: str) -> str:
    """Resample speaker WAV to 22050Hz if needed (XTTS v2 requirement)."""
    rate, data = wavfile.read(src_path)
    if rate == XTTS_SAMPLE_RATE:
        return src_path  # already correct, no change needed
    print(f"🔧 Resampling voice from {rate}Hz → {XTTS_SAMPLE_RATE}Hz...")
    num_samples = int(len(data) * XTTS_SAMPLE_RATE / rate)
    resampled = resample(data, num_samples).astype(np.int16)
    prepared_path = src_path.replace(".wav", "_22k.wav")
    wavfile.write(prepared_path, XTTS_SAMPLE_RATE, resampled)
    print(f"✅ Resampled voice saved: {prepared_path}")
    return prepared_path


def summary_to_audio(
    text: str,
    output_path: str = "meeting_summary.wav",
    lang: str = "en",
    speaker_wav: str = "my_voice.wav",
) -> str:
    if not text or not text.strip():
        raise ValueError("Cannot convert empty text to audio.")

    if not os.path.exists(speaker_wav):
        raise FileNotFoundError(f"Speaker voice file not found: '{speaker_wav}'")

    # Resample to 22050Hz if needed (fixes "Error opening wav: System error")
    speaker_wav = _prepare_voice_wav(speaker_wav)

    print("🔊 Loading voice cloning model (first time takes a few minutes)...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    print(f"🎤 Generating audio in your voice...")
    tts.tts_to_file(
        text=text.strip(),
        speaker_wav=speaker_wav,
        language=lang,
        file_path=output_path
    )

    print(f"🎵 Audio saved to: {output_path}")
    return output_path