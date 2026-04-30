"""Operator MCP tools for platform management."""

import asyncio
import os
import signal
import subprocess
from pathlib import Path
from typing import Any

import aiohttp
import httpx
from dispatch_agents import FeedbackSentiment, FeedbackType
from pydantic import BaseModel, Field

from dispatch_cli.utils import (
    DISPATCH_YAML,
    LOCAL_ROUTER_PORT,
    LOCAL_ROUTER_URL,
)
# PORT: original imports kept for reference; replaced by SecureMCP/Context.
# from mcp.server.fastmcp import Context, FastMCP
# from mcp.server.session import ServerSession
from macaw_adapters.mcp import SecureMCP, Context

from ..client import OperatorBackendClient
from ..config import MCPConfig
from ..models import (
    CreateScheduleRequest,
    CreateScheduleResponse,
    DeleteScheduleRequest,
    DeleteScheduleResponse,
    EventRecord,
    EventTraceResponse,
    GetScheduleRequest,
    GetScheduleResponse,
    ListLongTermMemoriesResponse,
    ListSchedulesRequest,
    ListSchedulesResponse,
    RebootAgentResponse,
    RecentTracesResponse,
    StopAgentResponse,
    TopicListItem,
    UpdateScheduleRequest,
    UpdateScheduleResponse,
)


# Request models
class ListNamespacesRequest(BaseModel):
    """Request payload for listing namespaces."""

    pass  # No parameters needed


class ListAgentsRequest(BaseModel):
    """Request payload for listing agents."""

    namespace: str = Field(
        description="Namespace (required). Use the namespace from the agent's dispatch.yaml, or call list_namespaces to discover valid namespaces."
    )
    limit: int = Field(default=50, description="Maximum number of agents to return")


class CreateAgentRequest(BaseModel):
    """Request payload for creating an agent."""

    parent_directory: str = Field(
        description="Parent directory where the agent directory will be created"
    )
    agent_name: str = Field(description="Name for the agent")
    description: str = Field(description="Description of what the agent does")
    namespace: str | None = Field(
        default=None,
        description="Namespace (optional, auto-discovered from dispatch.yaml if present)",
    )


class DeployAgentRequest(BaseModel):
    """Request payload for deploying an agent."""

    agent_directory: str = Field(description="Path to the agent directory")


class GetDeployStatusRequest(BaseModel):
    """Request payload for getting deployment status."""

    job_id: str = Field(description="Deployment job ID returned by deploy_agent")
    namespace: str = Field(
        description="Namespace (required). Use the namespace from the agent's dispatch.yaml, or call list_namespaces to discover valid namespaces."
    )


class UninstallAgentRequest(BaseModel):
    """Request payload for uninstalling an agent."""

    agent_name: str = Field(description="Agent name")
    namespace: str = Field(
        description="Namespace (required). Use the namespace from the agent's dispatch.yaml, or call list_namespaces to discover valid namespaces."
    )


class StopAgentRequest(BaseModel):
    """Request payload for stopping an agent."""

    agent_name: str = Field(description="Agent name")
    namespace: str = Field(
        description="Namespace (required). Use the namespace from the agent's dispatch.yaml, or call list_namespaces to discover valid namespaces."
    )


class RebootAgentRequest(BaseModel):
    """Request payload for rebooting an agent."""

    agent_name: str = Field(description="Agent name")
    namespace: str = Field(
        description="Namespace (required). Use the namespace from the agent's dispatch.yaml, or call list_namespaces to discover valid namespaces."
    )


class GetAgentLogsRequest(BaseModel):
    """Request payload for getting agent logs."""

    agent_name: str = Field(description="Agent name")
    namespace: str = Field(
        description="Namespace (required). Use the namespace from the agent's dispatch.yaml, or call list_namespaces to discover valid namespaces."
    )
    version: str = Field(default="latest", description="Agent version")
    limit: int = Field(default=100, description="Maximum number of log lines")


class GetTopicSchemaRequest(BaseModel):
    """Request payload for getting topic schema."""

    topic: str = Field(description="Topic name")
    namespace: str = Field(
        description="Namespace (required). Use the namespace from the agent's dispatch.yaml, or call list_namespaces to discover valid namespaces."
    )


class PublishEventRequest(BaseModel):
    """Request payload for publishing an event."""

    topic: str = Field(description="Topic name")
    payload: dict[str, Any] = Field(description="Event payload (JSON object)")
    namespace: str = Field(
        description="Namespace (required). Use the namespace from the agent's dispatch.yaml, or call list_namespaces to discover valid namespaces."
    )


class ListTopicsRequest(BaseModel):
    """Request payload for listing topics."""

    namespace: str = Field(
        description="Namespace (required). Use the namespace from the agent's dispatch.yaml, or call list_namespaces to discover valid namespaces."
    )


class GetRecentEventsRequest(BaseModel):
    """Request payload for getting recent events."""

    namespace: str = Field(
        description="Namespace (required). Use the namespace from the agent's dispatch.yaml, or call list_namespaces to discover valid namespaces."
    )
    topic: str | None = Field(default=None, description="Optional topic filter")
    limit: int = Field(
        default=20, description="Max events to return (1-100)", ge=1, le=100
    )


class GetEventTraceRequest(BaseModel):
    """Request payload for getting an event trace."""

    trace_id: str = Field(description="Trace ID to look up")
    namespace: str = Field(
        description="Namespace (required). Use the namespace from the agent's dispatch.yaml, or call list_namespaces to discover valid namespaces."
    )


class GetRecentTracesRequest(BaseModel):
    """Request payload for getting recent traces."""

    namespace: str = Field(
        description="Namespace (required). Use the namespace from the agent's dispatch.yaml, or call list_namespaces to discover valid namespaces."
    )
    topic: str | None = Field(default=None, description="Optional topic filter")
    limit: int = Field(
        default=50, description="Max traces to return (1-100)", ge=1, le=100
    )


class GetAgentFunctionsRequest(BaseModel):
    """Request payload for getting agent functions."""

    agent_name: str = Field(description="Agent name")
    namespace: str = Field(
        description="Namespace (required). Use the namespace from the agent's dispatch.yaml, or call list_namespaces to discover valid namespaces."
    )


class InvokeFunctionRequest(BaseModel):
    """Request payload for invoking a function."""

    agent_name: str = Field(description="Target agent name")
    function_name: str = Field(description="Function name to invoke")
    payload: dict[str, Any] = Field(
        default_factory=dict, description="Input payload for the function"
    )
    namespace: str = Field(
        description="Namespace (required). Use the namespace from the agent's dispatch.yaml, or call list_namespaces to discover valid namespaces."
    )
    timeout_seconds: int | None = Field(
        default=300, description="Timeout in seconds (default 5 minutes, max 24 hours)"
    )
    wait_for_result: bool = Field(
        default=True,
        description="If true, wait for result (blocking). If false, return invocation_id for polling.",
    )
    poll_interval_seconds: float = Field(
        default=1.0,
        description="How often to poll for result (when wait_for_result=True)",
    )


class GetInvocationStatusRequest(BaseModel):
    """Request payload for getting invocation status."""

    invocation_id: str = Field(description="Invocation ID to check")
    namespace: str = Field(
        description="Namespace (required). Use the namespace from the agent's dispatch.yaml, or call list_namespaces to discover valid namespaces."
    )


class StartLocalAgentDevRequest(BaseModel):
    """Request payload for starting agent in dev mode."""

    agent_directory: str = Field(description="Path to the agent directory")
    router_port: int = Field(
        default=LOCAL_ROUTER_PORT, description="Port to expose the router on"
    )
    enable_reload: bool = Field(
        default=False,
        description="Enable hot-reload: automatically restart agent when Python files change",
    )


class InvokeLocalFunctionRequest(BaseModel):
    """Request payload for invoking a function on a local agent."""

    agent_directory: str = Field(description="Path to the agent directory")
    function_name: str = Field(description="Name of the function to invoke")
    payload: dict[str, Any] = Field(
        default_factory=dict, description="Input payload for the function"
    )
    router_port: int = Field(default=LOCAL_ROUTER_PORT, description="Local router port")
    timeout_seconds: int = Field(default=60, description="Request timeout in seconds")


class InvokeLocalFunctionResponse(BaseModel):
    """Response from local function invocation."""

    status: str = Field(description="Invocation status (success, error)")
    result: dict[str, Any] | None = Field(
        default=None, description="Function return value (if successful)"
    )
    error: str | None = Field(default=None, description="Error message (if failed)")
    agent_name: str = Field(description="Name of the agent that handled the request")


class StopRouterRequest(BaseModel):
    """Request payload for stopping the local router."""

    pass  # No parameters needed — stops the running router


class ListRoutersRequest(BaseModel):
    """Request payload for listing tracked routers."""

    pass  # No parameters needed


class RouterInfo(BaseModel):
    """Information about a tracked router."""

    port: int = Field(description="Port the router is running on")
    pid: int = Field(description="Process ID of the router")
    started_at: str = Field(description="When the router was started")
    running: bool = Field(description="Whether the router process is currently running")


class ListRoutersResponse(BaseModel):
    """Response from listing tracked routers."""

    routers: list[RouterInfo] = Field(description="List of tracked routers")
    total: int = Field(description="Total number of tracked routers")


class SendTestEventRequest(BaseModel):
    """Request payload for sending a test event through local router."""

    topic: str = Field(description="Topic name")
    payload: dict[str, Any] = Field(description="Event payload (JSON object)")
    agent_directory: str | None = Field(
        default=None,
        description="Optional agent directory for context (auto-discovers namespace)",
    )
    router_port: int = Field(
        default=LOCAL_ROUTER_PORT, description="Port to send the test event to"
    )


class ReadLocalAgentLogsRequest(BaseModel):
    """Request payload for reading local agent logs."""

    agent_directory: str = Field(description="Path to the agent directory")
    lines: int = Field(
        default=50, description="Number of most recent log lines to retrieve"
    )


# Response models
class ListNamespacesResponse(BaseModel):
    """Response from listing namespaces."""

    namespaces: list[str] = Field(description="List of accessible namespaces")


class ListAgentsResponse(BaseModel):
    """Response from listing agents."""

    agents: list[dict[str, Any]] = Field(description="List of agents in namespace")


