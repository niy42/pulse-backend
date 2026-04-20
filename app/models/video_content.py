from pydantic import BaseModel, Field


class VideoContent(BaseModel):
    hooks: list[str] = Field(..., min_length=1)
    insights: list[str]
    contrarian: list[str]
    summary: list[str]
    quotes: list[str]
