"""Type definitions for local router functionality.

These types define the data shapes flowing through the local development router,
providing static type checking without runtime overhead via TypedDicts.
"""

from typing import TypedDict

from dispatch_agents import LLMToolCall


class LLMProviderResult(TypedDict, total=False):
    """Result returned from local LLM provider calls.

    This is the standardized shape returned by call_openai(), call_anthropic(),
    and call_google(). Each provider's raw response is converted to this format
    for consistent handling by the router.

    Fields:
        content: The text response content (may be None if tool_calls present)
        tool_calls: Function/tool calls requested by the model (OpenAI format)
        finish_reason: Why generation stopped (stop, length, tool_calls, etc.)
        input_tokens: Number of input/prompt tokens used
        output_tokens: Number of output/completion tokens generated
    """

    content: str | None
    tool_calls: list[LLMToolCall] | None
    finish_reason: str
    input_tokens: int
    output_tokens: int