class CreateAgentResponse(BaseModel):
    """Response from creating an agent."""

    success: bool = Field(description="Whether the agent was created successfully")
    agent_directory: str = Field(description="Path to the created agent directory")
    message: str = Field(description="Success or error message")


class DeployAgentResponse(BaseModel):
    """Response from deploying an agent."""

    agent_name: str = Field(description="Name of the deployed agent")
    status: str = Field(description="Deployment status")
    message: str = Field(description="Deployment output message")
    job_id: str | None = Field(
        default=None,
        description="Deployment job ID for polling status with get_deploy_status",
    )
    namespace: str | None = Field(
        default=None,
        description="Namespace the agent is being deployed to",
    )


class DeployStageInfo(BaseModel):
    """Information about a deployment stage."""

    name: str = Field(description="Stage name")
    status: str = Field(
        description="Stage status (e.g. pending, in_progress, completed, failed)"
    )
    started_at: str | None = Field(default=None, description="Stage start time")
    completed_at: str | None = Field(default=None, description="Stage completion time")


class GetDeployStatusResponse(BaseModel):
    """Response from getting deployment status."""

    job_id: str = Field(description="Deployment job ID")
    status: str = Field(
        description="Overall deployment status (e.g. in_progress, completed, failed)"
    )
    version: str | None = Field(default=None, description="Deployed agent version")
    stages: list[DeployStageInfo] = Field(
        default_factory=list, description="Deployment stage details"
    )
    logs: list[str] = Field(default_factory=list, description="Deployment log lines")
    error: str | None = Field(
        default=None, description="Error message if deployment failed"
    )


class UninstallAgentResponse(BaseModel):
    """Response from uninstalling an agent."""

    status: str = Field(description="Deletion status")
    agent_id: str = Field(description="ID of the deleted agent")


class GetAgentLogsResponse(BaseModel):
    """Response from getting agent logs."""

    events: list[dict[str, Any]] = Field(description="Array of log entries")
    next_token: str | None = Field(default=None, description="Token for pagination")


class GetTopicSchemaResponse(BaseModel):
    """Response from getting topic schema."""

    topic: str = Field(description="Topic name")
    canonical_schema: dict[str, Any] = Field(description="Topic schema definition")
    handlers: list[dict[str, Any]] = Field(
        description="List of agents subscribed to this topic"
    )
    org_id: str = Field(description="Organization ID")
    namespace: str = Field(description="Namespace")
    last_updated: str = Field(description="Last update timestamp")


class PublishEventResponse(BaseModel):
    """Response from publishing an event."""

    message: str = Field(description="Status message")
    event_uid: str = Field(description="Unique identifier for the published event")


class FunctionSchema(BaseModel):
    """Schema for an agent function."""

    name: str = Field(description="Function name")
    description: str | None = Field(default=None, description="Function description")
    input_schema: dict[str, Any] | None = Field(
        default=None, description="JSON Schema for function input"
    )
    output_schema: dict[str, Any] | None = Field(
        default=None, description="JSON Schema for function output"
    )


class GetAgentFunctionsResponse(BaseModel):
    """Response from getting agent functions."""

    agent_name: str = Field(description="Agent name")
    functions: list[FunctionSchema] = Field(description="List of available functions")
    total: int = Field(description="Total number of functions")


class InvokeFunctionResponse(BaseModel):
    """Response from invoking a function."""

    invocation_id: str = Field(description="Unique invocation identifier")
    trace_id: str = Field(
        description="Trace ID for viewing the invocation trace in the UI"
    )
    status: str = Field(
        description="Invocation status: PENDING, RUNNING, COMPLETED, or ERROR"
    )
    result: dict[str, Any] | None = Field(
        default=None, description="Function result (when status=COMPLETED)"
    )
    error: str | None = Field(
        default=None, description="Error message (when status=ERROR)"
    )
    waited: bool = Field(default=False, description="Whether we waited for the result")


class GetInvocationStatusResponse(BaseModel):
    """Response from getting invocation status."""

    invocation_id: str = Field(description="Invocation identifier")
    status: str = Field(
        description="Invocation status: PENDING, RUNNING, COMPLETED, or ERROR"
    )
    result: dict[str, Any] | None = Field(
        default=None, description="Function result (when status=COMPLETED)"
    )
    error: str | None = Field(
        default=None, description="Error message (when status=ERROR)"
    )
    created_at: str | None = Field(default=None, description="When invocation started")
    completed_at: str | None = Field(
        default=None, description="When invocation completed"
    )


class StartLocalAgentDevResponse(BaseModel):
    """Response from starting dev mode."""

    agent_name: str = Field(description="Name of the agent")
    status: str = Field(description="Dev mode status")
    message: str = Field(description="Status message with instructions")
    router_ui_url: str = Field(
        default="http://localhost:8080", description="Router UI URL"
    )
    startup_logs: list[str] = Field(
        default_factory=list,
        description="Startup warnings (e.g., unconfigured secrets)",
    )


class StopRouterResponse(BaseModel):
    """Response from stopping router."""

    status: str = Field(description="Router status")
    message: str = Field(description="Status message")


class AgentRouteInfo(BaseModel):
    """Information about an agent that received an event."""

    name: str = Field(description="Agent name")
    topics: list[str] = Field(description="Topics the agent handles")


class AgentResponse(BaseModel):
    """Response from an agent."""

    result: dict | None = Field(default=None, description="Result payload from agent")
    error: str | None = Field(default=None, description="Error message if failed")
    status: str | None = Field(default=None, description="Response status")


class SendTestEventResponse(BaseModel):
    """Response from sending test event."""

    status: str = Field(description="Event send status")
    message: str = Field(description="Status message")
    event_uid: str | None = Field(default=None, description="Event UID if successful")
    routed_to: list[AgentRouteInfo] = Field(
        default_factory=list, description="List of agents the event was routed to"
    )
    responses: dict[str, AgentResponse] = Field(
        default_factory=dict, description="Responses from each agent"
    )


class ReadLocalAgentLogsResponse(BaseModel):
    """Response from reading local agent logs."""

    agent_name: str = Field(description="Name of the agent")
    logs: list[str] = Field(description="List of log lines")
    total_lines: int = Field(description="Total number of lines retrieved")


class ListLongTermMemoriesRequest(BaseModel):
    """Request payload for listing long-term memories."""

    agent_name: str = Field(description="Agent name")
    namespace: str = Field(
        description="Namespace the agent belongs to. Use list_namespaces to discover valid namespaces."
    )


def write_pid_file(agent_directory: str, pid: int) -> str:
    """Write a PID file for an agent process.

    Args:
        agent_directory: Agent directory (can be relative or absolute)
        pid: Process ID to write

    Returns:
        Absolute path to the PID file that was created
    """
    abs_agent_dir = os.path.abspath(agent_directory)
    pid_file = os.path.join(abs_agent_dir, ".dispatch", "agent.pid")
    os.makedirs(os.path.dirname(pid_file), exist_ok=True)
    with open(pid_file, "w") as f:
        f.write(str(pid))
    return pid_file


def read_agent_log_file(
    agent_directory: str, lines: int = 50, max_line_length: int = 500
) -> list[str]:
    """Read recent log lines from an agent's log file.

    Args:
        agent_directory: Agent directory (can be relative or absolute)
        lines: Number of lines to read from end of file
        max_line_length: Maximum length of each line before truncation

    Returns:
        List of log lines (newest lines last)

    Raises:
        FileNotFoundError: If log file doesn't exist
    """
    abs_agent_dir = os.path.abspath(agent_directory)
    log_file = os.path.join(abs_agent_dir, ".dispatch", "logs", "agent.log")

    if not os.path.exists(log_file):
        raise FileNotFoundError(f"No log file found at {log_file}")

    logs = []
    with open(log_file) as f:
        all_lines = f.readlines()
        for line in all_lines[-lines:]:
            line = line.rstrip()

            # Skip empty lines and lines containing only null bytes/whitespace
            cleaned = line.replace("\x00", "").strip()
            if not cleaned:
                continue

            if len(line) > max_line_length:
                line = line[:max_line_length] + "... (truncated)"
            logs.append(line)

    return logs


async def cleanup_all_agent_processes(base_dir: str | None = None) -> int:
    """Clean up all agent dev processes by finding and removing PID files.

    Args:
        base_dir: Base directory to search for PID files (defaults to current working directory)

    Returns:
        Number of processes cleaned up
    """
    search_dir = Path(base_dir) if base_dir else Path.cwd()
    cleaned_count = 0

    # Find all .dispatch/agent.pid files recursively
    for pid_file in search_dir.rglob(".dispatch/agent.pid"):
        try:
            with open(pid_file) as f:
                pid = int(f.read().strip())

            # Try to kill the process group (kills parent + all children)
            try:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
                cleaned_count += 1
            except ProcessLookupError:
                # Process already stopped
                pass

            # Clean up PID file
            os.remove(pid_file)
        except (OSError, ValueError):
            # Invalid PID file or IO error - skip it
            pass

    return cleaned_count


