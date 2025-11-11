from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class Event(BaseModel):
    id: Optional[str] = Field(default=None)
    title: str
    date: str
    location: str
    performers: List[str] = []
    description: Optional[str] = None
