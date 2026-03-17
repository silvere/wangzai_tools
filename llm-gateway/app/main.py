"""LLM Gateway — main application entry point."""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import init_db
from app.routers import chat, admin
from app.providers.base import registry
from app.providers.openai_provider import OpenAIProvider, DeepSeekProvider
from app.providers.anthropic_provider import AnthropicProvider
from app.providers.google_provider import GoogleProvider


def setup_providers():
    """Register all configured providers."""
    if settings.openai_api_key:
        provider = OpenAIProvider(api_key=settings.openai_api_key)
        registry.register(provider, [
            "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4",
            "gpt-3.5-turbo", "o1", "o1-mini", "o3-mini",
        ])
        print(f"  ✓ OpenAI registered ({len([k for k in registry._model_map if registry._model_map[k]=='openai'])} models)")

    if settings.anthropic_api_key:
        provider = AnthropicProvider(api_key=settings.anthropic_api_key)
        registry.register(provider, [
            "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229", "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ])
        print(f"  ✓ Anthropic registered ({len([k for k in registry._model_map if registry._model_map[k]=='anthropic'])} models)")

    if settings.google_api_key:
        provider = GoogleProvider(api_key=settings.google_api_key)
        registry.register(provider, [
            "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash",
        ])
        print(f"  ✓ Google registered ({len([k for k in registry._model_map if registry._model_map[k]=='google'])} models)")

    if settings.deepseek_api_key:
        provider = DeepSeekProvider(api_key=settings.deepseek_api_key)
        registry.register(provider, ["deepseek-chat", "deepseek-reasoner"])
        print(f"  ✓ DeepSeek registered (2 models)")

    total = len(registry._model_map)
    print(f"\n  Total: {total} models available\n")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("\n🚀 LLM Gateway starting...\n")
    await init_db()
    setup_providers()

    # Auto-create a default token if none exist
    from app.auth import list_tokens, create_token
    tokens = await list_tokens()
    if not tokens:
        token = await create_token("default")
        print(f"  🔑 Default access token created: {token}\n")
        print(f"  Use this in your API calls:")
        print(f"  Authorization: Bearer {token}\n")

    print(f"  Admin secret: {settings.gateway_secret}")
    print(f"  Dashboard: http://localhost:{settings.gateway_port}\n")

    yield

    # Shutdown
    await registry.close_all()
    print("\n👋 LLM Gateway stopped.\n")


app = FastAPI(
    title="LLM Gateway",
    description="统一多模型 API 网关",
    version="0.1.0",
    lifespan=lifespan,
)

# Routers
app.include_router(chat.router)
app.include_router(admin.router)

# Static files for dashboard
import os
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
async def root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "name": "LLM Gateway",
        "version": "0.1.0",
        "docs": "/docs",
        "models": "/v1/models",
    }


@app.get("/health")
async def health():
    return {"status": "ok", "models": len(registry._model_map)}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.gateway_host,
        port=settings.gateway_port,
        reload=True,
    )
