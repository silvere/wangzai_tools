"""
Base provider interface and provider registry.
All providers translate to/from OpenAI-compatible format.
"""
import httpx
import time
from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional
from app.models.schemas import ChatCompletionRequest, ChatCompletionResponse


class BaseProvider(ABC):
    """Base class for LLM API providers."""

    name: str = "base"

    def __init__(self, api_key: str, base_url: str = ""):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=120.0)

    @abstractmethod
    async def chat_completion(
        self, request: ChatCompletionRequest
    ) -> ChatCompletionResponse:
        """Send a chat completion request and return OpenAI-compatible response."""
        pass

    @abstractmethod
    async def chat_completion_stream(
        self, request: ChatCompletionRequest
    ) -> AsyncIterator[str]:
        """Send a streaming chat completion request, yield SSE chunks."""
        pass

    async def close(self):
        await self.client.aclose()


class ProviderRegistry:
    """Registry of available providers and model routing."""

    def __init__(self):
        self._providers: dict[str, BaseProvider] = {}
        self._model_map: dict[str, str] = {}  # model -> provider_name

    def register(self, provider: BaseProvider, models: list[str]):
        self._providers[provider.name] = provider
        for model in models:
            self._model_map[model] = provider.name

    def get_provider(self, model: str) -> Optional[BaseProvider]:
        """Get the provider for a given model name."""
        # Exact match
        if model in self._model_map:
            return self._providers[self._model_map[model]]
        # Prefix match (e.g., "gpt-4o-2024-08-06" -> openai)
        for key, pname in self._model_map.items():
            if model.startswith(key):
                return self._providers[pname]
        return None

    def list_models(self) -> list[dict]:
        """List all available models."""
        result = []
        for model, pname in sorted(self._model_map.items()):
            result.append({"id": model, "provider": pname})
        return result

    async def close_all(self):
        for p in self._providers.values():
            await p.close()


registry = ProviderRegistry()
