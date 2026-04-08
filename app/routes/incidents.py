import uuid
from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile
from pydantic import ValidationError
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models.incident import Incident, IncidentAttachment, IncidentStatus
from app.schemas.incident import IncidentCreate, IncidentListResponse, IncidentResponse

router = APIRouter(prefix="/api/incidents", tags=["incidents"])

ALLOWED_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/webp",
    "text/plain",
    "application/pdf",
    "application/json",
    "text/csv",
}
MAX_UPLOAD_BYTES = settings.max_upload_size_mb * 1024 * 1024


@router.post("", response_model=IncidentResponse, status_code=201)
async def create_incident(
    reporter_email: str = Form(...),
    description: str = Form(...),
    reporter_name: str | None = Form(None),
    files: list[UploadFile] | None = None,
    db: AsyncSession = Depends(get_db),
) -> Incident:
    """Create a new incident with optional file attachments."""
    # Validate input via schema
    try:
        data = IncidentCreate(
            reporter_name=reporter_name,
            reporter_email=reporter_email,
            description=description,
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    incident = Incident(
        reporter_name=data.reporter_name,
        reporter_email=data.reporter_email,
        description=data.description,
        status=IncidentStatus.SUBMITTED,
    )
    db.add(incident)
    await db.flush()  # Get the ID

    # Handle file uploads
    if files:
        upload_dir = Path(settings.upload_dir) / str(incident.id)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Validate all files before writing any to disk
        validated_files: list[tuple[str, bytes, str]] = []
        for upload_file in files:
            if not upload_file.filename:
                continue

            content_type = upload_file.content_type or "application/octet-stream"
            if content_type not in ALLOWED_MIME_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type '{content_type}' not allowed. Allowed: {', '.join(sorted(ALLOWED_MIME_TYPES))}",
                )

            content = await upload_file.read()
            if len(content) > MAX_UPLOAD_BYTES:
                raise HTTPException(
                    status_code=400,
                    detail=f"File '{upload_file.filename}' exceeds {settings.max_upload_size_mb}MB limit",
                )

            validated_files.append((upload_file.filename, content, content_type))

        # Write validated files to disk
        for original_name, content, content_type in validated_files:
            safe_filename = f"{uuid.uuid4().hex}_{Path(original_name).name}"
            file_path = upload_dir / safe_filename
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)

            attachment = IncidentAttachment(
                incident_id=incident.id,
                filename=original_name,
                file_path=str(file_path),
                mime_type=content_type,
                file_size=len(content),
            )
            db.add(attachment)

    await db.commit()
    await db.refresh(incident, attribute_names=["attachments"])
    return incident


@router.get("", response_model=IncidentListResponse)
async def list_incidents(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List all incidents, newest first."""
    # Count
    count_result = await db.execute(select(func.count(Incident.id)))
    total = count_result.scalar_one()

    # Fetch
    query = (
        select(Incident)
        .options(selectinload(Incident.attachments))
        .order_by(Incident.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    incidents = result.scalars().all()

    return {"incidents": incidents, "total": total}


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> Incident:
    """Get incident details by ID."""
    query = (
        select(Incident)
        .options(selectinload(Incident.attachments))
        .where(Incident.id == incident_id)
    )
    result = await db.execute(query)
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    return incident
