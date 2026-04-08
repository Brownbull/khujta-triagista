import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.incident import Incident

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: AsyncSession = Depends(get_db)):
    """Home page — redirect to incident list."""
    count_result = await db.execute(select(func.count(Incident.id)))
    total = count_result.scalar_one()
    return templates.TemplateResponse(
        request,
        "incidents/list.html",
        context={"incidents": [], "total": total, "page": "list"},
    )


@router.get("/incidents", response_class=HTMLResponse)
async def incident_list_page(request: Request, db: AsyncSession = Depends(get_db)):
    """List all incidents."""
    query = (
        select(Incident)
        .options(selectinload(Incident.attachments))
        .order_by(Incident.created_at.desc())
        .limit(100)
    )
    result = await db.execute(query)
    incidents = result.scalars().all()

    count_result = await db.execute(select(func.count(Incident.id)))
    total = count_result.scalar_one()

    return templates.TemplateResponse(
        request,
        "incidents/list.html",
        context={"incidents": incidents, "total": total, "page": "list"},
    )


@router.get("/incidents/new", response_class=HTMLResponse)
async def incident_new_page(request: Request):
    """Submit a new incident form."""
    return templates.TemplateResponse(
        request,
        "incidents/submit.html",
        context={"page": "new"},
    )


@router.get("/incidents/{incident_id}", response_class=HTMLResponse)
async def incident_detail_page(
    request: Request,
    incident_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Incident detail page."""
    query = (
        select(Incident)
        .options(selectinload(Incident.attachments))
        .where(Incident.id == incident_id)
    )
    result = await db.execute(query)
    incident = result.scalar_one_or_none()

    if not incident:
        return templates.TemplateResponse(
            request,
            "incidents/not_found.html",
            context={"page": "detail"},
            status_code=404,
        )

    return templates.TemplateResponse(
        request,
        "incidents/detail.html",
        context={"incident": incident, "page": "detail"},
    )
