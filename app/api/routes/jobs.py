from fastapi import APIRouter, HTTPException
from uuid import uuid4
from datetime import datetime
import asyncio
import re
import json

from pydantic import BaseModel, field_validator
from typing import Any

from sse_starlette.sse import EventSourceResponse

from app.services.process_video import process_video
from app.services.user_service import get_or_create_user
from app.utils.helper import load_jobs, save_jobs

router = APIRouter()

jobs = load_jobs()


class APIError(BaseModel):
    message: str
    sub_message: str | None = None
    action: str | None = None


# -------------------------
# 📦 Schemas
# -------------------------
class CreateChatRequest(BaseModel):
    user_id: str


class SendMessageRequest(BaseModel):
    content: str

    @field_validator("content")
    def validate_url(cls, v):
        if not re.match(r"(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+", v):
            raise ValueError("Invalid YouTube URL")
        return v


class Message(BaseModel):
    role: str  # "user" | "assistant"
    content: Any


# -------------------------
# 🚀 Create New Chat
# -------------------------
@router.post("/chats")
async def create_chat(data: CreateChatRequest):
    job_id = str(uuid4())

    jobs[job_id] = {
        "id": job_id,
        "user_id": data.user_id,
        "title": "New Chat",
        "messages": [],
        "created_at": datetime.utcnow().isoformat(),
        "status": "idle",  # 👈 track job state
    }
    save_jobs(jobs)
    return jobs[job_id]


# -------------------------
# 💬 Send Message (Start Processing)
# -------------------------
@router.post("/chats/{chat_id}/messages")
async def send_message(chat_id: str, data: SendMessageRequest):
    # print("jobs before:", jobs)
    job = jobs.get(chat_id)

    if not job:
        # print(f"Missing chat_id: {chat_id}. Available: {list(jobs.keys())}")
        raise HTTPException(status_code=404, detail="Chat not found or expired")

    user = get_or_create_user(job["user_id"])

    if user["plan"] == "free" and user["requests_used"] >= 3:
        raise HTTPException(
            status_code=403,
            detail={
                "title": "Limit Reached",
                "message": "Upgrade to Pro to continue",
                "sub_message": "Your tokens will renew after 24 hours",
                "action": "Upgrade to Pro",
            },
        )

    user["requests_used"] += 1

    job["messages"].append(
        {
            "role": "user",
            "content": data.content,
        }
    )

    job["status"] = "processing"

    save_jobs(jobs)

    asyncio.create_task(run_job(chat_id, data.content))

    return {"status": "processing"}

    # ⚙️ Async processing
    asyncio.create_task(run_job(chat_id, data.content))

    return {"status": "processing"}


# -------------------------
# 📚 Get All Chats (Sidebar)
# -------------------------
@router.get("/chats")
async def get_chats(user_id: str):
    user_chats = [job for job in jobs.values() if job["user_id"] == user_id]
    return user_chats[::-1]


# -------------------------
# 💬 Get Single Chat
# -------------------------
@router.get("/chats/{chat_id}")
async def get_chat(chat_id: str):
    job = jobs.get(chat_id)

    if not job:
        raise HTTPException(status_code=404, detail="Chat not found")

    return job


# -------------------------
# ⚡ SSE STREAM ENDPOINT
# -------------------------
@router.get("/chats/{chat_id}/stream")
async def stream_chat(chat_id: str):
    async def event_generator():
        last_sent_len = 0

        while True:
            job = jobs.get(chat_id)

            if not job:
                yield {
                    "event": "error",
                    "data": json.dumps({"error": "Chat not found"}),
                }
                break

            messages = job["messages"]

            # 🔥 only send if new messages exist
            if len(messages) != last_sent_len:
                yield {
                    "event": "message",
                    "data": json.dumps(messages),
                }
                last_sent_len = len(messages)

            # ✅ stop when processing done
            if job["status"] == "done":
                yield {
                    "event": "end",
                    "data": "done",
                }
                break

            await asyncio.sleep(0.8)  # smoother than 1.5s

    return EventSourceResponse(event_generator())


# -------------------------
# ⚙️ Background Processor
# -------------------------
async def run_job(chat_id: str, url: str):
    job = jobs[chat_id]

    try:
        result = await process_video(url)

        # 🤖 Assistant response
        job["messages"].append(
            {
                "role": "assistant",
                "content": {
                    "hooks": result.hooks,
                    "insights": result.insights,
                    "contrarian": result.contrarian,
                    "summary": result.summary,
                    "quotes": result.quotes,
                },
            }
        )

        # 🧠 Auto-title chat
        if job["title"] == "New Chat":
            job["title"] = url[:50]

        job["status"] = "done"

    except Exception as e:
        job["messages"].append(
            {
                "role": "assistant",
                "content": {"error": str(e)},
            }
        )

        job["status"] = "done"


@router.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str):
    if chat_id in jobs:
        del jobs[chat_id]
        return {"status": "deleted"}
    raise HTTPException(404, "Not found")


@router.patch("/chats/{chat_id}")
async def rename_chat(chat_id: str, title: str):
    job = jobs.get(chat_id)
    if not job:
        raise HTTPException(404, "Not found")

    job["title"] = title
    return job
