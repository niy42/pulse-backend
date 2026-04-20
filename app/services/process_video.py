from app.services.youtube import extract_transcript
from app.services.llm import generate_content
from app.models.video_content import VideoContent
import asyncio


async def process_video(url: str) -> VideoContent:

    transcript = await extract_transcript(url)

    if not transcript:
        return VideoContent(
            hooks=["No hooks generated"],
            insights=["No insights generated"],
            contrarian=["No contrarian angle available"],
            summary=["Could not extract content from this video."],
            quotes=["No quotes available"],
        )

    # result = generate_content(transcript)
    # result = await asyncio.to_thread(generate_content, transcript)
    result = VideoContent(
        hooks=["Test hook"],
        insights=["Test insight"],
        contrarian=["Test contrarian"],
        summary=["Test summary"],
        quotes=["Test quotes"],
    )

    return result
