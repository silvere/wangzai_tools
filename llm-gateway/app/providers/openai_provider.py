"""OpenAI provider — also handles DeepSeek and other OpenAI-compatible APIs."""
import json
import time
import uuid
from typing import AsyncIterator
from app.providers.base import BaseProvider
from app.models.schemas import (
    ChatCompletionRequest, ChatCompletionResponse,
    ChatChoice, ChatMessage, Usage,
)


class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        super().__init__(api_key, base_url)

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _build_body(self, req: ChatCompletionRequest) -> dict:
        body = {
            "model": req.model,
            "messages": [m.model_dump(exclude_none=True) for m in req.messages],
        }
        if req.temperature is not None:
            body["temperature"] = req.temperature
        if req.top_p is not None:
            body["top_p"] = req.top_p
        if req.max_tokens is not None:
            body["max_tokens"] = req.max_tokens
        if req.stream:
            body["stream"] = True
        if req.stop:
            body["stop"] = req.stop
        if req.presence_penalty is not None:
            body["presence_penalty"] = req.presence_penalty
        if req.frequency_penalty is not None:
            body["frequency_penalty"] = req.frequency_penalty
        return body

    async def chat_completion(self, req: ChatCompletionRequest) -> ChatCompletionResponse:
        resp = await self.client.post(
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            json=self._build_body(req),
        )
        resp.raise_for_status()
        data = resp.json()
        return ChatCompletionResponse(
            id=data.get("id", f"chatcmpl-{uuid.uuid4().hex[:12]}"),
            created=data.get("created", int(time.time())),
            model=data.get("model", req.model),
            choices=[
                ChatChoice(
                    index=c.get("index", 0),
                    message=ChatMessage(**c["message"]),
                    finish_reason=c.get("finish_reason", "stop"),
                )
                for c in data.get("choices", [])
            ],
            usage=Usage(**data.get("usage", {})),
        )

    async def chat_completion_stream(self, req: ChatCompletionRequest) -> AsyncIterator[str]:
        req_body = self._build_body(req)
        req_body["stream"] = True
        async with self.client.stream(
            "POST",
            f"{self.base_url}/chat/completions",
            headers=self._headers(),
            json=req_body,
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    yield line + "\n\n"
                    if line.strip() == "data: [DONE]":
                        break


class DeepSeekProvider(OpenAIProvider):
    """DeepSeek uses OpenAI-compatible API."""
    name = "deepseek"

    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com/v1"):
        super().__init__(api_key, base_url)
