import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.ticket import Ticket
    from app.models.notification import Notification


class IncidentStatus(str, enum.Enum):
    SUBMITTED = "submitted"
    VALIDATING = "validating"
    TRIAGING = "triaging"
    DISPATCHED = "dispatched"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class Severity(str, enum.Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class Incident(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "incidents"

    # Reporter info
    reporter_name: Mapped[str | None] = mapped_column(String(255))
    reporter_email: Mapped[str] = mapped_column(String(255))

    # Incident content
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus), default=IncidentStatus.SUBMITTED, index=True
    )

    # Triage results (populated by agent)
    severity: Mapped[Severity | None] = mapped_column(Enum(Severity))
    category: Mapped[str | None] = mapped_column(String(100))
    affected_component: Mapped[str | None] = mapped_column(String(255))
    technical_summary: Mapped[str | None] = mapped_column(Text)
    root_cause_hypothesis: Mapped[str | None] = mapped_column(Text)
    suggested_assignee: Mapped[str | None] = mapped_column(String(255))
    confidence: Mapped[float | None] = mapped_column()
    recommended_actions: Mapped[dict | None] = mapped_column(JSON)
    related_files: Mapped[dict | None] = mapped_column(JSON)

    # Validation
    validation_flags: Mapped[dict | None] = mapped_column(JSON)
    injection_score: Mapped[float | None] = mapped_column()

    # Resolution
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolution_type: Mapped[str | None] = mapped_column(String(50))
    resolution_notes: Mapped[str | None] = mapped_column(Text)

    # Relationships
    attachments: Mapped[list["IncidentAttachment"]] = relationship(back_populates="incident")
    ticket: Mapped["Ticket | None"] = relationship(back_populates="incident")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="incident")


class IncidentAttachment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "incident_attachments"

    incident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("incidents.id")
    )
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(500))
    mime_type: Mapped[str] = mapped_column(String(100))
    file_size: Mapped[int] = mapped_column()

    incident: Mapped["Incident"] = relationship(back_populates="attachments")
