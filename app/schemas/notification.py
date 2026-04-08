import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.notification import NotificationType


class NotificationResponse(BaseModel):
    id: uuid.UUID
    incident_id: uuid.UUID
    type: NotificationType
    recipient: str
    subject: str | None
    body: str
    sent: bool
    sent_at: datetime | None
    error: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
