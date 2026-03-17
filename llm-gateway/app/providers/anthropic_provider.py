"""Anthropic provider — translates between OpenAI format and Anthropic Messages API."""
import json
import time
import uuid
from typing import AsyncIterator
from app.providers.base import BaseProvider
from app.models.schemas import (
    ChatCompletionRequest, ChatCompletionResponse,
    ChatChoice, ChatMessage, Usage,
)


class AnthropicProvider(BaseProvider):
    name = "anthropic"

    def __init__(self, api_key: str, base_url: str = "https://api.anthropic.com"):
        super().__init__(api_key, base_url)

    def _headers(self):
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    def _convert_messages(self, messages: list[ChatMessage]) -> tuple[str, list[dict]]:
        """Extract system prompt and convert messages to Anthropic format."""
        system = ""
        converted = []
        for m in messages:
            if m.role == "system":
                system = m.content or ""
            else:
                role = "user" if m.role == "user" else "assistant"
                converted.append({"role": role, "content": m.content or ""})
        # Anthropic requires alternating user/assistant, merge consecutive same-role
        if not converted:
            converted = [{"role": "user", "content": "Hello"}]
        return system, converted

    async def chat_completion(self, req: ChatCompletionRequest) -> ChatCompletionResponse:
        system, messages = self._convert_messages(req.messages)
        body = {
            "model": req.model,
            "messages": messages,
            "max_tokens": req.max_tokens or 4096,
        }
        if system:
            body["system"] = system
        if req.temperature is not None:
            body["temperature"] = req.temperature
        if req.top_p is not None:
            body["top_p"] = req.top_p
        if req.stop:
            body["stop_sequences"] = req.stop if isinstance(req.stop, list) else [req.stop]

        resp = await self.client.post(
            f"{self.base_url}/v1/messages",
            headers=self._headers(),
            json=body,
        )
        resp.raise_for_status()
        data = resp.json()

        # Convert Anthropic response to OpenAI format
        content = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")

        usage_data = data.get("usage", {})
        return ChatCompletionResponse(
            id=data.get("id", f"chatcmpl-{uuid.uuid4().hex[:12]}"),
            created=int(time.time()),
            model=data.get("model", req.model),
            choices=[
                ChatChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=content),
                    finish_reason=_map_stop_reason(data.get("stop_reason", "end_turn")),
                )
            ],
            usage=Usage(
                prompt_tokens=usage_data.get("input_tokens", 0),
                completion_tokens=usage_data.get("output_tokens", 0),
                total_tokens=usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0),
            ),
        )

    async def chat_completion_stream(self, req: ChatCompletionRequest) -> AsyncIterator[str]:
        system, messages = self._convert_messages(req.messages)
        body = {
            "model": req.model,
            "messages": messages,
            "max_tokens": req.max_tokens or 4096,
            "stream": True,
        }
        if system:
            body["system"] = system
        if req.temperature is not None:
            body["temperature"] = req.temperature

        async with self.client.stream(
            "POST",
            f"{self.base_url}/v1/messages",
            headers=self._headers(),
            json=body,
        ) as resp:
            resp.raise_for_status()
            collected_text = ""
            input_tokens = 0
            output_tokens = 0

            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                raw = line[6:]
                if raw.strip() == "[DONE]":
                    break
                try:
                    event = json.loads(raw)
                except json.JSONDecodeError:
                    continue

                etype = event.get("type", "")
                if etype == "content_block_delta":
                    delta_text = event.get("delta", {}).get("text", "")
                    if delta_text:
                        # Convert to OpenAI SSE format
                        chunk = {
                            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": req.model,
                            "choices": [{
                                "index": 0,
                                "delta": {"content": delta_text},
                                "finish_reason": None,
                            }],
                        }
                        yield f"data: {json.dumps(chunk)}\n\n"
                elif etype == "message_stop":
                    yield "data: [DONE]\n\n"


def _map_stop_reason(reason: str) -> str:
    mapping = {
        "end_turn": "stop",
        "max_tokens": "length",
        "stop_sequence": "stop",
    }
    return mapping.get(reason, "stop")
