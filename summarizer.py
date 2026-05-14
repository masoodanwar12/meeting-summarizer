from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()


def summarize_transcript(transcript: str) -> dict:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""You are an expert meeting analyst. Analyze the following meeting transcript and provide a structured summary.

TRANSCRIPT:
{transcript}

Please respond in this exact format:

SUMMARY:
[2-3 sentence overview of the meeting]

KEY POINTS:
- [key point 1]
- [key point 2]
- [key point 3]

ACTION ITEMS:
- [action item 1]
(write "None identified" if there are no clear action items)

DECISIONS MADE:
- [decision 1]
(write "None identified" if there are no clear decisions)
"""

    print("🤖 Sending transcript to Groq for summarization...")

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    raw_response = response.choices[0].message.content

    result = {
        "summary": _extract_section(raw_response, "SUMMARY"),
        "key_points": _extract_section(raw_response, "KEY POINTS"),
        "action_items": _extract_section(raw_response, "ACTION ITEMS"),
        "decisions": _extract_section(raw_response, "DECISIONS MADE"),
        "raw": raw_response
    }

    print("✅ Summary generated.\n")
    return result


def _extract_section(text: str, section_name: str) -> str:
    try:
        start = text.index(f"{section_name}:") + len(section_name) + 1
        next_section = None
        for marker in ["SUMMARY:", "KEY POINTS:", "ACTION ITEMS:", "DECISIONS MADE:"]:
            if marker != f"{section_name}:" and marker in text[start:]:
                pos = text.index(marker, start)
                if next_section is None or pos < next_section:
                    next_section = pos
        end = next_section if next_section else len(text)
        return text[start:end].strip()
    except ValueError:
        return "Not found"