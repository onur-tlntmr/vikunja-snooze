from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel

class VikunjaTask(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    done: bool = False
    due_date: Optional[datetime] = None
    reminders: Optional[list[Any]] = None
    project_id: int

class VikunjaWebhookData(BaseModel):
    task: VikunjaTask

class VikunjaWebhookPayload(BaseModel):
    event_name: str
    time: datetime
    data: VikunjaWebhookData
