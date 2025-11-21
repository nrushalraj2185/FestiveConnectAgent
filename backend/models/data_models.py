from typing import List, Optional
from pydantic import BaseModel, Field

class Event(BaseModel):
    id: Optional[str] = Field(default=None)
    title: str
    date: str
    location: str
    performers: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Organizer(BaseModel):
    organizer_id: Optional[str] = Field(default=None)
    name: str
    company: str
    region: str
    experience: int = 0  # years of experience
    managed_events: int = 0
    cultural_events: int = 0
    events_2025: int = 0
