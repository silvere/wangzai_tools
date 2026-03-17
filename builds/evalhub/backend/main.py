"""EvalHub 评测工坊 — FastAPI 后端"""
import asyncio, json, time
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from models import ModelProvider, EvalTask, TaskStatus, EvalRequest
from evaluator import list_datasets, run_eval

# In-memory store (V0.1 — will move to SQLite later)
models_store: dict[str, ModelProvider] = {}
tasks_store: dict[str, EvalTask] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 EvalHub V0.1 启动")
    yield
    print("👋 EvalHub 关闭")

app = FastAPI(title="EvalHub 评测工坊", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

# --- Model Management ---
@app.post("/api/models")
async def add_model(model: ModelProvider):
    models_store[model.id] = model
    return {"id": model.id, "name": model.name}

@app.get("/api/models")
async def get_models():
    return [{"id": m.id, "name": m.name, "model_id": m.model_id, "api_base": m.api_base, "created_at": m.created_at}
            for m in models_store.values()]

@app.delete("/api/models/{model_id}")
async def delete_model(model_id: str):
    if model_id not in models_store:
        raise HTTPException(404, "Model not found")
    del models_store[model_id]
    return {"ok": True}

# --- Datasets ---
@app.get("/api/datasets")
async def get_datasets():
    return [d.model_dump() for d in list_datasets()]

# --- Evaluation ---
@app.post("/api/eval")
async def start_eval(req: EvalRequest):
    if req.model_id not in models_store:
        raise HTTPException(404, "Model not found")
    provider = models_store[req.model_id]
    task = EvalTask(model_id=req.model_id, dataset_id=req.dataset_id)
    tasks_store[task.id] = task
    # Run in background
    asyncio.create_task(_run_eval_bg(provider, task))
    return {"task_id": task.id}

async def _run_eval_bg(provider: ModelProvider, task: EvalTask):
    await run_eval(provider, task)

@app.get("/api/tasks")
async def get_tasks():
    return [_task_summary(t) for t in sorted(tasks_store.values(), key=lambda t: t.created_at, reverse=True)]

@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    if task_id not in tasks_store:
        raise HTTPException(404, "Task not found")
    t = tasks_store[task_id]
    model = models_store.get(t.model_id)
    data = t.model_dump()
    data["model_name"] = model.name if model else "unknown"
    return data

def _task_summary(t: EvalTask) -> dict:
    model = models_store.get(t.model_id)
    return {
        "id": t.id, "model_id": t.model_id,
        "model_name": model.name if model else "unknown",
        "dataset_id": t.dataset_id, "status": t.status,
        "progress": t.progress, "score": t.score,
        "correct": t.correct, "total": t.total,
        "created_at": t.created_at, "finished_at": t.finished_at
    }

# --- Leaderboard ---
@app.get("/api/leaderboard")
async def leaderboard():
    completed = [t for t in tasks_store.values() if t.status == TaskStatus.completed]
    # Group by model, take best score per dataset
    board = {}
    for t in completed:
        model = models_store.get(t.model_id)
        key = f"{t.model_id}_{t.dataset_id}"
        if key not in board or t.score > board[key]["score"]:
            board[key] = {
                "model_name": model.name if model else "unknown",
                "model_id": t.model_id,
                "dataset_id": t.dataset_id,
                "score": t.score,
                "correct": t.correct,
                "total": t.total,
                "finished_at": t.finished_at
            }
    return sorted(board.values(), key=lambda x: x["score"], reverse=True)

# --- Serve Frontend ---
@app.get("/")
async def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8900)
