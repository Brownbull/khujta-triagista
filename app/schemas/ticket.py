import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.ticket import TicketStatus


class TicketResponse(BaseModel):
    id: uuid.UUID
    incident_id: uuid.UUID
    title: str
    body: str
    status: TicketStatus
    labels: dict | None = None
    assignee: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
