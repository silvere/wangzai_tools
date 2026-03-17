import aiosqlite
import os
from datetime import datetime

DB_PATH = "data/gateway.db"


async def get_db():
    os.makedirs("data", exist_ok=True)
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    db = await get_db()
    await db.executescript("""
        CREATE TABLE IF NOT EXISTS access_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            rate_limit INTEGER DEFAULT NULL
        );

        CREATE TABLE IF NOT EXISTS provider_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT NOT NULL,
            api_key TEXT NOT NULL,
            base_url TEXT NOT NULL,
            enabled INTEGER DEFAULT 1,
            priority INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS request_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            token_name TEXT,
            model TEXT NOT NULL,
            provider TEXT NOT NULL,
            prompt_tokens INTEGER DEFAULT 0,
            completion_tokens INTEGER DEFAULT 0,
            total_tokens INTEGER DEFAULT 0,
            input_cost REAL DEFAULT 0,
            output_cost REAL DEFAULT 0,
            total_cost REAL DEFAULT 0,
            latency_ms INTEGER DEFAULT 0,
            status TEXT DEFAULT 'ok',
            error TEXT DEFAULT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON request_logs(timestamp);
        CREATE INDEX IF NOT EXISTS idx_logs_model ON request_logs(model);
        CREATE INDEX IF NOT EXISTS idx_logs_token ON request_logs(token_name);
    """)
    await db.commit()
    await db.close()


async def log_request(
    token_name: str, model: str, provider: str,
    prompt_tokens: int, completion_tokens: int,
    input_cost: float, output_cost: float,
    latency_ms: int, status: str = "ok", error: str = None
):
    db = await get_db()
    await db.execute(
        """INSERT INTO request_logs
        (timestamp, token_name, model, provider, prompt_tokens, completion_tokens,
         total_tokens, input_cost, output_cost, total_cost, latency_ms, status, error)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.utcnow().isoformat(),
            token_name, model, provider,
            prompt_tokens, completion_tokens,
            prompt_tokens + completion_tokens,
            input_cost, output_cost, input_cost + output_cost,
            latency_ms, status, error
        )
    )
    await db.commit()
    await db.close()


async def get_stats(days: int = 7):
    db = await get_db()
    cursor = await db.execute("""
        SELECT
            COUNT(*) as total_requests,
            SUM(total_tokens) as total_tokens,
            SUM(total_cost) as total_cost,
            SUM(prompt_tokens) as total_prompt_tokens,
            SUM(completion_tokens) as total_completion_tokens,
            AVG(latency_ms) as avg_latency,
            COUNT(CASE WHEN status != 'ok' THEN 1 END) as error_count
        FROM request_logs
        WHERE timestamp >= datetime('now', ?)
    """, (f"-{days} days",))
    row = await cursor.fetchone()
    await db.close()
    return dict(row) if row else {}


async def get_stats_by_model(days: int = 7):
    db = await get_db()
    cursor = await db.execute("""
        SELECT
            model,
            COUNT(*) as requests,
            SUM(total_tokens) as tokens,
            SUM(total_cost) as cost,
            AVG(latency_ms) as avg_latency
        FROM request_logs
        WHERE timestamp >= datetime('now', ?)
        GROUP BY model
        ORDER BY cost DESC
    """, (f"-{days} days",))
    rows = await cursor.fetchall()
    await db.close()
    return [dict(r) for r in rows]


async def get_daily_stats(days: int = 30):
    db = await get_db()
    cursor = await db.execute("""
        SELECT
            DATE(timestamp) as date,
            COUNT(*) as requests,
            SUM(total_tokens) as tokens,
            SUM(total_cost) as cost
        FROM request_logs
        WHERE timestamp >= datetime('now', ?)
        GROUP BY DATE(timestamp)
        ORDER BY date
    """, (f"-{days} days",))
    rows = await cursor.fetchall()
    await db.close()
    return [dict(r) for r in rows]


async def get_recent_logs(limit: int = 50):
    db = await get_db()
    cursor = await db.execute("""
        SELECT * FROM request_logs
        ORDER BY id DESC LIMIT ?
    """, (limit,))
    rows = await cursor.fetchall()
    await db.close()
    return [dict(r) for r in rows]
