"""Dashboard page-serving routes (read-only UI, no honeypot logic)."""

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.core.settings import settings

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

templates = Jinja2Templates(directory=str(settings.base_path / "templates"))


@router.get("", include_in_schema=False)
async def overview(request: Request):
    """Render the dashboard overview page."""
    return templates.TemplateResponse(
        "dashboard/overview.html",
        {"request": request, "active_page": "overview"},
    )


@router.get("/sessions", include_in_schema=False)
async def sessions_list(request: Request):
    """Render the sessions list page."""
    return templates.TemplateResponse(
        "dashboard/sessions.html",
        {"request": request, "active_page": "sessions"},
    )


@router.get("/sessions/{session_id}", include_in_schema=False)
async def session_detail(request: Request, session_id: str):
    """Render the session detail page (JS fetches data client-side)."""
    return templates.TemplateResponse(
        "dashboard/detail.html",
        {
            "request": request,
            "active_page": "sessions",
            "session_id": session_id,
        },
    )
