"""Agent MCP tools for agent-specific functions."""

import asyncio
import json
import re
import sys
from typing import Any

from dispatch_agents.invocation import InvocationStatus

from mcp.server.lowlevel import Server
from mcp.types import TASK_REQUIRED, CallToolResult, TextContent, Tool

from ..client import AgentBackendClient
from ..config import MCPConfig

# Default polling configuration for function invocation
DEFAULT_POLL_INTERVAL = 1.0  # seconds
DEFAULT_TIMEOUT = 300  # seconds (5 minutes)


def sanitize_tool_name(name: str) -> str:
    """Sanitize name for MCP tool compatibility."""
    sanitized = re.sub(r"[^a-z0-9_]", "_", name.lower())
    sanitized = re.sub(r"_+", "_", sanitized)
    return sanitized.strip("_")


def register_agent_tools(
    server: Server,
    client: AgentBackendClient,
    config: MCPConfig,
):
    """Register agent-specific MCP tools based on agent functions."""

    if not config.agent_name:
        raise RuntimeError("Agent name is required for agent MCP server")

    # Enable experimental task support for async agent function execution
    if config.use_tasks:
        server.experimental.enable_tasks()

    # Fetch agent info to get function schemas
    try:
        agent_info = client.get_agent_info(
            config.agent_name, namespace=config.namespace
        )
    except Exception as e:
        raise RuntimeError(
            f"Failed to connect to agent '{config.agent_name}' in namespace '{config.namespace}': {e}\n"
            f"Deploy the agent first, then restart the MCP server."
        ) from e

    # Extract functions from agent info
    functions = agent_info.get("functions", [])
    if not functions:
        print(
            f"[yellow]![/yellow] Warning: Agent '{config.agent_name}' has no functions",
            file=sys.stderr,
        )
        print("The agent may not have any handlers defined yet.", file=sys.stderr)

    # Build dynamic tools from agent functions
    dynamic_tools: list[Tool] = []
    dynamic_tool_handlers: dict[str, dict[str, Any]] = {}

    for function in functions:
        func_name = function.get("name")
        if not func_name:
            continue

        # Create tool name from function name
        tool_name = sanitize_tool_name(f"invoke_function_{func_name}")

        base_description = function.get("description") or f"Invoke {func_name} function"
        full_description = f"{base_description}\n\nHandler: {func_name}"

        # Create tool definition with output schema
        tool = Tool(
            name=tool_name,
            description=full_description,
            inputSchema=function.get("input_schema", {}),
            outputSchema=function.get("output_schema"),
        )
        dynamic_tools.append(tool)

        # Store handler metadata for direct invocation
        dynamic_tool_handlers[tool_name] = {
            "function_name": func_name,
            "agent_name": config.agent_name,
            "namespace": config.namespace,
        }

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List agent function tools."""
        return dynamic_tools

    async def invoke_and_wait(
        handler_info: dict[str, Any],
        arguments: dict[str, Any],
        timeout: float = DEFAULT_TIMEOUT,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
    ) -> dict[str, Any]:
        """Invoke a function and wait for the result.

        Uses async client methods to avoid blocking the event loop.
        """
        # Start the invocation
        invoke_result = await client.invoke_function_async(
            agent_name=handler_info["agent_name"],
            function_name=handler_info["function_name"],
            payload=arguments,
            namespace=handler_info.get("namespace"),
            timeout_seconds=int(timeout),
        )

        invocation_id = invoke_result.get("invocation_id", "")
        trace_id = invoke_result.get("trace_id", "")
        if not invocation_id:
            return {
                "status": "error",
                "error": "No invocation_id returned from invoke",
            }

        # Poll for result
        max_polls = int(timeout / poll_interval)
        for _ in range(max_polls):
            await asyncio.sleep(poll_interval)

            status_result = await client.get_invocation_status_async(
                invocation_id, namespace=handler_info.get("namespace")
            )
            status = status_result.get("status", "unknown").lower()

            if status == InvocationStatus.COMPLETED.value:
                return {
                    "status": "completed",
                    "result": status_result.get("result"),
                    "invocation_id": invocation_id,
                    "trace_id": trace_id,
                }
            elif status == InvocationStatus.ERROR.value:
                return {
                    "status": "error",
                    "error": status_result.get("error", "Unknown error"),
                    "invocation_id": invocation_id,
                    "trace_id": trace_id,
                }

        return {
            "status": "timeout",
            "error": f"Timed out after {timeout} seconds",
            "invocation_id": invocation_id,
            "trace_id": trace_id,
        }

    async def handle_dynamic_agent_function(
        arguments: dict[str, Any], handler_info: dict[str, Any]
    ):
        """Handle dynamic agent function tool call using direct invocation."""
        func_name = handler_info["function_name"]

        if config.use_tasks:
            ctx = server.request_context
            ctx.experimental.validate_task_mode(TASK_REQUIRED)

            async def execute_agent_function(task):
                try:
                    await task.update_status(f"Invoking {func_name}...")

                    result = await invoke_and_wait(handler_info, arguments)

                    if result["status"] == "completed":
                        result_data = result.get("result")
                        # Return both structured content (for schema validation)
                        # and text content (for display)
                        if isinstance(result_data, dict):
                            result_text = json.dumps(result_data, indent=2)
                            return CallToolResult(
                                content=[TextContent(type="text", text=result_text)],
                                structuredContent=result_data,
                            )
                        else:
                            return CallToolResult(
                                content=[
                                    TextContent(type="text", text=str(result_data))
                                ]
                            )
                    else:
                        error_msg = result.get("error", "Unknown error")
                        return CallToolResult(
                            content=[
                                TextContent(
                                    type="text",
                                    text=f"Function {func_name} failed: {error_msg}",
                                )
                            ],
                            isError=True,
                        )
                except Exception as e:
                    return CallToolResult(
                        content=[TextContent(type="text", text=f"Error: {str(e)}")],
                        isError=True,
                    )

            return await ctx.experimental.run_task(execute_agent_function)
        else:
            # Direct invocation without MCP tasks
            # Return CallToolResult to support structured output
            try:
                result = await invoke_and_wait(handler_info, arguments)

                if result["status"] == "completed":
                    result_data = result.get("result")
                    if isinstance(result_data, dict):
                        result_text = json.dumps(result_data, indent=2)
                        return CallToolResult(
                            content=[TextContent(type="text", text=result_text)],
                            structuredContent=result_data,
                        )
                    else:
                        return CallToolResult(
                            content=[TextContent(type="text", text=str(result_data))]
                        )
                else:
                    error_msg = result.get("error", "Unknown error")
                    return CallToolResult(
                        content=[
                            TextContent(
                                type="text",
                                text=f"Function {func_name} failed: {error_msg}",
                            )
                        ],
                        isError=True,
                    )
            except Exception as e:
                return CallToolResult(
                    content=[TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True,
                )

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> CallToolResult:
        """Handle tool calls."""
        if name in dynamic_tool_handlers:
            return await handle_dynamic_agent_function(
                arguments, dynamic_tool_handlers[name]
            )
        else:
            raise ValueError(f"Unknown tool: {name}")
