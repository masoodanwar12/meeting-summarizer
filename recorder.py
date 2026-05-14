import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np

SAMPLE_RATE = 16000  # Whisper works best at 16kHz


def record_audio(output_path: str = "meeting.wav", duration: int = None) -> str:
    """
    Record audio from the microphone.

    Args:
        output_path: Where to save the .wav file
        duration: Recording duration in seconds.
                  If None, press Enter to stop recording.

    Returns:
        Path to the saved audio file
    """
    if duration:
        print(f"\n🎙️  Recording for {duration} seconds... Speak now!")
        audio = sd.rec(
            int(duration * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16"
        )
        sd.wait()
        print("✅ Recording complete.")
    else:
        print("\n🎙️  Recording started. Press ENTER to stop...")
        frames = []

        def callback(indata, frame_count, time_info, status):
            frames.append(indata.copy())

        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16", callback=callback):
            input()  # Wait for user to press Enter

        audio = np.concatenate(frames, axis=0)
        print("✅ Recording stopped.")

    write(output_path, SAMPLE_RATE, audio)
    print(f"💾 Audio saved to: {output_path}")
    return output_path
