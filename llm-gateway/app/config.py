from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Server
    gateway_port: int = 8800
    gateway_host: str = "0.0.0.0"
    gateway_secret: str = "change-me"

    # Provider API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/gateway.db"

    # Pricing (per 1M tokens, USD)
    # Updated regularly - these are defaults
    model_config_extra: dict = {}

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Model pricing database (input_price, output_price per 1M tokens in USD)
MODEL_PRICING = {
    # OpenAI
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4-turbo": (10.00, 30.00),
    "gpt-4": (30.00, 60.00),
    "gpt-3.5-turbo": (0.50, 1.50),
    "o1": (15.00, 60.00),
    "o1-mini": (3.00, 12.00),
    "o3-mini": (1.10, 4.40),
    # Anthropic
    "claude-3-5-sonnet-20241022": (3.00, 15.00),
    "claude-3-5-haiku-20241022": (0.80, 4.00),
    "claude-3-opus-20240229": (15.00, 75.00),
    "claude-3-sonnet-20240229": (3.00, 15.00),
    "claude-3-haiku-20240307": (0.25, 1.25),
    # Google
    "gemini-1.5-pro": (1.25, 5.00),
    "gemini-1.5-flash": (0.075, 0.30),
    "gemini-2.0-flash": (0.10, 0.40),
    # DeepSeek
    "deepseek-chat": (0.14, 0.28),
    "deepseek-reasoner": (0.55, 2.19),
}


def get_model_price(model: str) -> tuple[float, float]:
    """Get (input_price, output_price) per 1M tokens. Returns (0,0) if unknown."""
    # Try exact match first
    if model in MODEL_PRICING:
        return MODEL_PRICING[model]
    # Try prefix match (e.g., "gpt-4o-2024-08-06" -> "gpt-4o")
    for key in sorted(MODEL_PRICING.keys(), key=len, reverse=True):
        if model.startswith(key):
            return MODEL_PRICING[key]
    return (0.0, 0.0)
