"""
Meeting Summarizer
==================
Transcribes a meeting (from mic or audio file) and summarizes it using Claude.
Optionally converts the summary to speech using XTTS v2.

Usage:
    python main.py                          → record from mic
    python main.py --file meeting.mp3       → use existing audio file
    python main.py --duration 60            → record for exactly 60 seconds
    python main.py --tts                    → also speak the summary aloud (saves WAV)
    python main.py --file meeting.mp3 --tts → transcribe + summarize + speak
"""

import argparse
import os
from recorder import record_audio
from transcriber import transcribe_audio
from summarizer import summarize_transcript
from tts import summary_to_audio


def save_output(transcript: str, summary: dict, output_file: str = "meeting_output.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("           MEETING SUMMARIZER - OUTPUT\n")
        f.write("=" * 60 + "\n\n")
        f.write("📋 FULL SUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(summary["raw"] + "\n\n")
        f.write("=" * 60 + "\n")
        f.write("📝 FULL TRANSCRIPT\n")
        f.write("-" * 40 + "\n")
        f.write(transcript + "\n")
    print(f"💾 Output saved to: {output_file}")


def print_summary(summary: dict):
    print("\n" + "=" * 60)
    print("           📊 MEETING SUMMARY")
    print("=" * 60)
    print(summary["raw"])
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Meeting Summarizer")
    parser.add_argument("--file", type=str, help="Path to an existing audio file")
    parser.add_argument("--duration", type=int, help="Record for N seconds (mic mode)")
    parser.add_argument("--model", type=str, default="base",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size (default: base)")
    parser.add_argument("--output", type=str, default="meeting_output.txt",
                        help="Output file path (default: meeting_output.txt)")
    parser.add_argument("--tts", action="store_true",
                        help="Convert the meeting summary to speech (saves WAV)")
    parser.add_argument("--tts-output", type=str, default="meeting_summary.wav",
                        help="TTS audio output path (default: meeting_summary.wav)")
    parser.add_argument("--tts-lang", type=str, default="en",
                        help="Language code for TTS, e.g. 'en', 'ur', 'fr' (default: en)")
    parser.add_argument("--voice", type=str, default="meeting_recording.wav",
                        help="Path to speaker WAV file for voice cloning (default: meeting_recording.wav)")
    args = parser.parse_args()

    print("\n🎯 Meeting Summarizer Starting...\n")

    # ── Step 1: Get audio ──────────────────────────────────────────
    if args.file:
        print(f"📂 Using audio file: {args.file}")
        audio_path = args.file
    else:
        audio_path = record_audio(
            output_path="meeting_recording.wav",
            duration=args.duration
        )

    # ── Step 2: Transcribe ─────────────────────────────────────────
    transcript = transcribe_audio(audio_path, model_size=args.model)

    print("📄 TRANSCRIPT PREVIEW:")
    print("-" * 40)
    print(transcript[:500] + ("..." if len(transcript) > 500 else ""))
    print("-" * 40)

    if not transcript.strip():
        print("❌ Transcript is empty. Please check your audio file or recording.")
        return

    # ── Step 3: Summarize ──────────────────────────────────────────
    summary = summarize_transcript(transcript)

    print_summary(summary)
    save_output(transcript, summary, output_file=args.output)

    # ── Step 4: TTS (optional) ─────────────────────────────────────
    if args.tts:
        if not os.path.exists(args.voice):
            print(f"⚠️  TTS skipped: Speaker voice file '{args.voice}' not found.")
            print(f"    Or specify a different file with: --voice path/to/voice.wav")
            return

        try:
            tts_text = summary["summary"]
            if not tts_text or not tts_text.strip():
                print("⚠️  TTS skipped: Summary text is empty.")
                return

            audio_out = summary_to_audio(
                text=tts_text,
                output_path=args.tts_output,
                lang=args.tts_lang,
                speaker_wav=args.voice,
            )
            print(f"✅ TTS complete! Audio saved to: {audio_out}")

        except FileNotFoundError as e:
            print(f"❌ TTS failed — file not found: {e}")
        except ValueError as e:
            print(f"❌ TTS failed — invalid input: {e}")
        except Exception as e:
            print(f"❌ TTS failed unexpectedly: {e}")


if __name__ == "__main__":
    main()