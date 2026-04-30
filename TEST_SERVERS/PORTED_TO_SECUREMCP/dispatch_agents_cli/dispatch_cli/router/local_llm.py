"""Local LLM provider implementations for development mode.

Provides direct HTTP calls to LLM providers (OpenAI, Anthropic, Google)
without requiring backend infrastructure.

API keys can be configured via (in order of precedence):
1. Environment variables
2. `dispatch secret local add <KEY>` (stores in macOS Keychain)
3. ~/.dispatch/secrets.yaml (raw values, warns on access)

Required keys by provider:
- OPENAI_API_KEY for OpenAI models (gpt-*)
- ANTHROPIC_API_KEY for Anthropic models (claude-*)
- GOOGLE_API_KEY for Google models (gemini-*)
"""

import json
import os
from typing import Any

import httpx
from dispatch_agents.llm import LLMFunctionCall, LLMToolCall

from dispatch_cli.logger import get_logger
from dispatch_cli.router.models import LLMProviderResult

logger = get_logger()

# Provider -> environment variable mapping
PROVIDER_ENV_VARS: dict[str, str] = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
    "azure_openai": "AZURE_OPENAI_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "cohere": "COHERE_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}

# Supported providers (ones we have implementations for)
SUPPORTED_PROVIDERS = {"openai", "anthropic", "google"}


def get_popular_models_for_provider(provider: str, limit: int = 5) -> list[str]:
    """Get popular model names for a provider from the pricing table.

    Derives the list dynamically from llm_pricing.PRICING_TABLE so we have
    a single source of truth for model names.

    Args:
        provider: Provider name (openai, anthropic, google)
        limit: Maximum number of models to return

    Returns:
        List of model names for the provider
    """
    from dispatch_cli.router.llm_pricing import PRICING_TABLE

    # Map provider to model name prefixes for filtering
    provider_prefixes = {
        "openai": ("gpt-", "o1", "o3"),
        "anthropic": ("claude-",),
        "google": ("gemini-",),
    }

    prefixes = provider_prefixes.get(provider, ())
    if not prefixes:
        return []

    # Filter models from pricing table by prefix
    models = [
        model for model in PRICING_TABLE if any(model.startswith(p) for p in prefixes)
    ]

    # Sort to get a consistent order (prefer shorter/simpler names first)
    models.sort(key=lambda m: (len(m), m))

    return models[:limit]


def get_configured_providers() -> dict[str, bool]:
    """Check which LLM providers have API keys configured.

    Returns:
        Dict mapping provider name to whether it's configured.
    """
    result = {}
    for provider in SUPPORTED_PROVIDERS:
        env_var = PROVIDER_ENV_VARS.get(provider)
        if env_var:
            result[provider] = bool(os.environ.get(env_var))
    return result


def get_llm_status_message() -> tuple[bool, str]:
    """Get a status message about LLM provider configuration.

    Shows which LLM API keys are configured and WHERE each value comes from
    (macOS Keychain, environment variable, secrets.yaml, etc.).

    Returns:
        Tuple of (any_configured, message)
    """
    from dispatch_cli.secrets import get_secret_sources

    # Get the env var names for all providers
    env_vars = list(PROVIDER_ENV_VARS.values())

    # Get source info for each secret
    sources = get_secret_sources(required_secrets=env_vars)
    source_map = {s["name"]: s for s in sources}

    configured = get_configured_providers()
    any_configured = any(configured.values())

    lines = []
    for provider, is_configured in sorted(configured.items()):
        env_var = PROVIDER_ENV_VARS[provider]
        source_info = source_map.get(env_var, {})
        storage_type = source_info.get("storage_type")

        status = "✓" if is_configured else "✗"

        if is_configured and storage_type:
            lines.append(f"  {status} {provider.capitalize()} ← {storage_type}")
        elif is_configured:
            lines.append(f"  {status} {provider.capitalize()} ← environment variable")
        else:
            lines.append(f"  {status} {provider.capitalize()}: {env_var} (not set)")

    message = "\n".join(lines)
    return any_configured, message


