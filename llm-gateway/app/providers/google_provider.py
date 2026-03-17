"""Google Gemini provider — translates between OpenAI format and Gemini API."""
import json
import time
import uuid
from typing import AsyncIterator
from app.providers.base import BaseProvider
from app.models.schemas import (
    ChatCompletionRequest, ChatCompletionResponse,
    ChatChoice, ChatMessage, Usage,
)


class GoogleProvider(BaseProvider):
    name = "google"

    def __init__(self, api_key: str, base_url: str = "https://generativelanguage.googleapis.com/v1beta"):
        super().__init__(api_key, base_url)

    def _convert_messages(self, messages: list[ChatMessage]) -> tuple[str, list[dict]]:
        """Convert to Gemini format."""
        system = ""
        contents = []
        for m in messages:
            if m.role == "system":
                system = m.content or ""
            else:
                role = "user" if m.role == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": m.content or ""}],
                })
        return system, contents

    async def chat_completion(self, req: ChatCompletionRequest) -> ChatCompletionResponse:
        system, contents = self._convert_messages(req.messages)
        body = {"contents": contents}
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}

        gen_config = {}
        if req.temperature is not None:
            gen_config["temperature"] = req.temperature
        if req.top_p is not None:
            gen_config["topP"] = req.top_p
        if req.max_tokens is not None:
            gen_config["maxOutputTokens"] = req.max_tokens
        if req.stop:
            gen_config["stopSequences"] = req.stop if isinstance(req.stop, list) else [req.stop]
        if gen_config:
            body["generationConfig"] = gen_config

        resp = await self.client.post(
            f"{self.base_url}/models/{req.model}:generateContent?key={self.api_key}",
            json=body,
        )
        resp.raise_for_status()
        data = resp.json()

        # Extract text from Gemini response
        content = ""
        candidates = data.get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            content = "".join(p.get("text", "") for p in parts)

        usage_meta = data.get("usageMetadata", {})
        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:12]}",
            created=int(time.time()),
            model=req.model,
            choices=[
                ChatChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=content),
                    finish_reason="stop",
                )
            ],
            usage=Usage(
                prompt_tokens=usage_meta.get("promptTokenCount", 0),
                completion_tokens=usage_meta.get("candidatesTokenCount", 0),
                total_tokens=usage_meta.get("totalTokenCount", 0),
            ),
        )

    async def chat_completion_stream(self, req: ChatCompletionRequest) -> AsyncIterator[str]:
        system, contents = self._convert_messages(req.messages)
        body = {"contents": contents}
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}

        gen_config = {}
        if req.temperature is not None:
            gen_config["temperature"] = req.temperature
        if req.max_tokens is not None:
            gen_config["maxOutputTokens"] = req.max_tokens
        if gen_config:
            body["generationConfig"] = gen_config

        async with self.client.stream(
            "POST",
            f"{self.base_url}/models/{req.model}:streamGenerateContent?alt=sse&key={self.api_key}",
            json=body,
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                raw = line[6:]
                try:
                    event = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                candidates = event.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    text = "".join(p.get("text", "") for p in parts)
                    if text:
                        chunk = {
                            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": req.model,
                            "choices": [{
                                "index": 0,
                                "delta": {"content": text},
                                "finish_reason": None,
                            }],
                        }
                        yield f"data: {json.dumps(chunk)}\n\n"
            yield "data: [DONE]\n\n"
