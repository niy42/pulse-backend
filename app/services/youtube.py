import asyncio
from logging import info

import yt_dlp
import requests
import os
from typing import Any, Dict, Optional, cast


DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


import requests
from typing import Dict, Any


def log(step: str, msg: str = ""):
    print(f"\n[YT-PIPELINE] {step} {msg}")


def _extract_caption_text(sub_data: Dict[str, Any]) -> str:
    if not sub_data:
        return ""

    for lang, tracks in sub_data.items():
        for track in tracks:
            url = track.get("url")
            ext = track.get("ext")

            if not url:
                continue

            try:
                res = requests.get(url, timeout=10)
                data = res.json()

                # 🟢 JSON3 format (your current logic)
                if ext == "json3":
                    text = " ".join(
                        seg.get("utf8", "")
                        for event in data.get("events", [])
                        for seg in event.get("segs", [])
                    )

                # 🟡 VTT / other formats fallback
                else:
                    # text = res.text  # crude fallback (better than nothing)
                    text = res.text.replace("\n", " ")

                if text.strip():
                    return text.strip()

            except Exception:
                continue

    return ""


def _download_audio(url: str) -> Optional[str]:
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{DOWNLOAD_DIR}/%(id)s.%(ext)s",
        "quiet": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "postprocessor_args": ["-t", "600"],  # first 10 minutes only
    }

    log("STEP 1", "Extracting metadata + captions...")

    try:
        with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
            info = ydl.extract_info(url, download=False)
        log("STEP 1 OK", f"Title: {info.get('title')}")
    except Exception as e:
        log("STEP 1 FAILED", str(e))
        return ""


def _transcribe_audio(file_path: str) -> str:
    try:
        return (
            "This is a sample transcription of a YouTube video. "
            "The speaker talks about productivity, consistency, and growth. "
            "They emphasize that success comes from small daily actions, "
            "not sudden breakthroughs."
        )
    except Exception as e:
        print(f"[Transcription Error] {e}")
        return ""


from openai import OpenAI
import os


# def get_openai_client():
#     return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# def _transcribe_audio(file_path: str) -> str:
# client = get_openai_client()
#     try:
#         with open(file_path, "rb") as audio_file:
#             transcript = client.audio.transcriptions.create(
#                 file=audio_file,
#                 model="gpt-4o-transcribe",  # Whisper successor
#                 response_format="text",
#             )

#         return transcript.strip()

#     except Exception as e:
#         print(f"[Transcription Error] {e}")
#         return ""


async def extract_transcript(url: str) -> str:
    """
    Production-grade pipeline:
    1. Try captions (fast)
    2. Fallback to audio + transcription (reliable)
    """

    # 🔹 STEP 1: Extract metadata + captions
    ydl_opts: Dict[str, Any] = {
        "quiet": True,
        "skip_download": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitlesformat": "json3",
        "js_runtimes": {"node": r"C:\Program Files\nodejs\node.exe"},
    }

    try:
        with yt_dlp.YoutubeDL(cast(Any, ydl_opts)) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        print(f"[Metadata Error] {e}")
        return ""

    # 🔹 STEP 2: Try subtitles
    subtitles = info.get("subtitles") or {}
    auto_subs = info.get("automatic_captions") or {}

    log("STEP 2", f"subtitles keys: {list(subtitles.keys())}")
    log("STEP 2", f"auto captions keys: {list(auto_subs.keys())}")

    all_captions = {**auto_subs, **subtitles}

    log("STEP 3", "Extracting caption text...")

    transcript = _extract_caption_text(all_captions)

    log("STEP 3 RESULT", f"Length: {len(transcript)} chars")

    # if not transcript:
    #     transcript = await asyncio.to_thread(_extract_caption_text, subtitles)

    if transcript:
        log("STEP 4", "SUCCESS using captions")
        return transcript.strip()

    log("STEP 4", "No captions found → fallback to audio")

    # 🔹 STEP 3: Fallback → audio download + transcription
    log("STEP 5", "Downloading audio...")

    audio_path = _download_audio(url)

    if audio_path:
        log("STEP 5 OK", f"Audio saved: {audio_path}")

        transcript = _transcribe_audio(audio_path)

        log("STEP 5 RESULT", f"Transcript length: {len(transcript)}")

        # Optional cleanup (important for production)
        try:
            os.remove(audio_path)
        except Exception:
            pass

        if transcript:
            return transcript.strip()

    # 🔻 Final fallback
    log("FINAL", "Using description fallback")

    return info.get("description", "").strip()