OPERATOR_INSTRUCTIONS = """
Dispatch Agents Operator - MCP Server for managing AI agents on the Dispatch platform.

## Agent Configuration (dispatch.yaml)

When creating or modifying agents, the `dispatch.yaml` file in the agent directory controls
deployment settings. Key configuration options:

### Required Fields
- `agent_name`: Unique identifier for the agent
- `namespace`: Organization namespace (e.g., "skunkworks")
- `entrypoint`: Python file with @fn() decorated functions (default: "agent.py")
- `base_image`: Docker base image (default: "python:3.13-slim")

### Optional Features

**Persistent Storage (Volumes)** - Mount persistent directories:
```yaml
volumes:
  - name: data
    mountPath: /data
    mode: read_write_many
```
- `name`: Unique identifier for the volume (lowercase, alphanumeric with hyphens)
- `mountPath`: Path inside container (must be within /data)
- `mode`: Access mode (currently only `read_write_many` supported)
- Data persists across container restarts and redeployments
- Each agent gets isolated storage

**Secrets** - Inject non-LLM secrets as environment variables:
```yaml
secrets:
  - name: DD_API_KEY
    secret_id: /datadog/api-key
  - name: MY_SERVICE_TOKEN
    secret_id: /shared/my-service-token
```
**Important:** Do NOT add LLM provider API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY) here.
Use the LLM Gateway instead (see below).

**System Packages** - Install additional apt packages:
```yaml
system_packages:
  - ffmpeg
  - git
```

**Local Dependencies** - For monorepo development:
```yaml
local_dependencies:
  my_package: ../path/to/package
```

## Agent Functions

Agents expose functions using the @fn() decorator from dispatch_agents SDK:

```python
from dispatch_agents import fn, BasePayload

class MyInput(BasePayload):
    query: str

class MyOutput(BasePayload):
    result: str

@fn()
async def my_function(payload: MyInput) -> MyOutput:
    return MyOutput(result=f"Processed: {payload.query}")
```

## Environment Variables

Available environment variables in your agent code:
- `DISPATCH_AGENT_NAME`: The agent's name (from dispatch.yaml or pyproject.toml)
- `DISPATCH_NAMESPACE`: Namespace for API calls
- `BACKEND_URL`: URL of the backend API (auto-configured)
- `DISPATCH_API_KEY`: API key for authentication (auto-configured)

Example usage:
```python
import os
agent_name = os.environ.get("DISPATCH_AGENT_NAME", "unknown-agent")
```

## LLM Gateway

Dispatch provides a built-in LLM gateway with observability, cost tracking, and centralized
credential management. Agents can call LLM providers (OpenAI, Anthropic, etc.) without
managing API keys directly.

### Setup (CLI)
```bash
# Interactive setup wizard (recommended)
dispatch llm setup

# Or configure directly (org-wide by default)
dispatch llm configure openai --api-key sk-proj-... --default

# For local development only
dispatch llm local openai
```

### Usage in Agent Code
```python
from dispatch_agents import llm

# Uses the default configured provider
response = await llm.inference([
    {"role": "user", "content": "Hello!"}
])
print(response.content)

# Or specify provider/model explicitly
response = await llm.inference(
    messages=[{"role": "user", "content": "Hello!"}],
    provider="anthropic",
    model="claude-sonnet-4-5-20250929",
)
```

### Key Points
- Do NOT add LLM provider API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY) to
  `dispatch.yaml` secrets. The LLM gateway manages credentials automatically.
- Provider keys are configured at **org level** (shared across namespaces) by default.
  Namespaces can override with their own keys if needed.
- Use `dispatch llm setup` to configure providers, or the web UI at /manage/llm-providers.
- Each agent can have a **monthly budget** to cap LLM spend.
- Set `DISPATCH_LLM_INSTRUMENT=false` to bypass the gateway and use provider SDKs directly.

## Memory API

The SDK provides three memory clients for persistent state. Agent name is auto-detected
from the `DISPATCH_AGENT_NAME` environment variable.

### Long-term Memory (Key-Value Store)
```python
from dispatch_agents import memory

# Store data (agent_name auto-detected from DISPATCH_AGENT_NAME env var)
await memory.long_term.add(mem_key="user_prefs", mem_val='{"theme": "dark"}')

# Retrieve data
value = await memory.long_term.get(mem_key="user_prefs")

# List all memories for the agent
all_memories = await memory.long_term.list()

# Delete data
await memory.long_term.delete(mem_key="user_prefs")

# Override agent_name if needed (e.g., reading another agent's data)
value = await memory.long_term.get(mem_key="user_prefs", agent_name="other-agent")
all_memories = await memory.long_term.list(agent_name="other-agent")
```

You can also use the `list_long_term_memories` MCP tool to inspect an agent's memories.

### Short-term Memory (Session Store)
```python
# Store session data
await memory.short_term.add(session_id="sess123", session_data={"step": 1})

# Retrieve session
data = await memory.short_term.get(session_id="sess123")
```

**Note:** Memory API requires the backend to be running. In local dev mode, use `volumes`
for file-based persistence instead.

## Schedules

Schedules allow you to trigger agent functions automatically at specified times using cron expressions.
Use schedules for recurring tasks like daily reports, periodic data syncs, or scheduled maintenance.

### Creating a Schedule
```python
# Create a schedule that runs every weekday at 9am EST
create_schedule(
    agent_name="my-agent",
    function_name="generate_report",
    cron_expression="0 9 * * MON-FRI",
    timezone="America/New_York",
    payload={"report_type": "daily"},
    description="Daily report generation"
)
```

### Cron Expression Format
Standard 5-field cron format: `minute hour day-of-month month day-of-week`

Common patterns:
- `* * * * *` - Every minute
- `*/5 * * * *` - Every 5 minutes
- `0 * * * *` - Every hour (at minute 0)
- `0 9 * * *` - Daily at 9:00 AM
- `0 9 * * MON-FRI` - Weekdays at 9:00 AM
- `0 0 1 * *` - First day of each month at midnight
- `0 */2 * * *` - Every 2 hours

### Managing Schedules
- **List schedules**: Use `list_schedules` to see all schedules or filter by agent
- **Get details**: Use `get_schedule` with a schedule_id
- **Pause/Resume**: Use `update_schedule` with `is_paused=true/false`
- **Update timing**: Use `update_schedule` to change cron_expression or timezone
- **Delete**: Use `delete_schedule` to permanently remove a schedule

### Timezones
Always specify a timezone for schedules. Common timezones:
- `UTC` (default)
- `America/New_York`, `America/Los_Angeles`, `America/Chicago`
- `Europe/London`, `Europe/Paris`, `Europe/Berlin`
- `Asia/Tokyo`, `Asia/Shanghai`, `Asia/Singapore`

## Workflow

1. **Create agent**: Use create_agent tool with parent_directory, agent_name, description
2. **Configure**: Edit dispatch.yaml to add volumes, secrets, etc.
3. **Implement**: Write agent.py with @fn() decorated functions
4. **Test locally**: Use start_local_agent_dev tool
5. **Deploy**: Use deploy_agent tool to deploy to cloud
6. **Invoke**: Use invoke_function or get_agent_functions tools
7. **Schedule** (optional): Use create_schedule to run functions on a cron schedule
"""


