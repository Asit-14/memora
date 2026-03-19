from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NoteCreate(BaseModel):
    title: str
    content: Optional[str] = None
    is_pinned: bool = False
    color: str = 'default'


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    is_pinned: Optional[bool] = None
    color: Optional[str] = None


class NoteResponse(BaseModel):
    id: int
    title: str
    content: Optional[str]
    is_pinned: bool
    color: str
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
