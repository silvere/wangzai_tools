"""WebPilot 浏览器自动化工具 — FastAPI 后端 V0.2"""
import asyncio, base64, json, time, uuid
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from pathlib import Path
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

# --- State ---
pw = None
browser: Optional[Browser] = None
contexts: dict[str, BrowserContext] = {}
pages: dict[str, Page] = {}
screenshots: dict[str, bytes] = {}
task_logs: list[dict] = []

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
SCREENSHOTS_DIR = Path(__file__).parent.parent / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)
COOKIES_DIR = Path(__file__).parent.parent / "cookies"
COOKIES_DIR.mkdir(exist_ok=True)
TASKS_DIR = Path(__file__).parent.parent / "tasks"
TASKS_DIR.mkdir(exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global pw, browser
    pw = await async_playwright().start()
    browser = await pw.chromium.launch(headless=True, args=["--no-sandbox", "--disable-gpu"])
    print("🚀 WebPilot V0.1 启动 — Chromium ready")
    yield
    if browser: await browser.close()
    if pw: await pw.stop()
    print("👋 WebPilot 关闭")

app = FastAPI(title="WebPilot 浏览器自动化", version="0.2.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- Models ---
class NavigateReq(BaseModel):
    page_id: str
    url: str

class ClickReq(BaseModel):
    page_id: str
    selector: str

class TypeReq(BaseModel):
    page_id: str
    selector: str
    text: str

class EvalReq(BaseModel):
    page_id: str
    script: str

class WaitReq(BaseModel):
    page_id: str
    selector: str
    timeout: int = 10000

class TaskStep(BaseModel):
    action: str  # navigate, click, type, wait, screenshot, eval
    params: dict = {}

class TaskReq(BaseModel):
    name: str = "unnamed"
    steps: list[TaskStep]

class AICommandReq(BaseModel):
    page_id: str
    command: str  # natural language command

# --- Helpers ---
def log_action(page_id: str, action: str, detail: str, success: bool = True):
    entry = {"time": time.time(), "page_id": page_id, "action": action, "detail": detail, "success": success}
    task_logs.append(entry)
    if len(task_logs) > 500:
        task_logs.pop(0)

def get_page(page_id: str) -> Page:
    if page_id not in pages:
        raise HTTPException(404, f"Page {page_id} not found")
    return pages[page_id]

# --- Page Management ---
@app.post("/api/pages")
async def create_page():
    ctx = await browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = await ctx.new_page()
    pid = uuid.uuid4().hex[:8]
    contexts[pid] = ctx
    pages[pid] = page
    log_action(pid, "create", "New page created")
    return {"page_id": pid}

@app.get("/api/pages")
async def list_pages():
    result = []
    for pid, page in pages.items():
        try:
            result.append({"page_id": pid, "url": page.url, "title": await page.title()})
        except:
            result.append({"page_id": pid, "url": "unknown", "title": "unknown"})
    return result

@app.delete("/api/pages/{page_id}")
async def close_page(page_id: str):
    if page_id in pages:
        try: await pages[page_id].close()
        except: pass
        del pages[page_id]
    if page_id in contexts:
        try: await contexts[page_id].close()
        except: pass
        del contexts[page_id]
    return {"ok": True}

# --- Browser Actions ---
@app.post("/api/navigate")
async def navigate(req: NavigateReq):
    page = get_page(req.page_id)
    try:
        await page.goto(req.url, wait_until="domcontentloaded", timeout=30000)
        title = await page.title()
        log_action(req.page_id, "navigate", req.url)
        return {"url": page.url, "title": title}
    except Exception as e:
        log_action(req.page_id, "navigate", str(e), False)
        raise HTTPException(500, str(e))

@app.post("/api/click")
async def click(req: ClickReq):
    page = get_page(req.page_id)
    try:
        await page.click(req.selector, timeout=10000)
        log_action(req.page_id, "click", req.selector)
        return {"ok": True}
    except Exception as e:
        log_action(req.page_id, "click", str(e), False)
        raise HTTPException(500, str(e))

@app.post("/api/type")
async def type_text(req: TypeReq):
    page = get_page(req.page_id)
    try:
        await page.fill(req.selector, req.text, timeout=10000)
        log_action(req.page_id, "type", f"{req.selector} → {req.text[:50]}")
        return {"ok": True}
    except Exception as e:
        log_action(req.page_id, "type", str(e), False)
        raise HTTPException(500, str(e))

@app.post("/api/wait")
async def wait_for(req: WaitReq):
    page = get_page(req.page_id)
    try:
        await page.wait_for_selector(req.selector, timeout=req.timeout)
        log_action(req.page_id, "wait", req.selector)
        return {"ok": True}
    except Exception as e:
        log_action(req.page_id, "wait", str(e), False)
        raise HTTPException(500, str(e))

@app.post("/api/eval")
async def evaluate(req: EvalReq):
    page = get_page(req.page_id)
    try:
        result = await page.evaluate(req.script)
        log_action(req.page_id, "eval", req.script[:80])
        return {"result": result}
    except Exception as e:
        log_action(req.page_id, "eval", str(e), False)
        raise HTTPException(500, str(e))

@app.get("/api/screenshot/{page_id}")
async def screenshot(page_id: str):
    page = get_page(page_id)
    try:
        img = await page.screenshot(type="png")
        screenshots[page_id] = img
        # Also save to disk
        path = SCREENSHOTS_DIR / f"{page_id}_{int(time.time())}.png"
        path.write_bytes(img)
        log_action(page_id, "screenshot", str(path))
        return Response(content=img, media_type="image/png")
    except Exception as e:
        log_action(page_id, "screenshot", str(e), False)
        raise HTTPException(500, str(e))

@app.get("/api/content/{page_id}")
async def get_content(page_id: str):
    page = get_page(page_id)
    try:
        text = await page.evaluate("document.body.innerText")
        html = await page.content()
        return {"text": text[:5000], "html_length": len(html), "url": page.url, "title": await page.title()}
    except Exception as e:
        raise HTTPException(500, str(e))

# --- Task Runner ---
@app.post("/api/tasks/run")
async def run_task(req: TaskReq):
    """Run a sequence of browser actions"""
    results = []
    # Create a page for the task
    ctx = await browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    )
    page = await ctx.new_page()
    pid = uuid.uuid4().hex[:8]
    contexts[pid] = ctx
    pages[pid] = page

    for i, step in enumerate(req.steps):
        try:
            if step.action == "navigate":
                await page.goto(step.params.get("url", ""), wait_until="domcontentloaded", timeout=30000)
                results.append({"step": i, "action": "navigate", "ok": True, "url": page.url})
            elif step.action == "click":
                await page.click(step.params.get("selector", ""), timeout=10000)
                results.append({"step": i, "action": "click", "ok": True})
            elif step.action == "type":
                await page.fill(step.params.get("selector", ""), step.params.get("text", ""), timeout=10000)
                results.append({"step": i, "action": "type", "ok": True})
            elif step.action == "wait":
                await page.wait_for_selector(step.params.get("selector", ""), timeout=step.params.get("timeout", 10000))
                results.append({"step": i, "action": "wait", "ok": True})
            elif step.action == "screenshot":
                img = await page.screenshot(type="png")
                b64 = base64.b64encode(img).decode()
                results.append({"step": i, "action": "screenshot", "ok": True, "image_b64": b64})
            elif step.action == "eval":
                val = await page.evaluate(step.params.get("script", ""))
                results.append({"step": i, "action": "eval", "ok": True, "result": val})
            elif step.action == "sleep":
                await asyncio.sleep(step.params.get("seconds", 1))
                results.append({"step": i, "action": "sleep", "ok": True})
            else:
                results.append({"step": i, "action": step.action, "ok": False, "error": "Unknown action"})
        except Exception as e:
            results.append({"step": i, "action": step.action, "ok": False, "error": str(e)})
            if step.params.get("stop_on_error", False):
                break

    return {"task_name": req.name, "page_id": pid, "results": results, "total_steps": len(req.steps)}

class SaveTaskReq(BaseModel):
    name: str
    steps: list[TaskStep]
    description: str = ""

class CookieProfileReq(BaseModel):
    page_id: str
    profile_name: str

# --- Cookie Management ---
@app.post("/api/cookies/save")
async def save_cookies(req: CookieProfileReq):
    """Save cookies from a page's context to a named profile"""
    if req.page_id not in contexts:
        raise HTTPException(404, "Page not found")
    ctx = contexts[req.page_id]
    cookies = await ctx.cookies()
    path = COOKIES_DIR / f"{req.profile_name}.json"
    path.write_text(json.dumps(cookies, ensure_ascii=False, indent=2))
    log_action(req.page_id, "cookies_save", f"Saved {len(cookies)} cookies → {req.profile_name}")
    return {"ok": True, "count": len(cookies), "profile": req.profile_name}

@app.post("/api/cookies/load")
async def load_cookies(req: CookieProfileReq):
    """Load cookies from a named profile into a page's context"""
    if req.page_id not in contexts:
        raise HTTPException(404, "Page not found")
    path = COOKIES_DIR / f"{req.profile_name}.json"
    if not path.exists():
        raise HTTPException(404, f"Cookie profile '{req.profile_name}' not found")
    cookies = json.loads(path.read_text())
    ctx = contexts[req.page_id]
    await ctx.add_cookies(cookies)
    log_action(req.page_id, "cookies_load", f"Loaded {len(cookies)} cookies ← {req.profile_name}")
    return {"ok": True, "count": len(cookies), "profile": req.profile_name}

@app.get("/api/cookies/profiles")
async def list_cookie_profiles():
    """List saved cookie profiles"""
    profiles = []
    for f in COOKIES_DIR.glob("*.json"):
        cookies = json.loads(f.read_text())
        profiles.append({"name": f.stem, "count": len(cookies), "size": f.stat().st_size})
    return profiles

@app.delete("/api/cookies/profiles/{name}")
async def delete_cookie_profile(name: str):
    path = COOKIES_DIR / f"{name}.json"
    if path.exists(): path.unlink()
    return {"ok": True}

# --- Task Save/Load ---
@app.post("/api/tasks/save")
async def save_task(req: SaveTaskReq):
    """Save a task script to disk"""
    task_data = {"name": req.name, "description": req.description,
                 "steps": [s.model_dump() for s in req.steps], "created_at": time.time()}
    path = TASKS_DIR / f"{req.name}.json"
    path.write_text(json.dumps(task_data, ensure_ascii=False, indent=2))
    log_action("system", "task_save", f"Saved task: {req.name}")
    return {"ok": True, "name": req.name}

@app.get("/api/tasks/saved")
async def list_saved_tasks():
    """List saved task scripts"""
    tasks = []
    for f in TASKS_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text())
            tasks.append({"name": data.get("name", f.stem), "description": data.get("description", ""),
                          "steps_count": len(data.get("steps", [])), "created_at": data.get("created_at", 0)})
        except: pass
    return sorted(tasks, key=lambda t: t["created_at"], reverse=True)

@app.get("/api/tasks/saved/{name}")
async def get_saved_task(name: str):
    path = TASKS_DIR / f"{name}.json"
    if not path.exists():
        raise HTTPException(404, "Task not found")
    return json.loads(path.read_text())

@app.delete("/api/tasks/saved/{name}")
async def delete_saved_task(name: str):
    path = TASKS_DIR / f"{name}.json"
    if path.exists(): path.unlink()
    return {"ok": True}

# --- Logs ---
@app.get("/api/logs")
async def get_logs(limit: int = 50):
    return task_logs[-limit:]

# --- Serve Frontend ---
@app.get("/")
async def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8901)
