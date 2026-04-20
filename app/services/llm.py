import json
from openai import OpenAI
from app.config import OPENAI_API_KEY
from app.models.video_content import VideoContent

client = OpenAI(api_key=OPENAI_API_KEY)


def generate_content(transcript: str) -> VideoContent:
    prompt = f"""
You are a viral content strategist.

Return ONLY valid JSON in this exact format:

{{
  "hooks": "5 viral hooks",
  "insights": "3 insights",
  "contrarian": "2 contrarian takes",
  "summary": "1 summary",
  "quotes": "5 quote snippets"
}}

Rules:
- short, punchy
- optimized for Telegram engagement
- no extra text
- no markdown
- no explanations

Transcript:
{transcript}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You write viral content."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
    )

    raw_output = response.choices[0].message.content or ""

    try:
        data = json.loads(raw_output)
        return VideoContent(**data)

    except Exception as e:
        print("Parsing error:", e)
        print("Raw output:", raw_output)

        # Fallback (still valid type)
        return VideoContent(
            hooks="Failed to generate hooks",
            insights="",
            contrarian="",
            summary="Something went wrong generating content.",
            quotes=""
        )