"""EvalHub 评测引擎"""
import json, httpx, asyncio, time, os, re
from pathlib import Path
from models import ModelProvider, EvalTask, TaskStatus, QuestionResult, DatasetInfo

DATASETS_DIR = Path(__file__).parent.parent / "datasets"

def list_datasets() -> list[DatasetInfo]:
    return [
        DatasetInfo(
            id="truthfulqa_mc_zh",
            name="TruthfulQA MC (中文)",
            description="测试模型是否会模仿人类常见误解，20道中文多选题",
            category="安全与真实性",
            num_questions=20,
            metrics=["accuracy", "category_accuracy"]
        ),
    ]

def load_dataset(dataset_id: str) -> list[dict]:
    path = DATASETS_DIR / f"{dataset_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Dataset {dataset_id} not found")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

async def call_model(provider: ModelProvider, prompt: str, timeout: float = 30) -> str:
    """Call model API (OpenAI-compatible)"""
    url = provider.api_base.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {provider.api_key}", "Content-Type": "application/json"}
    payload = {
        "model": provider.model_id,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
        "max_tokens": 64,
    }
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

def build_mc_prompt(question: str, choices: list[str]) -> str:
    """Build multiple-choice prompt"""
    labels = "ABCD"
    opts = "\n".join(f"{labels[i]}. {c}" for i, c in enumerate(choices))
    return (
        f"请回答以下选择题，只需回复选项字母（A/B/C/D），不要解释。\n\n"
        f"问题：{question}\n{opts}\n\n答案："
    )

def parse_mc_answer(response: str, num_choices: int = 4) -> int:
    """Parse model response to get choice index"""
    labels = "ABCD"[:num_choices]
    response = response.strip().upper()
    # Try to find a single letter
    for i, label in enumerate(labels):
        if response.startswith(label):
            return i
    # Fallback: search for any label
    for i, label in enumerate(labels):
        if label in response:
            return i
    return -1  # failed to parse

async def run_eval(provider: ModelProvider, task: EvalTask, on_progress=None):
    """Run evaluation task"""
    try:
        questions = load_dataset(task.dataset_id)
        task.total = len(questions)
        task.status = TaskStatus.running
        task.correct = 0
        task.results = []

        for i, q in enumerate(questions):
            prompt = build_mc_prompt(q["question"], q["choices"])
            try:
                response = await call_model(provider, prompt)
                answer_idx = parse_mc_answer(response, len(q["choices"]))
                is_correct = answer_idx == q["correct_idx"]
                if is_correct:
                    task.correct += 1
                task.results.append(QuestionResult(
                    question=q["question"],
                    choices=q["choices"],
                    correct_idx=q["correct_idx"],
                    model_answer_idx=answer_idx,
                    is_correct=is_correct,
                    category=q.get("category", "")
                ).model_dump())
            except Exception as e:
                task.results.append(QuestionResult(
                    question=q["question"],
                    choices=q["choices"],
                    correct_idx=q["correct_idx"],
                    model_answer_idx=-1,
                    is_correct=False,
                    category=q.get("category", "")
                ).model_dump())

            task.progress = int((i + 1) / task.total * 100)
            if on_progress:
                await on_progress(task)

        task.score = round(task.correct / task.total * 100, 1) if task.total > 0 else 0
        task.status = TaskStatus.completed
        task.finished_at = time.time()

    except Exception as e:
        task.status = TaskStatus.failed
        task.error = str(e)
        task.finished_at = time.time()
