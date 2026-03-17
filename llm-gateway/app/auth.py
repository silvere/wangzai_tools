"""Authentication middleware — validates access tokens."""
import secrets
from fastapi import Request, HTTPException
from app.database import get_db


async def verify_token(request: Request) -> str:
    """Verify Bearer token and return token name. Raises 401 if invalid."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = auth[7:]
    db = await get_db()
    cursor = await db.execute(
        "SELECT name, enabled FROM access_tokens WHERE token = ?", (token,)
    )
    row = await cursor.fetchone()
    await db.close()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid access token")
    if not row["enabled"]:
        raise HTTPException(status_code=403, detail="Token is disabled")
    return row["name"]


async def create_token(name: str) -> str:
    """Create a new access token."""
    token = f"gw-{secrets.token_hex(24)}"
    db = await get_db()
    from datetime import datetime
    await db.execute(
        "INSERT INTO access_tokens (token, name, created_at) VALUES (?, ?, ?)",
        (token, name, datetime.utcnow().isoformat())
    )
    await db.commit()
    await db.close()
    return token


async def list_tokens() -> list[dict]:
    db = await get_db()
    cursor = await db.execute("SELECT id, token, name, created_at, enabled FROM access_tokens")
    rows = await cursor.fetchall()
    await db.close()
    return [dict(r) for r in rows]


async def toggle_token(token_id: int, enabled: bool):
    db = await get_db()
    await db.execute("UPDATE access_tokens SET enabled = ? WHERE id = ?", (int(enabled), token_id))
    await db.commit()
    await db.close()


async def delete_token(token_id: int):
    db = await get_db()
    await db.execute("DELETE FROM access_tokens WHERE id = ?", (token_id,))
    await db.commit()
    await db.close()
