"""Chat completions API — OpenAI-compatible endpoint."""
import time
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatCompletionRequest
from app.providers.base import registry
from app.auth import verify_token
from app.database import log_request
from app.config import get_model_price

router = APIRouter()


@router.post("/v1/chat/completions")
async def chat_completions(request: Request, body: ChatCompletionRequest):
    # Auth
    token_name = await verify_token(request)

    # Find provider
    provider = registry.get_provider(body.model)
    if not provider:
        raise HTTPException(
            status_code=400,
            detail=f"Model '{body.model}' not found. Use GET /v1/models to list available models."
        )

    start = time.time()

    # Streaming
    if body.stream:
        async def stream_gen():
            try:
                total_chunks = 0
                async for chunk in provider.chat_completion_stream(body):
                    total_chunks += 1
                    yield chunk
                # Log approximate usage for streaming (tokens not exact)
                latency = int((time.time() - start) * 1000)
                await log_request(
                    token_name=token_name, model=body.model, provider=provider.name,
                    prompt_tokens=0, completion_tokens=0,
                    input_cost=0, output_cost=0,
                    latency_ms=latency, status="ok"
                )
            except Exception as e:
                latency = int((time.time() - start) * 1000)
                await log_request(
                    token_name=token_name, model=body.model, provider=provider.name,
                    prompt_tokens=0, completion_tokens=0,
                    input_cost=0, output_cost=0,
                    latency_ms=latency, status="error", error=str(e)
                )
                yield f"data: {{}}\n\n"

        return StreamingResponse(stream_gen(), media_type="text/event-stream")

    # Non-streaming
    try:
        resp = await provider.chat_completion(body)
        latency = int((time.time() - start) * 1000)

        # Calculate cost
        input_price, output_price = get_model_price(body.model)
        input_cost = resp.usage.prompt_tokens * input_price / 1_000_000
        output_cost = resp.usage.completion_tokens * output_price / 1_000_000

        await log_request(
            token_name=token_name, model=body.model, provider=provider.name,
            prompt_tokens=resp.usage.prompt_tokens,
            completion_tokens=resp.usage.completion_tokens,
            input_cost=input_cost, output_cost=output_cost,
            latency_ms=latency, status="ok"
        )
        return resp

    except HTTPException:
        raise
    except Exception as e:
        latency = int((time.time() - start) * 1000)
        await log_request(
            token_name=token_name, model=body.model, provider=provider.name,
            prompt_tokens=0, completion_tokens=0,
            input_cost=0, output_cost=0,
            latency_ms=latency, status="error", error=str(e)
        )
        raise HTTPException(status_code=502, detail=f"Provider error: {str(e)}")


@router.get("/v1/models")
async def list_models():
    models = registry.list_models()
    return {
        "object": "list",
        "data": [
            {"id": m["id"], "object": "model", "owned_by": m["provider"]}
            for m in models
        ],
    }
