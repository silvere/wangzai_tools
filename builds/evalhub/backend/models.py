"""EvalHub 数据模型"""
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
import time, uuid

class ModelProvider(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    name: str
    api_base: str  # e.g. https://api.openai.com/v1
    api_key: str
    model_id: str  # e.g. gpt-4o
    created_at: float = Field(default_factory=time.time)

class TaskStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"

class EvalTask(BaseModel):
    id: str = Field(default_factory=lambda: uuid.uuid4().hex[:8])
    model_id: str       # reference to ModelProvider.id
    dataset_id: str     # e.g. "truthfulqa_mc"
    status: TaskStatus = TaskStatus.pending
    progress: int = 0   # 0-100
    total: int = 0
    correct: int = 0
    score: float = 0.0
    results: list = Field(default_factory=list)  # per-question results
    created_at: float = Field(default_factory=time.time)
    finished_at: Optional[float] = None
    error: Optional[str] = None

class DatasetInfo(BaseModel):
    id: str
    name: str
    description: str
    category: str
    num_questions: int
    metrics: list[str]

class EvalRequest(BaseModel):
    model_id: str
    dataset_id: str

class QuestionResult(BaseModel):
    question: str
    choices: list[str]
    correct_idx: int
    model_answer_idx: int
    is_correct: bool
    category: str = ""
