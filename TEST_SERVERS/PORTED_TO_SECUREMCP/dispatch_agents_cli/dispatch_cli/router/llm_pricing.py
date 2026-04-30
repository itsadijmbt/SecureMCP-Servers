"""LLM model pricing for local development.

Provides cost calculation using a static fallback pricing table.
This is simpler than the backend implementation since local dev
doesn't need dynamic pricing fetching.

Pricing is stored in USD per 1 million tokens internally.
"""

from typing import TypedDict


class ModelPricing(TypedDict):
    """Pricing for a single model."""

    input: float  # USD per 1M input tokens
    output: float  # USD per 1M output tokens


# Fallback pricing for unknown models
# Uses a moderate estimate - similar to GPT-4o pricing
DEFAULT_PRICING: ModelPricing = {"input": 2.50, "output": 10.00}

# Static pricing table for common models
# Kept in sync with backend/infrastructure/llm/pricing.py
PRICING_TABLE: dict[str, ModelPricing] = {
    # OpenAI - GPT-5 series
    "gpt-5": {"input": 1.375, "output": 11.00},
    "gpt-5-mini": {"input": 0.275, "output": 2.20},
    "gpt-5-nano": {"input": 0.055, "output": 0.44},
    "gpt-5.2": {"input": 2.00, "output": 8.00},
    # OpenAI - GPT-4.1 series
    "gpt-4.1": {"input": 2.00, "output": 8.00},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    "gpt-4.1-nano": {"input": 0.10, "output": 0.40},
    # OpenAI - GPT-4o series
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.165, "output": 0.66},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    # OpenAI - Reasoning models
    "o1": {"input": 16.50, "output": 66.00},
    "o1-mini": {"input": 1.21, "output": 4.84},
    "o3-mini": {"input": 1.21, "output": 4.84},
    # Anthropic - Claude 4
    "claude-opus-4-5": {"input": 5.00, "output": 25.00},
    "claude-opus-4-6": {"input": 15.00, "output": 75.00},
    "claude-opus-4-1": {"input": 15.00, "output": 75.00},
    "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
    "claude-sonnet-4": {"input": 3.00, "output": 15.00},
    # Anthropic - Claude 3.x
    "claude-3-7-sonnet": {"input": 3.60, "output": 18.00},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-5-haiku": {"input": 1.00, "output": 5.00},
    "claude-3-haiku": {"input": 0.25, "output": 1.25},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    # Google Gemini
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
    # DeepSeek
    "deepseek-chat": {"input": 0.14, "output": 0.28},
    "deepseek-reasoner": {"input": 0.55, "output": 2.19},
}


def normalize_model_name(model: str) -> str:
    """Normalize model name for pricing lookup.

    Only strips provider prefix if present - no aliases or fuzzy matching.
    Users should use canonical model names as expected by the provider APIs.

    Args:
        model: Model name (may include provider prefix like "openai::gpt-4o")

    Returns:
        Model name with provider prefix stripped
    """
    # Remove provider prefix if present (e.g., "openai::gpt-4o" -> "gpt-4o")
    if "::" in model:
        model = model.split("::")[-1]

    return model


def get_model_pricing(model: str) -> ModelPricing:
    """Get pricing for a model.

    Uses exact match against PRICING_TABLE. For unknown models, returns
    DEFAULT_PRICING rather than failing - this allows cost tracking even
    for new models not yet in our pricing table.

    Args:
        model: Model name (canonical format, e.g., "gpt-4o", "claude-3-5-sonnet-20241022")

    Returns:
        ModelPricing dict with input and output costs per 1M tokens
    """
    normalized = normalize_model_name(model)

    if normalized in PRICING_TABLE:
        return PRICING_TABLE[normalized]

    return DEFAULT_PRICING


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate the cost of an LLM call in USD.

    Args:
        model: Model name (e.g., "gpt-4o", "claude-3-5-sonnet-20241022")
        input_tokens: Number of input/prompt tokens
        output_tokens: Number of output/completion tokens

    Returns:
        Cost in USD, rounded to 6 decimal places

    Example:
        >>> calculate_cost("gpt-4o", input_tokens=1000, output_tokens=500)
        0.0075  # $2.50/1M input + $10/1M output
    """
    pricing = get_model_pricing(model)
    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return round(input_cost + output_cost, 6)