class LocalLLMError(Exception):
    """Error from local LLM provider call."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def get_api_key(provider: str) -> str:
    """Get API key for a provider from environment.

    Args:
        provider: Provider name (e.g., "openai", "anthropic")

    Returns:
        API key from environment

    Raises:
        LocalLLMError: If API key is not set
    """
    env_var = PROVIDER_ENV_VARS.get(provider)
    if not env_var:
        raise LocalLLMError(f"Unknown provider: {provider}")

    api_key = os.environ.get(env_var)
    if not api_key:
        # Build helpful error with status of all providers
        _, status_msg = get_llm_status_message()
        configured = get_configured_providers()
        available = [p for p, is_set in configured.items() if is_set]

        error_lines = [
            f"Missing {env_var} for {provider} provider.",
            "",
            "LLM Provider Status:",
            status_msg,
            "",
        ]

        if available:
            error_lines.append(
                f"Tip: You can use models from configured providers: {', '.join(available)}"
            )
        else:
            error_lines.extend(
                [
                    "No LLM providers configured. Add API keys using:",
                    f"  dispatch secret local add {env_var}",
                    "",
                    "Or set as environment variable:",
                    f"  export {env_var}=your-api-key",
                    "",
                    "Then restart the router.",
                ]
            )

        raise LocalLLMError("\n".join(error_lines))

    return api_key


async def call_provider(
    *,
    provider: str,
    model: str,
    messages: list[dict[str, Any]],
    api_key: str,
    temperature: float = 1.0,
    max_tokens: int | None = None,
    tools: list[dict[str, Any]] | None = None,
    response_format: dict[str, Any] | None = None,
) -> LLMProviderResult:
    """Call the appropriate provider based on provider name.

    Args:
        provider: Provider name (openai, anthropic, google)
        model: Model name
        messages: List of message dicts with role/content
        api_key: API key for the provider
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        tools: Tool definitions for function calling
        response_format: Structured output format specification

    Returns:
        LLMProviderResult with: content, tool_calls, finish_reason, input_tokens, output_tokens

    Raises:
        LocalLLMError: If provider call fails
    """
    if provider == "openai":
        return await call_openai(
            messages=messages,
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            response_format=response_format,
        )
    elif provider == "anthropic":
        return await call_anthropic(
            messages=messages,
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
        )
    elif provider == "google":
        return await call_google(
            messages=messages,
            model=model,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    else:
        raise LocalLLMError(
            f"Provider '{provider}' is not yet supported in local dev mode. "
            f"Supported providers: openai, anthropic, google"
        )


async def call_openai(
    *,
    messages: list[dict[str, Any]],
    model: str,
    api_key: str,
    temperature: float = 1.0,
    max_tokens: int | None = None,
    tools: list[dict[str, Any]] | None = None,
    response_format: dict[str, Any] | None = None,
) -> LLMProviderResult:
    """Call OpenAI API directly.

    Args:
        messages: List of message dicts with role/content
        model: Model name (e.g., "gpt-4o")
        api_key: OpenAI API key
        temperature: Sampling temperature (0-2)
        max_tokens: Maximum tokens in response
        tools: Tool definitions for function calling
        response_format: Structured output format (json_object or json_schema)

    Returns:
        LLMProviderResult with: content, tool_calls, finish_reason, input_tokens, output_tokens
    """
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }

    if max_tokens is not None:
        payload["max_tokens"] = max_tokens
    if tools:
        payload["tools"] = tools
    if response_format:
        payload["response_format"] = response_format

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        except httpx.HTTPStatusError as e:
            error_body = e.response.text
            try:
                error_json = e.response.json()
                error_msg = error_json.get("error", {}).get("message", error_body)
            except Exception:
                error_msg = error_body

            if e.response.status_code == 401:
                raise LocalLLMError(
                    "Invalid OpenAI API key. Check your OPENAI_API_KEY in .env",
                    status_code=401,
                ) from e
            elif e.response.status_code == 429:
                raise LocalLLMError(
                    f"OpenAI rate limit exceeded: {error_msg}",
                    status_code=429,
                ) from e
            elif e.response.status_code == 404:
                # Model not found - provide helpful suggestions
                popular = get_popular_models_for_provider("openai", limit=5)
                model_suggestions = (
                    ", ".join(popular) if popular else "gpt-4o, gpt-4o-mini"
                )
                raise LocalLLMError(
                    f"Model '{model}' not found. "
                    f"Check the model name is correct.\n\n"
                    f"Popular OpenAI models: {model_suggestions}\n\n"
                    f"See https://platform.openai.com/docs/models for all available models.",
                    status_code=404,
                ) from e
            else:
                raise LocalLLMError(
                    f"OpenAI API error ({e.response.status_code}): {error_msg}",
                    status_code=e.response.status_code,
                ) from e

    choice = data["choices"][0]
    message = choice["message"]

    # Extract tool calls if present
    tool_calls: list[LLMToolCall] | None = None
    if message.get("tool_calls"):
        tool_calls = [
            LLMToolCall(
                id=tc["id"],
                type=tc["type"],
                function=LLMFunctionCall(
                    name=tc["function"]["name"],
                    arguments=tc["function"]["arguments"],
                ),
            )
            for tc in message["tool_calls"]
        ]

    return {
        "content": message.get("content"),
        "tool_calls": tool_calls,
        "finish_reason": choice["finish_reason"],
        "input_tokens": data["usage"]["prompt_tokens"],
        "output_tokens": data["usage"]["completion_tokens"],
    }


async def call_anthropic(
    *,
    messages: list[dict[str, Any]],
    model: str,
    api_key: str,
    temperature: float = 1.0,
    max_tokens: int | None = None,
    tools: list[dict[str, Any]] | None = None,
) -> LLMProviderResult:
    """Call Anthropic API directly.

    Handles conversion from OpenAI message format to Anthropic format:
    - System messages become the 'system' parameter
    - Tool definitions use Anthropic's format

    Args:
        messages: List of message dicts with role/content (OpenAI format)
        model: Model name (e.g., "claude-3-5-sonnet-20241022")
        api_key: Anthropic API key
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response (required by Anthropic, defaults to 4096)
        tools: Tool definitions for function calling (OpenAI format, will be converted)

    Returns:
        LLMProviderResult with: content, tool_calls, finish_reason, input_tokens, output_tokens
    """
    # Extract system message and convert remaining messages
    system_content: str | None = None
    anthropic_messages: list[dict[str, Any]] = []

    for msg in messages:
        if msg["role"] == "system":
            # Anthropic uses a separate system parameter
            system_content = msg["content"]
        elif msg["role"] == "tool":
            # Convert tool results to Anthropic format
            anthropic_messages.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": msg.get("tool_call_id", ""),
                            "content": msg["content"],
                        }
                    ],
                }
            )
        elif msg["role"] == "assistant" and msg.get("tool_calls"):
            # Convert assistant tool calls to Anthropic format
            content_blocks = []
            if msg.get("content"):
                content_blocks.append({"type": "text", "text": msg["content"]})
            for tc in msg["tool_calls"]:
                content_blocks.append(
                    {
                        "type": "tool_use",
                        "id": tc["id"],
                        "name": tc["function"]["name"],
                        "input": json.loads(tc["function"]["arguments"])
                        if isinstance(tc["function"]["arguments"], str)
                        else tc["function"]["arguments"],
                    }
                )
            anthropic_messages.append({"role": "assistant", "content": content_blocks})
        else:
            anthropic_messages.append({"role": msg["role"], "content": msg["content"]})

    # Build payload
    payload: dict[str, Any] = {
        "model": model,
        "messages": anthropic_messages,
        "max_tokens": max_tokens or 4096,  # Anthropic requires max_tokens
    }

    if system_content:
        payload["system"] = system_content
    if temperature != 1.0:
        payload["temperature"] = temperature
    if tools:
        # Convert OpenAI tool format to Anthropic format
        anthropic_tools = []
        for tool in tools:
            if tool.get("type") == "function":
                func = tool["function"]
                anthropic_tools.append(
                    {
                        "name": func["name"],
                        "description": func.get("description", ""),
                        "input_schema": func.get(
                            "parameters", {"type": "object", "properties": {}}
                        ),
                    }
                )
        if anthropic_tools:
            payload["tools"] = anthropic_tools

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        except httpx.HTTPStatusError as e:
            error_body = e.response.text
            try:
                error_json = e.response.json()
                error_msg = error_json.get("error", {}).get("message", error_body)
            except Exception:
                error_msg = error_body

            if e.response.status_code == 401:
                raise LocalLLMError(
                    "Invalid Anthropic API key. Check your ANTHROPIC_API_KEY in .env",
                    status_code=401,
                ) from e
            elif e.response.status_code == 429:
                raise LocalLLMError(
                    f"Anthropic rate limit exceeded: {error_msg}",
                    status_code=429,
                ) from e
            elif e.response.status_code == 404 or (
                e.response.status_code == 400 and "model" in error_msg.lower()
            ):
                # Model not found - provide helpful suggestions
                popular = get_popular_models_for_provider("anthropic", limit=3)
                model_suggestions = (
                    ", ".join(popular) if popular else "claude-3-5-sonnet-20241022"
                )
                raise LocalLLMError(
                    f"Model '{model}' not found. "
                    f"Check the model name is correct.\n\n"
                    f"Popular Anthropic models: {model_suggestions}\n\n"
                    f"See https://docs.anthropic.com/en/docs/about-claude/models for all available models.",
                    status_code=404,
                ) from e
            else:
                raise LocalLLMError(
                    f"Anthropic API error ({e.response.status_code}): {error_msg}",
                    status_code=e.response.status_code,
                ) from e

    # Extract content and tool calls from response
    content: str | None = None
    tool_calls: list[LLMToolCall] | None = None

    for block in data.get("content", []):
        if block["type"] == "text":
            content = block["text"]
        elif block["type"] == "tool_use":
            if tool_calls is None:
                tool_calls = []
            # Convert to OpenAI-compatible format
            tool_calls.append(
                LLMToolCall(
                    id=block["id"],
                    type="function",
                    function=LLMFunctionCall(
                        name=block["name"],
                        arguments=json.dumps(block["input"]),
                    ),
                )
            )

    # Map Anthropic stop_reason to OpenAI finish_reason
    stop_reason = data.get("stop_reason", "stop")
    finish_reason_map = {
        "end_turn": "stop",
        "max_tokens": "length",
        "stop_sequence": "stop",
        "tool_use": "tool_calls",
    }
    finish_reason = finish_reason_map.get(stop_reason, stop_reason)

    return {
        "content": content,
        "tool_calls": tool_calls,
        "finish_reason": finish_reason,
        "input_tokens": data["usage"]["input_tokens"],
        "output_tokens": data["usage"]["output_tokens"],
    }


async def call_google(
    *,
    messages: list[dict[str, Any]],
    model: str,
    api_key: str,
    temperature: float = 1.0,
    max_tokens: int | None = None,
) -> LLMProviderResult:
    """Call Google Gemini API directly.

    Converts OpenAI message format to Gemini format.

    Args:
        messages: List of message dicts with role/content (OpenAI format)
        model: Model name (e.g., "gemini-1.5-flash")
        api_key: Google API key
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response

    Returns:
        LLMProviderResult with: content, tool_calls, finish_reason, input_tokens, output_tokens
    """
    # Convert messages to Gemini format
    system_instruction: str | None = None
    gemini_contents: list[dict[str, Any]] = []

    for msg in messages:
        if msg["role"] == "system":
            system_instruction = msg["content"]
        elif msg["role"] == "user":
            gemini_contents.append(
                {
                    "role": "user",
                    "parts": [{"text": msg["content"]}],
                }
            )
        elif msg["role"] == "assistant":
            gemini_contents.append(
                {
                    "role": "model",
                    "parts": [{"text": msg["content"]}],
                }
            )

    # Build payload
    payload: dict[str, Any] = {
        "contents": gemini_contents,
        "generationConfig": {
            "temperature": temperature,
        },
    }

    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    if max_tokens:
        payload["generationConfig"]["maxOutputTokens"] = max_tokens

    # Gemini API uses model in URL and API key as query parameter
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                url,
                params={"key": api_key},
                headers={"Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        except httpx.HTTPStatusError as e:
            error_body = e.response.text
            try:
                error_json = e.response.json()
                error_msg = error_json.get("error", {}).get("message", error_body)
            except Exception:
                error_msg = error_body

            if e.response.status_code == 400 and "API_KEY" in error_msg.upper():
                raise LocalLLMError(
                    "Invalid Google API key. Check your GOOGLE_API_KEY in .env",
                    status_code=401,
                ) from e
            elif e.response.status_code == 429:
                raise LocalLLMError(
                    f"Google rate limit exceeded: {error_msg}",
                    status_code=429,
                ) from e
            elif e.response.status_code == 404 or (
                e.response.status_code == 400
                and ("model" in error_msg.lower() or "not found" in error_msg.lower())
            ):
                # Model not found - provide helpful suggestions
                popular = get_popular_models_for_provider("google", limit=3)
                model_suggestions = (
                    ", ".join(popular)
                    if popular
                    else "gemini-1.5-flash, gemini-1.5-pro"
                )
                raise LocalLLMError(
                    f"Model '{model}' not found. "
                    f"Check the model name is correct.\n\n"
                    f"Popular Google models: {model_suggestions}\n\n"
                    f"See https://ai.google.dev/models for all available models.",
                    status_code=404,
                ) from e
            else:
                raise LocalLLMError(
                    f"Google API error ({e.response.status_code}): {error_msg}",
                    status_code=e.response.status_code,
                ) from e

    # Extract response
    candidates = data.get("candidates", [])
    if not candidates:
        raise LocalLLMError("No response from Gemini API")

    candidate = candidates[0]
    content_parts = candidate.get("content", {}).get("parts", [])
    content = content_parts[0].get("text", "") if content_parts else ""

    # Map finish reason
    finish_reason_raw = candidate.get("finishReason", "STOP")
    finish_reason_map = {
        "STOP": "stop",
        "MAX_TOKENS": "length",
        "SAFETY": "content_filter",
        "RECITATION": "content_filter",
    }
    finish_reason = finish_reason_map.get(finish_reason_raw, "stop")

    # Extract usage metadata
    usage = data.get("usageMetadata", {})
    input_tokens = usage.get("promptTokenCount", 0)
    output_tokens = usage.get("candidatesTokenCount", 0)

    return {
        "content": content,
        "tool_calls": None,  # TODO: Add tool support for Gemini
        "finish_reason": finish_reason,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
    }
