from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


# --- OpenAI-compatible request/response models ---

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: Optional[str] = None
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    stop: Optional[str | list[str]] = None
    presence_penalty: Optional[float] = None
    frequency_penalty: Optional[float] = None
    user: Optional[str] = None


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatChoice(BaseModel):
    index: int = 0
    message: ChatMessage
    finish_reason: Optional[str] = "stop"


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatChoice]
    usage: Usage


# --- Gateway internal models ---

class ProviderConfig(BaseModel):
    name: str
    api_key: Optional[str] = None
    base_url: str
    models: list[str] = []
    enabled: bool = True


class AccessToken(BaseModel):
    token: str
    name: str
    created_at: datetime
    enabled: bool = True
    rate_limit: Optional[int] = None  # requests per minute


class RequestLog(BaseModel):
    id: Optional[int] = None
    timestamp: datetime
    token_name: str
    model: str
    provider: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    latency_ms: int
    status: str
    error: Optional[str] = None
