# app/routes/xp.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.xp_service import process_xp_event

router = APIRouter()


class XPEvent(BaseModel):
    user_id: str
    action: str
    metadata: dict = {}


@router.post("/xp")
async def add_xp(event: XPEvent):
    result = await process_xp_event(event)
    return result
