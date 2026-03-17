"""Admin API — manage tokens, view stats, configure providers."""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.config import settings
from app.auth import create_token, list_tokens, toggle_token, delete_token
from app.database import get_stats, get_stats_by_model, get_daily_stats, get_recent_logs

router = APIRouter(prefix="/admin")


def _check_admin(request: Request):
    """Simple admin auth via gateway secret."""
    auth = request.headers.get("Authorization", "")
    token = auth.replace("Bearer ", "") if auth.startswith("Bearer ") else ""
    secret = request.query_params.get("secret", "")
    if token != settings.gateway_secret and secret != settings.gateway_secret:
        raise HTTPException(status_code=403, detail="Admin access denied")


# --- Token Management ---

class CreateTokenRequest(BaseModel):
    name: str


@router.post("/tokens")
async def admin_create_token(request: Request, body: CreateTokenRequest):
    _check_admin(request)
    token = await create_token(body.name)
    return {"token": token, "name": body.name}


@router.get("/tokens")
async def admin_list_tokens(request: Request):
    _check_admin(request)
    tokens = await list_tokens()
    # Mask tokens for security
    for t in tokens:
        tk = t["token"]
        t["token_masked"] = tk[:6] + "..." + tk[-4:] if len(tk) > 10 else tk
    return {"tokens": tokens}


@router.delete("/tokens/{token_id}")
async def admin_delete_token(request: Request, token_id: int):
    _check_admin(request)
    await delete_token(token_id)
    return {"ok": True}


@router.patch("/tokens/{token_id}")
async def admin_toggle_token(request: Request, token_id: int, enabled: bool = True):
    _check_admin(request)
    await toggle_token(token_id, enabled)
    return {"ok": True}


# --- Stats ---

@router.get("/stats")
async def admin_stats(request: Request, days: int = 7):
    _check_admin(request)
    overview = await get_stats(days)
    by_model = await get_stats_by_model(days)
    daily = await get_daily_stats(days)
    return {"overview": overview, "by_model": by_model, "daily": daily}


@router.get("/logs")
async def admin_logs(request: Request, limit: int = 50):
    _check_admin(request)
    logs = await get_recent_logs(limit)
    return {"logs": logs}
