from pydantic import BaseModel
from enum import Enum
from typing import Optional

class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    FAILED = "FAILED"

class Notification(BaseModel):
    message_id: str
    recipient: str
    subject: str
    body: str
    status: NotificationStatus = NotificationStatus.PENDING
    retry_count: int = 0
    error_message: Optional[str] = None