def create_operator_mcp(client: OperatorBackendClient, config: MCPConfig) -> SecureMCP:
    """Create operator MCP server with tools."""
    # PORT: SecureMCP.__init__ does not accept `instructions=`; OPERATOR_INSTRUCTIONS
    # is preserved as a module constant for reference only. Original was:
    #   mcp = FastMCP("dispatch-operator", instructions=OPERATOR_INSTRUCTIONS)
    mcp = SecureMCP("dispatch-operator")

    def _get_namespace(namespace: str | None = None) -> str:
        """Get namespace from argument or config."""
        ns = namespace or config.namespace
        if not ns:
            raise ValueError("Namespace is required")
        return str(ns)

    def _read_agent_config(agent_directory: str) -> dict[str, Any]:
        """Read dispatch.yaml from an agent directory.

        Returns the parsed YAML as a dict, or {} if no config file found.
        """
        import yaml

        hidden = os.path.join(agent_directory, ".dispatch.yaml")
        if os.path.exists(hidden):
            raise RuntimeError(
                ".dispatch.yaml is no longer supported; rename it to dispatch.yaml"
            )
        candidate = os.path.join(agent_directory, DISPATCH_YAML)
        if os.path.exists(candidate):
            with open(candidate, encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            return data if isinstance(data, dict) else {}
        return {}

    # PORT (original):
    # @mcp.tool()
    # async def list_namespaces(request: ListNamespacesRequest) -> ListNamespacesResponse:
    #     """List all accessible namespaces."""
    #     result = client.list_namespaces()
    #     return ListNamespacesResponse(namespaces=result.get("namespaces", []))
    @mcp.tool()
    async def list_namespaces() -> dict:
        """List all accessible namespaces.

        Returns:
            Dict with list of namespaces.
        """
        result = client.list_namespaces()
        return ListNamespacesResponse(namespaces=result.get("namespaces", [])).model_dump()

    # PORT (original):
    # @mcp.tool()
    # async def list_agents(request: ListAgentsRequest) -> ListAgentsResponse:
    #     """List agents in namespace.
    #
    #     Args:
    #         request: ListAgentsRequest with optional namespace and limit
    #
    #     Returns:
    #         ListAgentsResponse with list of agents
    #     """
    #     ns = _get_namespace(request.namespace)
    #     agents = client.list_agents(namespace=ns, limit=request.limit)
    #     # Backend returns list directly
    #     return ListAgentsResponse(agents=agents)
    @mcp.tool()
    async def list_agents(namespace: str, limit: int = 50) -> dict:
        """List agents in namespace.

        Args:
            namespace: Namespace (required). Use the namespace from the agent's
                dispatch.yaml, or call list_namespaces to discover valid namespaces.
            limit: Maximum number of agents to return (default 50).

        Returns:
            Dict with list of agents.
        """
        ns = _get_namespace(namespace)
        agents = client.list_agents(namespace=ns, limit=limit)
        # Backend returns list directly
        return ListAgentsResponse(agents=agents).model_dump()

    # PORT (original):
    # @mcp.tool()
    # async def create_agent(request: CreateAgentRequest) -> CreateAgentResponse:
    #     """Initialize a new agent directory with scaffold code."""
    #     ns = _get_namespace(request.namespace)
    #     agent_dir = os.path.join(request.parent_directory, request.agent_name)
    #     ...
    #     return CreateAgentResponse(success=True, agent_directory=agent_dir,
    #         message=f"Successfully created agent '{request.agent_name}'")
    @mcp.tool()
    async def create_agent(
        parent_directory: str,
        agent_name: str,
        description: str,
        namespace: str | None = None,
    ) -> dict:
        """Initialize a new agent directory with scaffold code.

        Args:
            parent_directory: Parent directory where the agent directory will be created.
            agent_name: Name for the agent.
            description: Description of what the agent does.
            namespace: Namespace (optional, auto-discovered from dispatch.yaml if present).

        Returns:
            Dict with success status, agent_directory path, and message.
        """
        ns = _get_namespace(namespace)
        agent_dir = os.path.join(parent_directory, agent_name)

        # Create agent directory
        os.makedirs(agent_dir, exist_ok=True)
        # Create/update dispatch.yaml with agent name, namespace, and description
        dispatch_yaml_path = os.path.join(agent_dir, "dispatch.yaml")
        dispatch_yaml_content = f"""agent_name: {agent_name}
namespace: {ns}
"""
        with open(dispatch_yaml_path, "w") as f:
            f.write(dispatch_yaml_content)

        # Run dispatch agent init command
        result = subprocess.run(
            ["dispatch", "agent", "init", "--path", ".", "--assume-yes"],
            cwd=agent_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            return CreateAgentResponse(
                success=False,
                agent_directory=agent_dir,
                message=f"Failed to create agent: {result.stderr}",
            ).model_dump()

        return CreateAgentResponse(
            success=True,
            agent_directory=agent_dir,
            message=f"Successfully created agent '{agent_name}'",
        ).model_dump()

    # PORT (original — kept commented for review):
    # @mcp.tool()
    # async def deploy_agent(
    #     request: DeployAgentRequest,
    #     ctx: Context[ServerSession, None],
    # ) -> DeployAgentResponse:
    #     """Deploy an agent from directory (auto-discovers namespace from dispatch.yaml)."""
    #     abs_agent_dir = os.path.abspath(request.agent_directory)
    #     agent_config = _read_agent_config(abs_agent_dir)
    #     agent_name = agent_config.get("agent_name") or os.path.basename(abs_agent_dir)
    #     await ctx.info(f"Starting deployment of agent '{agent_name}'")
    #     process = await asyncio.create_subprocess_exec(
    #         "dispatch", "agent", "deploy", "--force", "--no-wait",
    #         cwd=abs_agent_dir,
    #         stdin=asyncio.subprocess.DEVNULL,
    #         stdout=asyncio.subprocess.PIPE,
    #         stderr=asyncio.subprocess.PIPE,
    #     )
    #     stdout_lines: list[str] = []
    #     stderr_lines: list[str] = []
    #     async def read_stdout() -> None:
    #         if process.stdout:
    #             async for line in process.stdout:
    #                 line_str = line.decode().strip()
    #                 if line_str:
    #                     stdout_lines.append(line_str)
    #                     await ctx.debug(line_str)
    #     async def read_stderr() -> None:
    #         if process.stderr:
    #             async for line in process.stderr:
    #                 line_str = line.decode().strip()
    #                 if line_str:
    #                     stderr_lines.append(line_str)
    #                     await ctx.error(line_str)
    #     await asyncio.gather(read_stdout(), read_stderr())
    #     await process.wait()
    #     if process.returncode != 0:
    #         error_msg = "\n".join(stderr_lines) or "\n".join(stdout_lines)
    #         await ctx.error(f"Deployment failed: {error_msg}")
    #         raise RuntimeError(f"Failed to deploy agent: {error_msg}")
    #     job_id: str | None = None
    #     deploy_namespace: str | None = None
    #     for line in stdout_lines + stderr_lines:
    #         if line.startswith("DEPLOY_JOB_ID="):
    #             job_id = line.split("=", 1)[1]
    #         elif line.startswith("DEPLOY_NAMESPACE="):
    #             deploy_namespace = line.split("=", 1)[1]
    #     await ctx.info(f"Agent '{agent_name}' image uploaded successfully")
    #     return DeployAgentResponse(
    #         agent_name=agent_name, status="submitted", message=message,
    #         job_id=job_id, namespace=deploy_namespace,
    #     )
    # PORT changes vs original:
    #   1. signature: `request: DeployAgentRequest` flattened to `agent_directory: str`.
    #      SecureMCP's _extract_parameters can't introspect pydantic models for the
    #      input schema — it would advertise the tool as a single string parameter.
    #   2. `ctx: Context[ServerSession, None]` → `ctx: Context`. SecureMCP's Context
    #      is a plain dataclass, not generic. ServerSession import dropped at top.
    #   3. every `await ctx.info/debug/error(...)` lost the `await`. SecureMCP's
    #      Context log methods are sync (mcp.py:319-352).
    #   4. `request.agent_directory` → `agent_directory` (no more model wrapper).
    #   5. `return DeployAgentResponse(...)` → `.model_dump()`. SecureMCP wraps
    #      non-dict returns as `{"result": <obj>}`; pydantic objects need the
    #      explicit dict conversion to come through cleanly.
    @mcp.tool()
    async def deploy_agent(
        agent_directory: str,
        ctx: Context,
    ) -> dict:
        """Deploy an agent from directory (auto-discovers namespace from dispatch.yaml).

        Args:
            agent_directory: Path to the agent directory.
            ctx: MCP context for logging.

        Returns:
            Dict with agent_name, status, and deployment message.
        """
        # Convert to absolute path for consistency
        abs_agent_dir = os.path.abspath(agent_directory)

        # Read agent_name from dispatch.yaml for the response
        agent_config = _read_agent_config(abs_agent_dir)
        agent_name = agent_config.get("agent_name") or os.path.basename(abs_agent_dir)

        ctx.info(f"Starting deployment of agent '{agent_name}'")

        # Run dispatch agent deploy with --force --no-wait so it returns
        # after uploading the image without blocking on the full deployment.
        # --force avoids typer.confirm prompts (stdin is DEVNULL).
        process = await asyncio.create_subprocess_exec(
            "dispatch",
            "agent",
            "deploy",
            "--force",
            "--no-wait",
            cwd=abs_agent_dir,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout_lines: list[str] = []
        stderr_lines: list[str] = []

        async def read_stdout() -> None:
            if process.stdout:
                async for line in process.stdout:
                    line_str = line.decode().strip()
                    if line_str:
                        stdout_lines.append(line_str)
                        ctx.debug(line_str)

        async def read_stderr() -> None:
            if process.stderr:
                async for line in process.stderr:
                    line_str = line.decode().strip()
                    if line_str:
                        stderr_lines.append(line_str)
                        ctx.error(line_str)

        await asyncio.gather(read_stdout(), read_stderr())
        await process.wait()

        if process.returncode != 0:
            error_msg = "\n".join(stderr_lines) or "\n".join(stdout_lines)
            ctx.error(f"Deployment failed: {error_msg}")
            raise RuntimeError(f"Failed to deploy agent: {error_msg}")

        # Parse DEPLOY_JOB_ID from CLI output
        job_id: str | None = None
        deploy_namespace: str | None = None
        for line in stdout_lines + stderr_lines:
            if line.startswith("DEPLOY_JOB_ID="):
                job_id = line.split("=", 1)[1]
            elif line.startswith("DEPLOY_NAMESPACE="):
                deploy_namespace = line.split("=", 1)[1]

        ctx.info(f"Agent '{agent_name}' image uploaded successfully")

        message = (
            f"Deployment of '{agent_name}' has been submitted (job_id={job_id}). "
            "The deployment is running in the background and typically takes 3-5 minutes. "
            "Use the get_deploy_status tool with the returned job_id to check progress."
        )

        return DeployAgentResponse(
            agent_name=agent_name,
            status="submitted",
            message=message,
            job_id=job_id,
            namespace=deploy_namespace,
        ).model_dump()

    # PORT (original):
    # @mcp.tool()
    # async def get_deploy_status(request: GetDeployStatusRequest) -> GetDeployStatusResponse:
    #     ns = _get_namespace(request.namespace)
    #     data = await client.get_deploy_status_async(request.job_id, namespace=ns)
    #     ... return GetDeployStatusResponse(job_id=request.job_id, ...)
    @mcp.tool()
    async def get_deploy_status(job_id: str, namespace: str) -> dict:
        """Get the status of a deployment job.

        Use this to poll for deployment progress after deploy_agent returns
        a job_id. Deployments typically take 3-5 minutes.

        Args:
            job_id: Deployment job ID returned by deploy_agent.
            namespace: Namespace (required).

        Returns:
            Dict with status, stages, logs, and error details.
        """
        ns = _get_namespace(namespace)
        data = await client.get_deploy_status_async(job_id, namespace=ns)

        stages = [
            DeployStageInfo(
                name=s.get("name", ""),
                status=s.get("status", ""),
                started_at=s.get("started_at"),
                completed_at=s.get("completed_at"),
            )
            for s in data.get("stages", [])
        ]

        return GetDeployStatusResponse(
            job_id=job_id,
            status=data.get("status", "unknown"),
            version=data.get("version"),
            stages=stages,
            logs=data.get("logs", []),
            error=data.get("error"),
        ).model_dump()

    # PORT (original):
    # @mcp.tool()
    # async def uninstall_agent(request: UninstallAgentRequest) -> UninstallAgentResponse:
    #     ns = _get_namespace(request.namespace)
    #     result = client.delete_agent(request.agent_name, namespace=ns)
    #     return UninstallAgentResponse(**result)
    @mcp.tool()
    async def uninstall_agent(agent_name: str, namespace: str) -> dict:
        """Uninstall an agent and clean up all resources.

        Args:
            agent_name: Agent name.
            namespace: Namespace (required).

        Returns:
            Dict with deletion status and agent_id.
        """
        ns = _get_namespace(namespace)
        result = client.delete_agent(agent_name, namespace=ns)
        return UninstallAgentResponse(**result).model_dump()

    # PORT (original):
    # @mcp.tool()
    # async def stop_agent(request: StopAgentRequest) -> StopAgentResponse:
    #     ns = _get_namespace(request.namespace)
    #     return client.stop_agent(request.agent_name, namespace=ns)
    @mcp.tool()
    async def stop_agent(agent_name: str, namespace: str) -> dict:
        """Stop a running agent by scaling to 0 instances and marking as disabled.

        Args:
            agent_name: Agent name.
            namespace: Namespace (required).

        Returns:
            Dict with status and agent_name.
        """
        ns = _get_namespace(namespace)
        result = client.stop_agent(agent_name, namespace=ns)
        # client.stop_agent may already return a dict; handle both shapes.
        if hasattr(result, "model_dump"):
            return result.model_dump()
        return result

    # PORT (original):
    # @mcp.tool()
    # async def reboot_agent(request: RebootAgentRequest) -> RebootAgentResponse:
    #     ns = _get_namespace(request.namespace)
    #     return client.reboot_agent(request.agent_name, namespace=ns)
    @mcp.tool()
    async def reboot_agent(agent_name: str, namespace: str) -> dict:
        """Reboot an agent by rebuilding from source and forcing a new deployment.

        Preserves environment variables and secrets. Use get_deploy_status with
        the returned job_id to poll for completion.

        Args:
            agent_name: Agent name.
            namespace: Namespace (required).

        Returns:
            Dict with status, agent_name, job_id, and version.
        """
        ns = _get_namespace(namespace)
        result = client.reboot_agent(agent_name, namespace=ns)
        if hasattr(result, "model_dump"):
            return result.model_dump()
        return result

    # PORT (original):
    # @mcp.tool()
    # async def get_agent_logs(request: GetAgentLogsRequest) -> GetAgentLogsResponse:
    #     ns = _get_namespace(request.namespace)
    #     result = client.get_agent_logs(request.agent_name, version=request.version,
    #         limit=request.limit, namespace=ns)
    #     return GetAgentLogsResponse(**result)
    @mcp.tool()
    async def get_agent_logs(
        agent_name: str,
        namespace: str,
        version: str | None = None,
        limit: int = 100,
    ) -> dict:
        """Get recent logs from an agent's CloudWatch logs.

        Args:
            agent_name: Agent name.
            namespace: Namespace (required).
            version: Optional agent version filter.
            limit: Maximum number of log entries (default 100).

        Returns:
            Dict with events array and next_token.
        """
        ns = _get_namespace(namespace)
        result = client.get_agent_logs(
            agent_name,
            version=version,
            limit=limit,
            namespace=ns,
        )
        return GetAgentLogsResponse(**result).model_dump()

    # PORT (original):
    # @mcp.tool()
    # async def get_topic_schema(request: GetTopicSchemaRequest) -> GetTopicSchemaResponse:
    #     ns = _get_namespace(request.namespace)
    #     result = client.get_topic_schema(request.topic, namespace=ns)
    #     return GetTopicSchemaResponse(**result)
    @mcp.tool()
    async def get_topic_schema(topic: str, namespace: str) -> dict:
        """Get schema details for a specific topic.

        Args:
            topic: Topic name.
            namespace: Namespace (required).

        Returns:
            Dict with topic, canonical_schema, and handlers.
        """
        ns = _get_namespace(namespace)
        result = client.get_topic_schema(topic, namespace=ns)
        return GetTopicSchemaResponse(**result).model_dump()

    # PORT (original):
    # @mcp.tool()
    # async def publish_event(request: PublishEventRequest) -> PublishEventResponse:
    #     ns = _get_namespace(request.namespace)
    #     result = client.publish_event(request.topic, request.payload, namespace=ns)
    #     return PublishEventResponse(**result)
    @mcp.tool()
    async def publish_event(topic: str, payload: dict, namespace: str) -> dict:
        """Publish an event to a topic.

        Args:
            topic: Topic name.
            payload: Event payload (JSON-serializable dict).
            namespace: Namespace (required).

        Returns:
            Dict with message and event_uid.
        """
        ns = _get_namespace(namespace)
        result = client.publish_event(topic, payload, namespace=ns)
        return PublishEventResponse(**result).model_dump()

    # PORT (original):
    # @mcp.tool()
    # async def list_topics(request: ListTopicsRequest) -> list[TopicListItem]:
    #     ns = _get_namespace(request.namespace)
    #     return client.list_topics(namespace=ns)
    @mcp.tool()
    async def list_topics(namespace: str) -> list:
        """List all topics in a namespace.

        Returns topics with their subscribed handlers, webhook configuration,
        and schema information.

        Args:
            namespace: Namespace (required).

        Returns:
            List of topic items (dicts) with topic details and subscribers.
        """
        ns = _get_namespace(namespace)
        result = client.list_topics(namespace=ns)
        return [r.model_dump() if hasattr(r, "model_dump") else r for r in result]

    # PORT (original):
    # @mcp.tool()
    # async def get_recent_events(request: GetRecentEventsRequest) -> list[EventRecord]:
    #     ns = _get_namespace(request.namespace)
    #     return client.get_recent_events(namespace=ns, topic=request.topic, limit=request.limit)
    @mcp.tool()
    async def get_recent_events(
        namespace: str, topic: str | None = None, limit: int = 50
    ) -> list:
        """Get recent events, optionally filtered by topic.

        Args:
            namespace: Namespace (required).
            topic: Optional topic filter.
            limit: Maximum number of events (default 50).

        Returns:
            List of event records (dicts).
        """
        ns = _get_namespace(namespace)
        result = client.get_recent_events(namespace=ns, topic=topic, limit=limit)
        return [r.model_dump() if hasattr(r, "model_dump") else r for r in result]

    # PORT (original):
    # @mcp.tool()
    # async def get_event_trace(request: GetEventTraceRequest) -> EventTraceResponse:
    #     ns = _get_namespace(request.namespace)
    #     return client.get_event_trace(trace_id=request.trace_id, namespace=ns)
    @mcp.tool()
    async def get_event_trace(trace_id: str, namespace: str) -> dict:
        """Get the full event trace tree for a given trace ID.

        Returns a tree-structured view of all events in the trace, enriched
        with invocation status, LLM call summaries, and MCP tool calls.

        Args:
            trace_id: Trace ID to fetch.
            namespace: Namespace (required).

        Returns:
            Dict with trace_id, total_events, tree-structured events, and optional llm_summary.
        """
        ns = _get_namespace(namespace)
        result = client.get_event_trace(trace_id=trace_id, namespace=ns)
        if hasattr(result, "model_dump"):
            return result.model_dump()
        return result

    # PORT (original):
    # @mcp.tool()
    # async def get_recent_traces(request: GetRecentTracesRequest) -> RecentTracesResponse:
    #     ns = _get_namespace(request.namespace)
    #     return client.get_recent_traces(namespace=ns, topic=request.topic, limit=request.limit)
    @mcp.tool()
    async def get_recent_traces(
        namespace: str, topic: str | None = None, limit: int = 20
    ) -> dict:
        """Get recent trace summaries for agent invocations.

        Returns summaries of recent traces, including trigger type, involved
        agents, and event counts. Useful for discovering trace IDs to inspect
        with get_event_trace.

        Args:
            namespace: Namespace (required).
            topic: Optional topic filter.
            limit: Maximum number of trace summaries (default 20).

        Returns:
            Dict with total_events, unique_traces, and list of TraceSummary.
        """
        ns = _get_namespace(namespace)
        result = client.get_recent_traces(namespace=ns, topic=topic, limit=limit)
        if hasattr(result, "model_dump"):
            return result.model_dump()
        return result

    # PORT (original):
    # @mcp.tool()
    # async def get_agent_functions(request: GetAgentFunctionsRequest) -> GetAgentFunctionsResponse:
    #     ns = _get_namespace(request.namespace)
    #     agent_info = client.get_agent_info(request.agent_name, namespace=ns)
    #     ...
    #     return GetAgentFunctionsResponse(agent_name=request.agent_name, functions=functions, total=len(functions))
    @mcp.tool()
    async def get_agent_functions(agent_name: str, namespace: str) -> dict:
        """Get the list of functions exposed by an agent.

        Use this to discover what functions are available on an agent
        before invoking them.

        Args:
            agent_name: Agent name.
            namespace: Namespace (required).

        Returns:
            Dict with list of functions and their schemas.
        """
        ns = _get_namespace(namespace)
        agent_info = client.get_agent_info(agent_name, namespace=ns)

        # Extract functions from agent info
        functions_data = agent_info.get("functions", [])
        functions = [
            FunctionSchema(
                name=f.get("name", ""),
                description=f.get("description"),
                input_schema=f.get("input_schema"),
                output_schema=f.get("output_schema"),
            )
            for f in functions_data
        ]

        return GetAgentFunctionsResponse(
            agent_name=agent_name,
            functions=functions,
            total=len(functions),
        ).model_dump()

    # PORT (original):
    # @mcp.tool()
    # async def invoke_function(request: InvokeFunctionRequest) -> InvokeFunctionResponse:
    #     ns = _get_namespace(request.namespace)
    #     invoke_result = await client.invoke_function_async(
    #         agent_name=request.agent_name, function_name=request.function_name,
    #         payload=request.payload, namespace=ns, timeout_seconds=request.timeout_seconds)
    #     ...polls for result if request.wait_for_result, else returns immediately...
    @mcp.tool()
    async def invoke_function(
        agent_name: str,
        function_name: str,
        payload: dict,
        namespace: str,
        wait_for_result: bool = True,
        timeout_seconds: int = 300,
        poll_interval_seconds: float = 1.0,
    ) -> dict:
        """Invoke a function on an agent and optionally wait for the result.

        This is the primary way to call agent functions directly. By default,
        it waits for the function to complete and returns the result.

        Set wait_for_result=False to get the invocation_id immediately
        and poll later using get_invocation_status.

        Args:
            agent_name: Agent name.
            function_name: Function name on the agent.
            payload: Function payload (JSON-serializable dict).
            namespace: Namespace (required).
            wait_for_result: If True, poll until result is available.
            timeout_seconds: Total timeout when waiting (default 300).
            poll_interval_seconds: Poll interval when waiting (default 1.0).

        Returns:
            Dict with status and result (if waited).
        """
        ns = _get_namespace(namespace)

        # Start the invocation (use async method for proper non-blocking)
        invoke_result = await client.invoke_function_async(
            agent_name=agent_name,
            function_name=function_name,
            payload=payload,
            namespace=ns,
            timeout_seconds=timeout_seconds,
        )

        invocation_id = invoke_result.get("invocation_id", "")
        trace_id = invoke_result.get("trace_id", "")
        status = invoke_result.get("status", "PENDING")

        if not wait_for_result:
            # Return immediately without waiting
            return InvokeFunctionResponse(
                invocation_id=invocation_id,
                trace_id=trace_id,
                status=status,
                result=None,
                error=None,
                waited=False,
            ).model_dump()

        # Poll for result using async method
        max_polls = int((timeout_seconds or 300) / poll_interval_seconds)
        for _ in range(max_polls):
            await asyncio.sleep(poll_interval_seconds)

            # Use async polling to avoid blocking the event loop
            status_result = await client.get_invocation_status_async(
                invocation_id, namespace=ns
            )
            status = status_result.get("status", "UNKNOWN").lower()

            if status == "completed":
                result = status_result.get("result")
                return InvokeFunctionResponse(
                    invocation_id=invocation_id,
                    trace_id=trace_id,
                    status=status,
                    result=result,
                    error=None,
                    waited=True,
                ).model_dump()
            elif status == "error":
                error = status_result.get("error", "Unknown error")
                return InvokeFunctionResponse(
                    invocation_id=invocation_id,
                    trace_id=trace_id,
                    status=status,
                    result=None,
                    error=error,
                    waited=True,
                ).model_dump()
            # pending/running - continue polling

        # Timeout waiting for result
        return InvokeFunctionResponse(
            invocation_id=invocation_id,
            trace_id=trace_id,
            status="TIMEOUT",
            result=None,
            error=f"Timed out after {timeout_seconds} seconds",
            waited=True,
        ).model_dump()

    # PORT (original):
    # @mcp.tool()
    # async def get_invocation_status(request: GetInvocationStatusRequest) -> GetInvocationStatusResponse:
    #     ns = _get_namespace(request.namespace)
    #     result = client.get_invocation_status(request.invocation_id, namespace=ns)
    #     return GetInvocationStatusResponse(invocation_id=request.invocation_id, ...)
    @mcp.tool()
    async def get_invocation_status(invocation_id: str, namespace: str) -> dict:
        """Get the status of a previously started invocation.

        Use this to poll for results when invoke_function was called
        with wait_for_result=False.

        Args:
            invocation_id: Invocation ID returned by invoke_function.
            namespace: Namespace (required).

        Returns:
            Dict with status, result, and timestamps.
        """
        ns = _get_namespace(namespace)
        result = client.get_invocation_status(invocation_id, namespace=ns)

        return GetInvocationStatusResponse(
            invocation_id=invocation_id,
            status=result.get("status", "UNKNOWN"),
            result=result.get("result"),
            error=result.get("error"),
            created_at=result.get("created_at"),
            completed_at=result.get("completed_at"),
        ).model_dump()

    # PORT (original):
    # @mcp.tool()
    # async def list_long_term_memories(request: ListLongTermMemoriesRequest) -> ListLongTermMemoriesResponse:
    #     ns = _get_namespace(request.namespace)
    #     return client.list_long_term_memories(request.agent_name, namespace=ns)
    @mcp.tool()
    async def list_long_term_memories(agent_name: str, namespace: str) -> dict:
        """List all long-term memories for an agent.

        Returns all key-value pairs stored in the agent's long-term memory.

        Args:
            agent_name: Agent name.
            namespace: Namespace (required).

        Returns:
            Dict with agent_name and list of memory entries.
        """
        ns = _get_namespace(namespace)
        result = client.list_long_term_memories(agent_name, namespace=ns)
        if hasattr(result, "model_dump"):
            return result.model_dump()
        return result

    # PORT (original):
    # @mcp.tool()
    # async def start_local_agent_dev(
    #     request: StartLocalAgentDevRequest,
    #     ctx: Context[ServerSession, None],
    # ) -> StartLocalAgentDevResponse:
    #     ... uses request.agent_directory, request.router_port, request.enable_reload
    #     ... awaits ctx.info/debug/error/warning throughout
    #     return StartLocalAgentDevResponse(...)
    @mcp.tool()
    async def start_local_agent_dev(
        agent_directory: str,
        ctx: Context,
        router_port: int = LOCAL_ROUTER_PORT,
        enable_reload: bool = False,
    ) -> dict:
        """Start agent in local dev mode (auto-discovers config from dispatch.yaml).

        This starts the local router and agent worker, allowing you to test the agent
        locally without deploying to the cloud.

        Automatically stops any existing dev processes for the same agent before starting.

        When done with development, clean up by executing the stop_local_router tool.

        Args:
            agent_directory: Path to the agent directory.
            ctx: MCP context for logging.
            router_port: Port to expose the router on.
            enable_reload: Enable hot-reload on Python file changes.

        Returns:
            Dict with agent_name, status, and message.
        """
        # Convert to absolute path for consistency
        abs_agent_dir = os.path.abspath(agent_directory)
        agent_name = os.path.basename(abs_agent_dir)

        # Check if local router is running
        try:
            async with httpx.AsyncClient() as http_client:
                response = await http_client.get(
                    f"{LOCAL_ROUTER_URL}:{router_port}/health", timeout=0.5
                )
                response.raise_for_status()
            ctx.debug("Router is running")
        except Exception:
            # Router is not running - start it automatically
            ctx.info("Router is not running, starting it now...")

            # Start the router
            await asyncio.create_subprocess_exec(
                "dispatch",
                "router",
                "start",
                "--port",
                str(router_port),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            # Wait for router with fast retries - router will respond when ready
            router_ready = False
            async with httpx.AsyncClient() as http_client:
                for attempt in range(20):  # 20 attempts * 0.1s = 2s max
                    try:
                        response = await http_client.get(
                            f"{LOCAL_ROUTER_URL}:{router_port}/health", timeout=0.5
                        )
                        response.raise_for_status()
                        router_ready = True
                        ctx.info("Router started successfully")
                        break
                    except Exception:
                        if attempt < 19:
                            await asyncio.sleep(0.1)

            if not router_ready:
                ctx.error("Router failed to start within 2 seconds")
                raise RuntimeError("Router failed to start within 2 seconds")

        # Clean up any existing agent dev processes for this agent
        # Use PID file to track running processes for this specific agent
        pid_file = os.path.join(abs_agent_dir, ".dispatch", "agent.pid")

        if os.path.exists(pid_file):
            ctx.debug("Found PID file for existing agent process...")
            try:
                with open(pid_file) as f:
                    old_pid = int(f.read().strip())

                # Check if process is still running and kill the entire process group
                try:
                    os.killpg(os.getpgid(old_pid), signal.SIGTERM)
                    ctx.info(
                        f"Stopped existing agent dev process group (PID {old_pid})"
                    )
                except ProcessLookupError:
                    # Process already dead, just clean up the PID file
                    ctx.debug(f"Process {old_pid} already stopped")
                except PermissionError:
                    ctx.warning(f"No permission to kill process {old_pid}")

                # Clean up stale PID file
                os.remove(pid_file)
            except (OSError, ValueError) as e:
                ctx.debug(f"Error reading PID file: {e}")

        reload_msg = " with hot-reload" if enable_reload else ""
        ctx.info(f"Starting dev mode for agent '{agent_name}'{reload_msg}")

        # Build command arguments
        cmd_args = [
            "dispatch",
            "agent",
            "dev",
            "--router-port",
            str(router_port),
        ]
        if enable_reload:
            cmd_args.append("--reload")

        # Run dispatch agent dev command in the background
        # Set start_new_session=True to create a new process group
        # This allows us to kill the entire group (parent + all children)
        process = await asyncio.create_subprocess_exec(
            *cmd_args,
            cwd=abs_agent_dir,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            start_new_session=True,
        )

        # Write PID to file so we can stop it later
        pid_file = write_pid_file(abs_agent_dir, process.pid)

        # Collect any startup logs from the CLI output BEFORE starting background monitor
        startup_logs: list[str] = []
        if process.stdout:
            try:
                while True:
                    line = await asyncio.wait_for(
                        process.stdout.readline(), timeout=0.2
                    )
                    if not line:
                        break
                    line_str = line.decode().strip()
                    if line_str:
                        startup_logs.append(line_str)
                        ctx.info(line_str)
            except TimeoutError:
                pass  # No more immediate output

        ctx.info(
            f"Dev mode started for agent '{agent_name}' (running in background)"
        )

        # Start background task to read remaining output
        # Note: Don't clean up PID file here - it should persist even after MCP server exits
        # PID file is cleaned up by: start_local_agent_dev (auto-cleanup) or stop_local_router
        async def monitor_process():
            """Monitor process output in the background."""
            try:
                if process.stdout:
                    async for line in process.stdout:
                        line_str = line.decode().strip()
                        if line_str:
                            ctx.debug(f"[{agent_name}] {line_str}")
                if process.stderr:
                    async for line in process.stderr:
                        line_str = line.decode().strip()
                        if line_str:
                            ctx.debug(f"[{agent_name}] {line_str}")
            except Exception as e:
                ctx.error(f"Error monitoring {agent_name}: {e}")

        # Start monitoring in the background (after we've read startup warnings)
        asyncio.create_task(monitor_process())

        router_ui_url = f"{LOCAL_ROUTER_URL}:{router_port}"

        return StartLocalAgentDevResponse(
            agent_name=agent_name,
            status="running",
            message=f"Agent '{agent_name}' is running in dev mode.\n\n"
            f"View the router UI at: {router_ui_url}\n"
            f"Send test events using the send_local_test_event tool.",
            router_ui_url=router_ui_url,
            startup_logs=startup_logs,
        ).model_dump()

    # PORT (original):
    # @mcp.tool()
    # async def stop_local_router(request: StopRouterRequest, ctx: Context[ServerSession, None]) -> StopRouterResponse:
    #     ... awaits ctx.info/debug/error throughout, returns StopRouterResponse
    @mcp.tool()
    async def stop_local_router(ctx: Context) -> dict:
        """Stop the local dispatch router.

        This also cleans up any agent dev processes started with start_local_agent_dev.

        Args:
            ctx: MCP context for logging.

        Returns:
            Dict with status and message.
        """
        ctx.info("Stopping router")

        # Build command
        cmd = ["dispatch", "router", "stop"]

        # Run dispatch router stop command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode().strip() or stdout.decode().strip()

            # Check if router was already stopped (connection refused)
            if (
                "Connection refused" in error_msg
                or "Could not stop router" in error_msg
                or "No router found" in error_msg
            ):
                ctx.info("Router is already stopped")

                # Still clean up any agent dev processes using PID files
                ctx.info("Cleaning up agent dev processes...")
                cleaned = await cleanup_all_agent_processes()
                if cleaned > 0:
                    ctx.info(f"Stopped {cleaned} agent process(es)")

                return StopRouterResponse(
                    status="stopped",
                    message="Router is already stopped (agent dev processes cleaned up)",
                ).model_dump()

            # Other errors should still be raised
            ctx.error(f"Failed to stop router: {error_msg}")
            raise RuntimeError(f"Failed to stop router: {error_msg}")

        ctx.info("Router stopped successfully")

        # Also kill any dispatch agent dev processes using PID files
        ctx.info("Cleaning up agent dev processes...")
        cleaned = await cleanup_all_agent_processes()
        if cleaned > 0:
            ctx.info(f"Stopped {cleaned} agent process(es)")
        else:
            ctx.debug("No agent processes to clean up")

        return StopRouterResponse(
            status="stopped",
            message="Router stopped (agent dev processes cleaned up)",
        ).model_dump()

    # PORT (original):
    # @mcp.tool()
    # async def list_local_routers(request: ListRoutersRequest, ctx: Context[ServerSession, None]) -> ListRoutersResponse:
    #     ... awaits ctx.debug, returns ListRoutersResponse
    @mcp.tool()
    async def list_local_routers(ctx: Context) -> dict:
        """List all tracked local routers.

        Shows all routers that have been started and are being tracked,
        along with their current status.

        Args:
            ctx: MCP context for logging.

        Returns:
            Dict with list of tracked routers.
        """
        from dispatch_cli.commands.router import get_tracked_routers

        ctx.debug("Listing tracked routers")

        routers_data = get_tracked_routers()
        routers = [
            RouterInfo(
                port=r.get("port", 0),
                pid=r.get("pid", 0),
                started_at=r.get("started_at", ""),
                running=r.get("running", False),
            )
            for r in routers_data
        ]

        running_count = sum(1 for r in routers if r.running)
        ctx.info(
            f"Found {len(routers)} tracked router(s), {running_count} running"
        )

        return ListRoutersResponse(routers=routers, total=len(routers)).model_dump()

    # PORT (original):
    # @mcp.tool()
    # async def send_local_test_event(request: SendTestEventRequest, ctx: Context[ServerSession, None]) -> SendTestEventResponse:
    #     ... uses request.topic, request.payload, request.router_port; awaits ctx.info/error
    @mcp.tool()
    async def send_local_test_event(
        topic: str,
        payload: dict,
        ctx: Context,
        router_port: int = LOCAL_ROUTER_PORT,
    ) -> dict:
        """Send a test event through the local router using dispatch router test.

        Args:
            topic: Topic name.
            payload: Event payload (JSON-serializable dict).
            ctx: MCP context for logging.
            router_port: Local router port (default LOCAL_ROUTER_PORT).

        Returns:
            Dict with status and message.
        """
        ctx.info(f"Sending test event to topic '{topic}'")

        # Call the router API directly
        local_router_url = f"{LOCAL_ROUTER_URL}:{router_port}"
        event_data = {"payload": payload, "sender_id": "mcp-test"}

        try:
            timeout = aiohttp.ClientTimeout(total=60.0 * 60 * 24)  # 24 hours
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{local_router_url}/api/unstable/events/{topic}",
                    json=event_data,
                ) as response:
                    response.raise_for_status()
                    result = await response.json()

            # Parse the router response
            status = result.get("status", "unknown")
            message = result.get("message", "No message")
            trace_id = result.get("trace_id")

            # Parse routed_to agents
            routed_to = [
                AgentRouteInfo(name=agent["name"], topics=agent["topics"])
                for agent in result.get("routed_to", [])
            ]

            # Parse agent responses
            responses = {}
            for agent_name, agent_response in result.get("responses", {}).items():
                responses[agent_name] = AgentResponse(
                    result=agent_response.get("result"),
                    error=agent_response.get("error"),
                    status=agent_response.get("status"),
                )

            ctx.info(f"Event routed to {len(routed_to)} agent(s)")

            return SendTestEventResponse(
                status=status,
                message=message,
                event_uid=trace_id,
                routed_to=routed_to,
                responses=responses,
            ).model_dump()

        except aiohttp.ClientError as e:
            error_msg = f"HTTP error: {e}"
            ctx.error(f"Failed to send event: {error_msg}")
            raise RuntimeError(f"Failed to send event: {error_msg}")
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            ctx.error(f"Failed to send event: {error_msg}")
            raise RuntimeError(f"Failed to send event: {error_msg}")

    # PORT (original):
    # @mcp.tool()
    # async def invoke_local_function(request: InvokeLocalFunctionRequest, ctx: Context[ServerSession, None]) -> InvokeLocalFunctionResponse:
    #     ... uses request.agent_directory, request.function_name, request.payload, request.router_port, request.timeout_seconds
    #     ... awaits ctx.info/debug/error throughout
    #     return InvokeLocalFunctionResponse(...)
    @mcp.tool()
    async def invoke_local_function(
        agent_directory: str,
        function_name: str,
        ctx: Context,
        payload: dict | None = None,
        router_port: int = LOCAL_ROUTER_PORT,
        timeout_seconds: int = 60,
    ) -> dict:
        """Invoke a function on a locally running agent.

        This tool calls @fn() decorated functions on agents running in local dev mode.
        It waits for the function to complete and returns the result directly.

        Prerequisites:
        - Agent must be running (start_local_agent_dev starts both router and agent)

        Args:
            agent_directory: Path to the agent directory.
            function_name: Name of the function to invoke.
            ctx: MCP context for logging.
            payload: Input payload for the function (default empty dict).
            router_port: Local router port.
            timeout_seconds: Request timeout in seconds.

        Returns:
            Dict with status and result.
        """
        if payload is None:
            payload = {}
        # Get agent name from directory
        abs_agent_dir = os.path.abspath(agent_directory)
        agent_name = os.path.basename(abs_agent_dir)
        local_router_url = f"{LOCAL_ROUTER_URL}:{router_port}"

        ctx.info(
            f"Invoking function '{function_name}' on agent '{agent_name}'"
        )

        try:
            timeout = aiohttp.ClientTimeout(total=float(timeout_seconds))
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Step 1: Start the invocation
                invoke_data = {
                    "agent_name": agent_name,
                    "function_name": function_name,
                    "payload": payload,
                    "timeout_seconds": timeout_seconds,
                }

                async with session.post(
                    f"{local_router_url}/api/unstable/invoke",
                    json=invoke_data,
                ) as response:
                    if response.status == 404:
                        error_detail = await response.text()
                        return InvokeLocalFunctionResponse(
                            status="error",
                            result=None,
                            error=f"Agent '{agent_name}' not found. Is it running? Error: {error_detail}",
                            agent_name=agent_name,
                        ).model_dump()
                    response.raise_for_status()
                    invoke_result = await response.json()

                invocation_id = invoke_result.get("invocation_id")
                if not invocation_id:
                    return InvokeLocalFunctionResponse(
                        status="error",
                        result=None,
                        error="No invocation_id returned from router",
                        agent_name=agent_name,
                    ).model_dump()

                ctx.debug(f"Invocation started: {invocation_id}")

                # Step 2: Poll for completion
                poll_interval = 0.2  # 200ms between polls
                max_polls = int(timeout_seconds / poll_interval)

                for _ in range(max_polls):
                    async with session.get(
                        f"{local_router_url}/api/unstable/invoke/{invocation_id}",
                    ) as status_response:
                        status_response.raise_for_status()
                        status_data = await status_response.json()

                    status = status_data.get("status", "unknown")

                    if status == "completed":
                        result = status_data.get("result")
                        ctx.info(
                            f"Function '{function_name}' completed successfully"
                        )
                        return InvokeLocalFunctionResponse(
                            status="success",
                            result=result,
                            error=None,
                            agent_name=agent_name,
                        ).model_dump()

                    if status == "error":
                        error = status_data.get("error", "Unknown error")
                        ctx.error(f"Function failed: {error}")
                        return InvokeLocalFunctionResponse(
                            status="error",
                            result=None,
                            error=error,
                            agent_name=agent_name,
                        ).model_dump()

                    # Still pending, wait and poll again
                    await asyncio.sleep(poll_interval)

                # Timeout reached
                return InvokeLocalFunctionResponse(
                    status="error",
                    result=None,
                    error=f"Timeout after {timeout_seconds}s waiting for function to complete",
                    agent_name=agent_name,
                ).model_dump()

        except aiohttp.ClientError as e:
            error_msg = f"HTTP error: {e}"
            ctx.error(f"Failed to invoke function: {error_msg}")
            return InvokeLocalFunctionResponse(
                status="error",
                result=None,
                error=error_msg,
                agent_name=agent_name,
            ).model_dump()
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            ctx.error(f"Failed to invoke function: {error_msg}")
            return InvokeLocalFunctionResponse(
                status="error",
                result=None,
                error=error_msg,
                agent_name=agent_name,
            ).model_dump()

    # PORT (original):
    # @mcp.tool()
    # async def read_local_agent_logs(request: ReadLocalAgentLogsRequest, ctx: Context[ServerSession, None]) -> ReadLocalAgentLogsResponse:
    #     ... uses request.agent_directory, request.lines; awaits ctx.debug/info
    @mcp.tool()
    async def read_local_agent_logs(
        agent_directory: str,
        ctx: Context,
        lines: int = 50,
    ) -> dict:
        """Read recent logs from a local agent dev process.

        Reads the most recent log lines from the agent's log file.
        The log file is created when you start the agent with start_local_agent_dev.

        Args:
            agent_directory: Path to the agent directory.
            ctx: MCP context for logging.
            lines: Number of recent log lines to return (default 50).

        Returns:
            Dict with agent_name, logs, and total_lines.
        """
        # Convert to absolute path for consistency
        abs_agent_dir = os.path.abspath(agent_directory)
        agent_name = os.path.basename(abs_agent_dir)

        ctx.debug(f"Reading logs for agent '{agent_name}'...")

        # Use helper function to read logs
        try:
            logs = read_agent_log_file(abs_agent_dir, lines=lines)
            ctx.info(f"Retrieved {len(logs)} log lines for agent '{agent_name}'")
        except FileNotFoundError as e:
            raise RuntimeError(
                f"No log file found for agent '{agent_name}'. "
                "Start the agent first using start_local_agent_dev."
            ) from e

        return ReadLocalAgentLogsResponse(
            agent_name=agent_name, logs=logs, total_lines=len(logs)
        ).model_dump()

    # Schedule Management Tools
    # PORT (originals): each tool used to take `request: SomeScheduleRequest` and pass it
    # straight to the matching `client.<method>(request)` call. Ported tools accept the
    # request fields as flat kwargs and reconstruct the pydantic model internally.

    @mcp.tool()
    async def create_schedule(
        agent_name: str,
        function_name: str,
        cron_expression: str,
        namespace: str,
        timezone: str = "UTC",
        payload: dict | None = None,
        description: str | None = None,
        timeout_seconds: int | None = None,
    ) -> dict:
        """Create a new function schedule with a cron expression.

        Schedules trigger a function on an agent at specified times based on a cron expression.
        The schedule becomes active immediately and will start triggering at the specified times.

        Common cron patterns:
        - '* * * * *' - Every minute
        - '*/5 * * * *' - Every 5 minutes
        - '0 * * * *' - Every hour
        - '0 9 * * *' - Daily at 9am
        - '0 9 * * MON-FRI' - Weekdays at 9am
        - '0 0 1 * *' - First day of each month at midnight

        Args:
            agent_name: Target agent name.
            function_name: Function to invoke on each trigger.
            cron_expression: Cron expression.
            namespace: Dispatch namespace.
            timezone: Timezone for the cron expression (default UTC).
            payload: Static payload passed on each invocation (default empty).
            description: Optional human-readable description.
            timeout_seconds: Per-invocation timeout in seconds (1-86400).

        Returns:
            Dict with schedule_id and confirmation message.
        """
        request = CreateScheduleRequest(
            agent_name=agent_name,
            function_name=function_name,
            cron_expression=cron_expression,
            namespace=namespace,
            timezone=timezone,
            payload=payload or {},
            description=description,
            timeout_seconds=timeout_seconds,
        )
        result = await client.create_schedule(request)
        if hasattr(result, "model_dump"):
            return result.model_dump()
        return result

    @mcp.tool()
    async def list_schedules(
        namespace: str,
        agent_name: str | None = None,
    ) -> dict:
        """List all schedules in the namespace.

        Optionally filter by agent name to see only schedules for a specific agent.

        Args:
            namespace: Dispatch namespace.
            agent_name: Optional filter by agent name.

        Returns:
            Dict with list of schedules and total count.
        """
        request = ListSchedulesRequest(namespace=namespace, agent_name=agent_name)
        result = await client.list_schedules(request)
        if hasattr(result, "model_dump"):
            return result.model_dump()
        return result

    @mcp.tool()
    async def get_schedule(schedule_id: str, namespace: str) -> dict:
        """Get details for a specific schedule.

        Args:
            schedule_id: Schedule ID to retrieve.
            namespace: Dispatch namespace.

        Returns:
            Dict with full schedule details.
        """
        request = GetScheduleRequest(schedule_id=schedule_id, namespace=namespace)
        result = await client.get_schedule(request)
        if hasattr(result, "model_dump"):
            return result.model_dump()
        return result

    @mcp.tool()
    async def update_schedule(
        schedule_id: str,
        namespace: str,
        cron_expression: str | None = None,
        timezone: str | None = None,
        payload: dict | None = None,
        description: str | None = None,
        is_paused: bool | None = None,
    ) -> dict:
        """Update a schedule's configuration.

        Can update any combination of: cron expression, timezone, payload, description.
        Use is_paused=true to pause the schedule (stop triggering) or is_paused=false to resume.

        Args:
            schedule_id: Schedule ID to update.
            namespace: Dispatch namespace.
            cron_expression: New cron expression (optional).
            timezone: New timezone (optional).
            payload: New payload (optional).
            description: New description (optional).
            is_paused: Set to true to pause, false to resume.

        Returns:
            Dict with updated schedule details.
        """
        request = UpdateScheduleRequest(
            schedule_id=schedule_id,
            namespace=namespace,
            cron_expression=cron_expression,
            timezone=timezone,
            payload=payload,
            description=description,
            is_paused=is_paused,
        )
        result = await client.update_schedule(request)
        if hasattr(result, "model_dump"):
            return result.model_dump()
        return result

    @mcp.tool()
    async def delete_schedule(schedule_id: str, namespace: str) -> dict:
        """Delete a schedule permanently.

        The schedule will stop triggering immediately. This action cannot be undone.

        Args:
            schedule_id: Schedule ID to delete.
            namespace: Dispatch namespace.

        Returns:
            Dict with confirmation message.
        """
        request = DeleteScheduleRequest(schedule_id=schedule_id, namespace=namespace)
        result = await client.delete_schedule(request)
        if hasattr(result, "model_dump"):
            return result.model_dump()
        return result

    @mcp.prompt()
    def local_agent_dev() -> str:
        """Interactive workflow to test an agent locally.

        Guides you through:
        1. Starting the agent in dev mode
        2. Selecting and sending a test event to one of the agent's functions
        3. Checking the agent logs for any errors

        This prompt dynamically discovers available agent directories by searching
        for dispatch.yaml files.
        """
        # Find all directories containing dispatch.yaml (or legacy .dispatch.yaml).
        # Depth-limited walk to avoid hanging in large trees.
        cwd = Path.cwd()
        agent_dirs: list[str] = []
        max_depth = 4
        skip_dirs = {
            ".git",
            "node_modules",
            ".venv",
            "__pycache__",
            ".tox",
            ".mypy_cache",
        }
        dispatch_names = {DISPATCH_YAML}

        for dirpath, dirnames, filenames in os.walk(cwd):
            depth = Path(dirpath).relative_to(cwd).parts
            if len(depth) >= max_depth:
                dirnames.clear()
                continue
            # Prune heavy/irrelevant subtrees
            dirnames[:] = [d for d in dirnames if d not in skip_dirs]

            if dispatch_names & set(filenames):
                agent_dir = str(Path(dirpath).relative_to(cwd))
                if agent_dir not in agent_dirs:
                    agent_dirs.append(agent_dir)

        agent_dirs = sorted(agent_dirs)

        # Build the list of available directories
        if agent_dirs:
            dirs_list = "\n".join(f"   - {d}" for d in agent_dirs)
            agent_selection = f"""Available agent directories found:
{dirs_list}

First, ask me if I want to:
A) Test one of the existing agents listed above
B) Create a new agent first, then test it

If I choose A, ask which existing agent to test.
If I choose B, help me create a new agent using the create_agent tool."""
        else:
            agent_selection = """No existing agent directories found.

Let's create a new agent first using the create_agent tool. Ask me for:
- Parent directory (e.g., "." or a subdirectory)
- Agent name (e.g., "my-test-agent")
- Description of what the agent does"""

        return f"""I want to test a Dispatch agent locally. Please help me:

{agent_selection}

Once we have an agent directory (either existing or newly created), walk me through these steps:

1. Start the agent in dev mode
   - Use the start_local_agent_dev tool with the selected agent directory
   - This will automatically start the router if needed

2. After the agent is running, list the available functions/topics for this agent
   - You can check the agent's code or configuration to see what functions it exposes
   - Ask me which topic or function I want to test

3. Send a test event to the selected topic/function
   - Use the send_local_test_event tool
   - Construct an appropriate payload based on the function's input schema
   - Show me the response from the agent

4. Check the agent logs for any errors
   - Use the read_local_agent_logs tool to retrieve recent logs
   - Look for any error messages or stack traces
   - Summarize what the logs show

Please walk me through each step, waiting for confirmation before proceeding to the next step."""

    # =========================================================================
    # Feedback
    # =========================================================================

    class SubmitFeedbackRequest(BaseModel):
        """Request payload for submitting feedback."""

        feedback_type: FeedbackType = Field(
            default="general",
            description="Type of feedback: bug, feature_request, or general",
        )
        message: str = Field(
            description=(
                "Feedback message. Include relevant context such as the agent "
                "name, namespace, what operation was being performed, and any "
                "error details if reporting a bug."
            ),
        )
        reproduction_steps: str | None = Field(
            default=None,
            description=(
                "For bug reports: minimal, complete steps to reproduce the "
                "error. Include the exact commands or actions taken, the "
                "expected outcome, and the actual outcome. Strip out anything "
                "not needed to trigger the bug — the goal is a minimal "
                "reproducible example, not a full project dump."
            ),
        )
        sentiment: FeedbackSentiment | None = Field(
            default=None,
            description="Optional sentiment: 'positive' or 'negative'",
        )

    class SubmitFeedbackResponse(BaseModel):
        """Response from submitting feedback."""

        pass

    # PORT (original):
    # @mcp.tool()
    # async def submit_feedback(request: SubmitFeedbackRequest) -> SubmitFeedbackResponse:
    #     await client.submit_feedback(request.model_dump())
    #     return SubmitFeedbackResponse()
    @mcp.tool()
    async def submit_feedback(
        message: str,
        feedback_type: str = "general",
        reproduction_steps: str | None = None,
        sentiment: str | None = None,
    ) -> dict:
        """Send feedback to the Dispatch Agents team.

        If you encounter anything unintuitive, broken, or have suggestions
        or feature requests about Dispatch Agents, use this tool to send
        them directly to the team.

        IMPORTANT: Do NOT include any proprietary or personal information
        about the user's project, company, or data in the message. Keep
        feedback focused on the Dispatch Agents platform itself.

        Args:
            message: Feedback message.
            feedback_type: Type of feedback (bug, feature_request, general).
            reproduction_steps: For bug reports, minimal steps to reproduce.
            sentiment: Optional sentiment ('positive' or 'negative').
        """
        request = SubmitFeedbackRequest(
            message=message,
            feedback_type=feedback_type,
            reproduction_steps=reproduction_steps,
            sentiment=sentiment,
        )
        await client.submit_feedback(request.model_dump())
        return SubmitFeedbackResponse().model_dump()

    # ── MCP Prompts (loaded from markdown files) ──────────────────────
    # Prompts are the cross-client equivalent of Claude Code skills.
    # Any MCP client (Claude, Cursor, Codex) can list and invoke them.

    _prompts_dir = Path(__file__).parent / "prompts"

    @mcp.prompt()
    def getting_started() -> str:
        """Build and deploy a Dispatch Agent from scratch.

        Step-by-step guide: scaffold, write handlers, test locally, deploy.
        Use when the user wants to create an agent or get started with
        Dispatch Agents.
        """
        return (_prompts_dir / "getting-started.md").read_text()

    @mcp.prompt()
    def fork_session() -> str:
        """Fork the current AI session into a Dispatch agent container.

        Creates a remote copy of the current conversation running inside
        a container with shell access, persistent storage, and network
        access to internal services.
        """
        return (_prompts_dir / "fork-session.md").read_text()

    return mcp
