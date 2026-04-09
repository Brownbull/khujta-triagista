import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.incident import IncidentStatus, Severity


class IncidentCreate(BaseModel):
    reporter_name: str | None = None
    reporter_email: str = Field(..., max_length=255)
    description: str = Field(..., min_length=10, max_length=10000)


class AttachmentResponse(BaseModel):
    id: uuid.UUID
    filename: str
    mime_type: str
    file_size: int

    model_config = {"from_attributes": True}


class IncidentResponse(BaseModel):
    id: uuid.UUID
    reporter_name: str | None
    reporter_email: str
    description: str
    status: IncidentStatus
    severity: Severity | None
    category: str | None
    affected_component: str | None
    technical_summary: str | None
    root_cause_hypothesis: str | None
    suggested_assignee: str | None
    confidence: float | None
    recommended_actions: list | None = None
    related_files: list | None = None
    triage_engine: str | None = None
    triage_tokens_in: int | None = None
    triage_tokens_out: int | None = None
    validation_flags: dict | None = None
    injection_score: float | None = None
    resolved_at: datetime | None
    resolution_type: str | None
    resolution_notes: str | None
    created_at: datetime
    updated_at: datetime
    attachments: list[AttachmentResponse] = []

    model_config = {"from_attributes": True}


class IncidentListResponse(BaseModel):
    incidents: list[IncidentResponse]
    total: int
