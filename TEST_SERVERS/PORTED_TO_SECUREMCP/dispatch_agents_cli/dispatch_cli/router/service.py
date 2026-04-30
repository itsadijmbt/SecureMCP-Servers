"""Local router service for testing multi-agent workflows."""

import asyncio
import json
import os
import signal
import subprocess
import uuid
from collections import deque
from datetime import UTC, datetime
from typing import Any

import grpc
import httpx
from agentservice.v1 import (
    message_pb2,
    request_response_pb2,
    service_pb2_grpc,
)
from dispatch_agents import LLMToolCall
from dispatch_agents.models import (
    EventRequest,
    FunctionMessage,
    InvokeFunctionRequest,
    KVStoreRequest,
    Message,
    PublishEventBody,
    PublishResponse,
    SessionStoreRequest,
    StrictBaseModel,
    SubscriptionBody,
    SubscriptionResponse,
    TopicMessage,
)
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import Field

from dispatch_cli.commands.agent import (
    stop_local_agent_by_name,
    unregister_local_agent,
)
from dispatch_cli.logger import get_logger, set_logger
from dispatch_cli.secrets import load_secrets_to_env
from dispatch_cli.utils import LOCAL_ROUTER_PORT

# Initialize logger for standalone uvicorn mode (not run through CLI main)
set_logger()

# Load secrets for local development
# 1. Load from ~/.dispatch/secrets.yaml (Keychain-backed centralized secrets)
# 2. Fallback to environment variables and cwd/.env
_loaded_secrets = load_secrets_to_env(warn_on_raw=True)
load_dotenv()  # Also try cwd/.env as fallback for legacy support

DEV_NAMESPACE = "dev"


def _kill_process_by_port(port: int) -> tuple[bool, str]:
    """Kill the process listening on the specified port.

    Uses lsof to find the process ID and sends SIGTERM to stop it gracefully.

    Args:
        port: The port number to look up

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Use lsof to find the process ID listening on this port
        result = subprocess.run(
            ["lsof", "-t", "-i", f":{port}"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0 or not result.stdout.strip():
            return False, f"No process found listening on port {port}"

        # lsof -t returns just the PID(s), one per line
        pids = result.stdout.strip().split("\n")
        killed_pids = []

        for pid_str in pids:
            try:
                pid = int(pid_str.strip())
                os.kill(pid, signal.SIGTERM)
                killed_pids.append(pid)
            except (ValueError, ProcessLookupError):
                # Process may have already exited
                continue

        if killed_pids:
            return True, f"Killed process(es) {killed_pids} on port {port}"
        else:
            return False, f"Could not kill any processes on port {port}"

    except subprocess.TimeoutExpired:
        return False, f"Timeout looking up process on port {port}"
    except FileNotFoundError:
        return False, "lsof command not found (required for process lookup)"
    except Exception as e:
        return False, f"Error killing process on port {port}: {e}"


def _stop_agent_by_name_or_port(
    agent_name: str, port: int | None = None
) -> tuple[bool, str]:
    """Stop an agent using PID tracking first, then fall back to port-based lookup.

    This provides a more reliable way to stop agents since PID tracking doesn't
    depend on lsof or external tools.

    Args:
        agent_name: Name of the agent to stop
        port: Optional port to fall back to if PID tracking fails

    Returns:
        Tuple of (success: bool, message: str)
    """
    # First, try to stop using PID tracking (more reliable)
    success, message = stop_local_agent_by_name(agent_name)
    if success:
        return True, f"Stopped via PID tracking: {message}"

    # If PID tracking failed and we have a port, try port-based lookup
    if port is not None:
        success, message = _kill_process_by_port(port)
        if success:
            # Clean up stale tracking file if it exists
            unregister_local_agent(agent_name)
            return True, f"Stopped via port lookup: {message}"

    return False, message


def _stop_all_agents_sync() -> tuple[list[str], list[dict]]:
    """Synchronously stop all registered agents.

    This is a synchronous version for use in signal handlers and shutdown hooks
    where we can't use async/await.

    Uses PID tracking as primary method (more reliable), with port-based lookup
    as fallback for agents started before PID tracking was implemented.

    Returns:
        Tuple of (stopped_agents: list[str], failed_agents: list[dict])
    """
    logger = get_logger()
    stopped_agents = []
    failed_agents = []

    # Access the global _agents dict directly (no async lock in sync context)
    # This is safe during shutdown as no new requests are being processed
    agents_to_stop = list(_agents.items())

    for agent_name, agent_data in agents_to_stop:
        agent_url = agent_data.get("url", "")

        # Extract port for fallback (may be None if URL is missing)
        port = None
        if agent_url:
            try:
                port = int(agent_url.split(":")[-1])
            except (ValueError, IndexError):
                pass

        # Use unified stop function (PID tracking first, then port fallback)
        success, message = _stop_agent_by_name_or_port(agent_name, port)
        if success:
            stopped_agents.append(agent_name)
            logger.info(f"Stopped agent {agent_name}: {message}")
        else:
            failed_agents.append({"agent": agent_name, "reason": message})
            logger.warning(f"Failed to stop agent {agent_name}: {message}")

    # Clear storage
    _agents.clear()
    _subscriptions_by_topic.clear()

    logger.info(f"Cleanup complete: stopped {len(stopped_agents)} agent(s)")
    return stopped_agents, failed_agents


async def store_message(message: Message):
    """Store a message in the thread storage for UI display."""
    # Build message data based on message type
    if isinstance(message, TopicMessage):
        msg_data = {
            "uid": message.uid,
            "type": "topic",
            "topic": message.topic,
            "payload": message.payload,
            "trace_id": message.trace_id,
            "sender_id": message.sender_id,
            "ts": message.ts,
            "parent_id": message.parent_id,
            "stored_at": datetime.now().isoformat(),
        }
    elif isinstance(message, FunctionMessage):
        msg_data = {
            "uid": message.uid,
            "type": "function",
            "function_name": message.function_name,
            "payload": message.payload,
            "trace_id": message.trace_id,
            "sender_id": message.sender_id,
            "ts": message.ts,
            "parent_id": message.parent_id,
            "stored_at": datetime.now().isoformat(),
        }
    else:
        logger = get_logger()
        logger.warning(
            f"Unsupported message type in store_message: {type(message).__name__}"
        )
        return

    async with _message_storage_lock:
        # Add to trace-specific storage
        if message.trace_id not in _messages_by_trace_id:
            _messages_by_trace_id[message.trace_id] = deque(maxlen=100)
        _messages_by_trace_id[message.trace_id].append(msg_data)

        # Add to global recent messages
        _all_recent_messages.append(msg_data)


async def store_llm_call(llm_call_data: dict[str, Any]) -> None:
    """Store an LLM call for trace visualization.

    LLM calls are stored separately from messages and joined by trace_id
    when retrieving traces. This mirrors the backend pattern.
    """
    async with _llm_calls_lock:
        # Add to global recent LLM calls
        _llm_calls.append(llm_call_data)

        # Add to trace-specific storage if trace_id is present
        trace_id = llm_call_data.get("trace_id")
        if trace_id:
            if trace_id not in _llm_calls_by_trace_id:
                _llm_calls_by_trace_id[trace_id] = deque(maxlen=50)
            _llm_calls_by_trace_id[trace_id].append(llm_call_data)


class SystemStatus(StrictBaseModel):
    """System status response."""

    total_agents: int
    registered_agents: int
    network_name: str = "dispatch-network"


# Backend-compatible subscription storage
_subscriptions_lock: asyncio.Lock = asyncio.Lock()
_subscriptions_by_topic: dict[str, set[str]] = {}

# In-memory agent storage (replaces SQLite registry for local dev)
# Stores agent data when agents subscribe - if not subscribed, agent doesn't exist
_agents_lock: asyncio.Lock = asyncio.Lock()
_agents: dict[str, dict] = {}  # agent_name -> {url, functions, topics, last_seen}

# Pre-registered agent URLs (set by CLI before agent starts)
# This allows CLI to tell router the correct gRPC port before the agent subscribes
_preregistered_urls_lock: asyncio.Lock = asyncio.Lock()
_preregistered_urls: dict[str, str] = {}  # agent_name -> url (e.g., "127.0.0.1:50052")

# In-memory memory storage for local development
_memory_lock: asyncio.Lock = asyncio.Lock()
_long_term_memory: dict[
    tuple[str, str, str], dict
] = {}  # (agent_name, namespace, key) -> {"value": str, "created_at": str}
_short_term_memory: dict[
    tuple[str, str, str], dict
] = {}  # (agent_name, namespace, session_id) -> {"session_data": dict, "created_at": str}


# Message thread storage (in-memory, for development use)
_message_storage_lock: asyncio.Lock = asyncio.Lock()
_messages_by_trace_id: dict[
    str, deque
] = {}  # trace_id -> deque of messages (max 100 per thread)
_all_recent_messages: deque = deque(maxlen=500)  # Last 500 messages across all threads

# Invocation storage (in-memory, for local development)
_invocations_lock: asyncio.Lock = asyncio.Lock()
_invocations: dict[str, dict[str, Any]] = {}  # invocation_id -> invocation record

# LLM call storage (in-memory, for local development)
# Stored separately and joined by trace_id (mirrors backend pattern with ClickHouse)
_llm_calls_lock: asyncio.Lock = asyncio.Lock()
_llm_calls: deque = deque(maxlen=500)  # Recent LLM calls across all traces
_llm_calls_by_trace_id: dict[str, deque] = {}  # trace_id -> deque of LLM calls


class InvocationStatus:
    """Invocation status enum for local router."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"


# InvokeFunctionRequest is imported from dispatch_agents.models (SDK)
# to ensure API consistency between SDK, backend, and local router


class InvokeFunctionResponse(StrictBaseModel):
    """Response from initiating a function invocation."""

    invocation_id: str
    trace_id: str
    status: str


class InvocationStatusResponse(StrictBaseModel):
    """Response for invocation status polling."""

    invocation_id: str
    status: str
    agent_name: str
    function_name: str
    trace_id: str
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: str


# LLM request/response models (mirrors backend/models/llm.py)
class LLMMessage(StrictBaseModel):
    """A message in a conversation."""

    role: str = Field(description="Message role: system, user, assistant, tool")
    content: str | list[dict[str, Any]] | None = Field(
        default=None, description="Message content"
    )
    name: str | None = Field(default=None, description="Optional name for the author")
    tool_call_id: str | None = Field(
        default=None, description="Tool call ID for tool responses"
    )
    tool_calls: list[dict[str, Any]] | None = Field(
        default=None, description="Tool calls from assistant"
    )


class LLMInferenceRequest(StrictBaseModel):
    """Request for LLM inference via local router."""

    messages: list[LLMMessage] = Field(description="Conversation messages")
    model: str | None = Field(
        default=None,
        description="Model to use (uses configured default if not specified). "
        "Must be the canonical name expected by the provider API "
        "(e.g., gpt-4o, gpt-4o-mini, claude-3-5-sonnet-20241022, gemini-1.5-flash)",
    )
    provider: str | None = Field(
        default=None,
        description="Provider name (openai, anthropic, google). Uses configured default if not specified.",
    )
    tools: list[dict[str, Any]] | None = Field(
        default=None, description="Tool definitions for function calling"
    )
    temperature: float = Field(
        default=1.0, ge=0, le=2, description="Sampling temperature"
    )
    max_tokens: int | None = Field(default=None, description="Max tokens in response")
    response_format: dict[str, Any] | None = Field(
        default=None, description="Structured output format"
    )
    trace_id: str | None = Field(default=None, description="Trace ID for correlation")
    invocation_id: str | None = Field(
        default=None, description="Invocation ID if called from agent handler"
    )
    agent_name: str | None = Field(
        default=None, description="Agent name for cost tracking"
    )
    extra_headers: dict[str, str] | None = Field(
        default=None, description="Extra headers to forward to the LLM provider"
    )


class LLMInferenceResponse(StrictBaseModel):
    """Response from LLM inference."""

    llm_call_id: str = Field(description="Unique ID for this LLM call")
    content: str | None = Field(default=None, description="Text response content")
    tool_calls: list[LLMToolCall] | None = Field(
        default=None, description="Tool calls from response"
    )
    finish_reason: str = Field(description="Reason for completion")
    model: str = Field(description="Model that was used")
    provider: str = Field(description="Provider that was used")
    variant_name: str | None = Field(default=None, description="Not used in local mode")
    input_tokens: int = Field(description="Prompt token count")
    output_tokens: int = Field(description="Completion token count")
    cost_usd: float = Field(description="Calculated cost in USD")
    latency_ms: int = Field(description="Response time in milliseconds")


app = FastAPI(
    title="Dispatch Local Router",
    description="Local router service for testing multi-agent workflows",
    version="1.0.0",
)

# Get the directory where this file is located
current_dir = os.path.dirname(__file__)
static_dir = os.path.join(current_dir, "static")

# Mount static files if the directory exists
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Create API router for versioned endpoints
api_router = APIRouter()


@app.get("/")
async def serve_ui():
    """Serve the main UI."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"message": "UI not available - index.html not found"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "dispatch-local-router"}


@app.post("/shutdown")
async def shutdown_router():
    """Local only router shutdown endpoint.

    Stops all subscribed agents before shutting down the router to prevent
    ghost agents from continuing to run. Uses PID tracking as primary method
    with port-based lookup as fallback.
    """
    logger = get_logger()
    stopped_agents = []
    failed_agents = []

    try:
        # Get all agent URLs before clearing
        async with _agents_lock:
            agents_to_stop = list(_agents.items())

        # Stop each agent using unified stop function
        for agent_name, agent_data in agents_to_stop:
            agent_url = agent_data.get("url", "")

            # Extract port for fallback (may be None if URL is missing)
            port = None
            if agent_url:
                try:
                    port = int(agent_url.split(":")[-1])
                except (ValueError, IndexError):
                    pass

            # Use unified stop function (PID tracking first, then port fallback)
            success, message = _stop_agent_by_name_or_port(agent_name, port)
            if success:
                stopped_agents.append(agent_name)
                logger.info(f"Stopped agent {agent_name}: {message}")
            else:
                failed_agents.append({"agent": agent_name, "reason": message})
                logger.warning(f"Failed to stop agent {agent_name}: {message}")

        # Clear in-memory storage
        async with _agents_lock:
            _agents.clear()
        async with _subscriptions_lock:
            _subscriptions_by_topic.clear()

        logger.info(f"Router shutdown: stopped {len(stopped_agents)} agent(s)")

        # Schedule the actual shutdown
        os.kill(os.getpid(), signal.SIGTERM)

        return {
            "message": "Server is shutting down.",
            "stopped_agents": stopped_agents,
            "failed_agents": failed_agents,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error shutting down server: {e}")


@app.get("/system/status", response_model=SystemStatus)
async def get_system_status():
    """Get overall system status."""
    try:
        async with _subscriptions_lock:
            # Count unique agents across all topics
            all_agent_names = set()
            for topic_agents in _subscriptions_by_topic.values():
                all_agent_names.update(topic_agents)

        return SystemStatus(
            total_agents=len(all_agent_names), registered_agents=len(all_agent_names)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {e}")


# Backend-compatible endpoints
@api_router.post("/events/publish", response_model=PublishResponse)
async def publish(body: PublishEventBody):
    """Backend-compatible publish endpoint.

    Creates invocation records for each handler subscribed to the topic,
    then executes them asynchronously. Returns invocation_ids that can be
    polled for results (same pattern as /invoke endpoint).
    """
    logger = get_logger()
    logger.debug(
        f"Received publish request: topic={body.topic}, sender_id={body.sender_id}"
    )
    logger.debug(f"Payload size: {len(str(body.payload))} characters")

    # Convert to Message format
    message = TopicMessage.create(
        topic=body.topic,
        payload=body.payload,
        sender_id=body.sender_id,
        trace_id=body.trace_id,  # Preserve trace_id from request
        parent_id=body.parent_id,  # Preserve parent_id from request
    )

    # Store the message for thread tracking
    await store_message(message)

    # Route and create invocations (returns invocation_ids)
    invocation_ids = await route_message_to_agents_with_invocations(body.topic, message)

    return PublishResponse(
        message="Event published successfully",
        event_uid=message.uid,
        invocation_ids=invocation_ids,
        handler_count=len(invocation_ids),
    )


class RegisterAgentBody(StrictBaseModel):
    """Request body for pre-registering an agent URL."""

    agent_name: str
    url: str  # Full URL including port, e.g., "127.0.0.1:50052"


@api_router.post("/agents/register")
async def register_agent(body: RegisterAgentBody):
    """Pre-register an agent's URL before it starts.

    Called by the CLI when starting 'dispatch agent dev' to tell the router
    the correct gRPC port for the agent. This URL will be used when the agent
    subscribes, instead of guessing port 50051.
    """
    logger = get_logger()

    async with _preregistered_urls_lock:
        _preregistered_urls[body.agent_name] = body.url

    logger.info(f"Pre-registered agent '{body.agent_name}' at {body.url}")

    return {"message": f"Agent '{body.agent_name}' registered", "url": body.url}


@api_router.post("/events/subscribe", response_model=SubscriptionResponse)
async def subscribe(body: SubscriptionBody, request: Request):
    """Backend-compatible subscribe endpoint.

    Agents may subscribe with:
    - Topics only (@on handlers)
    - Functions only (@fn handlers)
    - Both topics and functions

    At minimum, agent_name is required.
    """
    logger = get_logger()
    if not body.agent_name:
        raise HTTPException(status_code=400, detail="agent_name is required")

    # Check if CLI pre-registered this agent with a specific URL
    async with _preregistered_urls_lock:
        preregistered_url = _preregistered_urls.get(body.agent_name)

    if preregistered_url:
        # Use the URL that CLI registered (has correct port)
        agent_url = preregistered_url
        logger.debug(f"Using pre-registered URL for {body.agent_name}: {agent_url}")
    else:
        # Fallback: derive from request (legacy behavior, assumes port 50051)
        client_host = request.client.host if request.client else "127.0.0.1"
        agent_url = f"{client_host}:50051"
        logger.debug(f"No pre-registered URL, using default: {agent_url}")

    # Process topics (may be empty for @fn-only agents)
    topics = []
    if body.topics:
        topics = [t for t in set(body.topics) if isinstance(t, str) and t.strip()]

    added_counts: dict[str, int] = {}
    if topics:
        async with _subscriptions_lock:
            for topic in topics:
                if topic not in _subscriptions_by_topic:
                    _subscriptions_by_topic[topic] = set()
                _subscriptions_by_topic[topic].add(body.agent_name)
                added_counts[topic] = len(_subscriptions_by_topic[topic])

    # Store agent data in-memory (this is the source of truth for local dev)
    async with _agents_lock:
        _agents[body.agent_name] = {
            "name": body.agent_name,
            "url": agent_url,
            "functions": [
                f.model_dump() if hasattr(f, "model_dump") else f
                for f in (body.functions or [])
            ],
            "topics": topics,
            "status": "healthy",
            "last_seen": datetime.now(UTC).isoformat(),
        }

    # Log subscription details
    fn_count = len(body.functions) if body.functions else 0
    if topics:
        logger.info(
            f"Agent {body.agent_name} subscribed to {len(topics)} topic(s), {fn_count} function(s) at {agent_url}"
        )
    else:
        logger.info(
            f"Agent {body.agent_name} registered {fn_count} callable function(s) (no topic subscriptions) at {agent_url}"
        )

    return SubscriptionResponse(
        message="Subscribed",
        topics=topics,
        agent_name=body.agent_name,
        subscribers=added_counts,
    )


@api_router.post("/events/unsubscribe", response_model=SubscriptionResponse)
async def unsubscribe(body: SubscriptionBody):
    """Backend-compatible unsubscribe endpoint."""
    if not body.topics or not body.agent_name:
        raise HTTPException(
            status_code=400, detail="Both topics and agent_name are required"
        )

    topics = [t for t in set(body.topics) if isinstance(t, str) and t.strip()]
    remaining_counts: dict[str, int] = {}

    async with _subscriptions_lock:
        for topic in topics:
            if (
                topic in _subscriptions_by_topic
                and body.agent_name in _subscriptions_by_topic[topic]
            ):
                _subscriptions_by_topic[topic].discard(body.agent_name)
                if not _subscriptions_by_topic[topic]:
                    _subscriptions_by_topic.pop(topic)
                    remaining_counts[topic] = 0
                else:
                    remaining_counts[topic] = len(_subscriptions_by_topic[topic])
            else:
                remaining_counts[topic] = len(_subscriptions_by_topic.get(topic, set()))

    return SubscriptionResponse(
        message="Unsubscribed",
        topics=topics,
        agent_name=body.agent_name,
        subscribers=remaining_counts,
    )


async def route_message_to_agents_with_invocations(
    topic: str, message: Message
) -> list[str]:
    """Route a topic message to all subscribed agents, creating invocation records.

    This mirrors the backend's _create_invocations_and_route() pattern:
    1. Find all agents subscribed to the topic
    2. Create invocation records for each handler
    3. Execute handlers asynchronously
    4. Store results in invocations table (not as .response topic messages)

    Args:
        topic: The topic being published to
        message: The TopicMessage being published

    Returns:
        List of invocation_ids created for this publish
    """
    logger = get_logger()

    # Get subscribed agents from subscription registry
    async with _subscriptions_lock:
        subscribed_agent_names = list(_subscriptions_by_topic.get(topic, set()))

    if not subscribed_agent_names:
        logger.debug(f"No agents subscribed to topic '{topic}'")
        return []

    # Get agent URLs from in-memory storage
    async with _agents_lock:
        agents_snapshot = dict(_agents)

    invocation_ids = []
    created_at = datetime.now(UTC).isoformat()

    for agent_name in subscribed_agent_names:
        agent = agents_snapshot.get(agent_name)
        if not agent:
            logger.warning(f"Agent {agent_name} subscribed but not in agent storage")
            continue

        agent_url = agent.get("url", "")
        if not agent_url:
            logger.warning(f"Agent {agent_name} has no URL configured")
            continue

        # Create invocation record for this handler (like backend does)
        invocation_id = str(uuid.uuid4())
        invocation_ids.append(invocation_id)

        async with _invocations_lock:
            _invocations[invocation_id] = {
                "invocation_id": invocation_id,
                "status": InvocationStatus.PENDING,
                "agent_name": agent_name,
                "function_name": topic,  # For topic handlers, use topic as function_name
                "trace_id": message.trace_id,
                "payload": message.payload,
                "sender_id": message.sender_id,
                "result": None,
                "error": None,
                "created_at": created_at,
            }

        logger.debug(f"Created invocation {invocation_id} for {agent_name}:{topic}")

        # Start async task to execute the handler
        asyncio.create_task(
            _execute_topic_handler_invocation(
                invocation_id=invocation_id,
                agent_name=agent_name,
                agent_url=agent_url,
                message=message,
            )
        )

    logger.info(
        f"Published to topic '{topic}': created {len(invocation_ids)} invocation(s)"
    )
    return invocation_ids


async def _execute_topic_handler_invocation(
    invocation_id: str,
    agent_name: str,
    agent_url: str,
    message: Message,
) -> None:
    """Execute a topic handler invocation asynchronously.

    Updates the invocation record with status and result/error.
    This is the topic-handler equivalent of _execute_function_invocation.
    """
    logger = get_logger()

    # Update status to RUNNING
    async with _invocations_lock:
        if invocation_id in _invocations:
            _invocations[invocation_id]["status"] = InvocationStatus.RUNNING

    try:
        # Send via gRPC
        result = await send_message_via_grpc(agent_name, agent_url, message)

        if result and result.get("status") == "success":
            # Success - store result in invocations table
            async with _invocations_lock:
                if invocation_id in _invocations:
                    _invocations[invocation_id]["status"] = InvocationStatus.COMPLETED
                    _invocations[invocation_id]["result"] = result.get("result")
            logger.success(
                f"Topic handler invocation {invocation_id} completed successfully"
            )
        else:
            # Error from handler or gRPC
            # Handler errors: {"result": {"error": "...", ...}, "status": "error"}
            # gRPC errors: {"error": "gRPC ..."}
            if result and result.get("status") == "error":
                # Handler raised an exception - extract error from result payload
                error_payload = result.get("result", {})
                error_msg = error_payload.get("error", "Unknown handler error")
            else:
                # gRPC-level error or no response
                error_msg = (
                    result.get("error", "Unknown error") if result else "No response"
                )
            async with _invocations_lock:
                if invocation_id in _invocations:
                    _invocations[invocation_id]["status"] = InvocationStatus.ERROR
                    _invocations[invocation_id]["error"] = error_msg
            logger.error(
                f"Topic handler invocation {invocation_id} failed: {error_msg}"
            )

    except Exception as e:
        # Unexpected error
        error_msg = f"{type(e).__name__}: {e}"
        async with _invocations_lock:
            if invocation_id in _invocations:
                _invocations[invocation_id]["status"] = InvocationStatus.ERROR
                _invocations[invocation_id]["error"] = error_msg
        logger.error(
            f"Topic handler invocation {invocation_id} failed with exception: {error_msg}"
        )


async def route_message_to_agents(topic: str, message: Message) -> dict[str, Any]:
    """Route a message to all agents that handle the given topic using subscription-based routing.

    DEPRECATED: Use route_message_to_agents_with_invocations for new code.
    This function is kept for backwards compatibility with the /events/{topic} endpoint.
    """

    # Get subscribed agents from subscription registry
    async with _subscriptions_lock:
        subscribed_agent_names = list(_subscriptions_by_topic.get(topic, set()))

    if not subscribed_agent_names:
        return {
            "status": "no_agents",
            "message": f"No agents subscribed to topic '{topic}'",
            "routed_to": [],
            "responses": {},
        }

    # Send message to subscribed agents via gRPC
    tasks = []
    agent_info: list[dict[str, Any]] = []

    # Get agent URLs from in-memory storage
    async with _agents_lock:
        agents_snapshot = dict(_agents)

    for agent_name in subscribed_agent_names:
        # Look up agent URL from in-memory storage
        agent = agents_snapshot.get(agent_name)
        if agent:
            agent_url = agent.get("url", "")
            agent_info.append({"name": agent_name, "topics": [topic]})
        else:
            # Agent subscribed but not in storage (shouldn't happen normally)
            get_logger().warning(
                f"Agent {agent_name} subscribed but not in agent storage"
            )
            continue

        if agent_url:
            task = send_message_via_grpc(agent_name, agent_url, message)
            tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Collect responses
    responses: dict[str, Any] = {}
    for agent_info_item, result in zip(agent_info, results):
        agent_name = agent_info_item["name"]
        if isinstance(result, Exception):
            responses[agent_name] = {"error": str(result)}
        else:
            responses[agent_name] = result
    get_logger().debug(f"Responses: {responses}")
    return {
        "status": "routed",
        "message": f"Message routed to {len(subscribed_agent_names)} subscribed agent(s)",
        "routed_to": agent_info,
        "responses": responses,
        "trace_id": message.trace_id,  # Include trace_id for frontend tracking
    }


async def send_message_via_grpc(
    agent_name: str, grpc_target, message: Message, timeout: float = 60.0 * 60 * 24
) -> dict | None:
    """Send a message to an agent via gRPC (port 50051).

    Supports both TopicMessage (@on handlers) and FunctionMessage (@fn handlers).
    """
    logger = get_logger()
    start_time = datetime.now()

    # Build gRPC request based on message type
    if isinstance(message, TopicMessage):
        message_type = "topic"
        topic = message.topic
        function_name = ""
        log_detail = f"topic: {message.topic}"
    elif isinstance(message, FunctionMessage):
        message_type = "function"
        topic = ""
        function_name = message.function_name
        log_detail = f"function: {message.function_name}"
    else:
        logger.error(
            f"Unsupported message type in send_message_via_grpc: {type(message).__name__}"
        )
        return None

    logger.debug(f"Sending message to {agent_name} via gRPC at {grpc_target}")
    logger.debug(
        f"Message {log_detail}, sender: {message.sender_id}, uid: {message.uid}"
    )

    try:
        # Create insecure gRPC channel (local development)
        logger.debug(f"Creating gRPC client with {timeout}s timeout")
        async with grpc.aio.insecure_channel(grpc_target) as channel:
            stub = service_pb2_grpc.AgentServiceStub(channel)

            # Convert Message to protobuf InvokeRequest
            payload = message_pb2.Payload(
                metadata={},
                data=json.dumps(message.payload).encode("utf-8"),
            )

            grpc_request = request_response_pb2.InvokeRequest(
                message_type=message_type,
                topic=topic,
                function_name=function_name,
                payload=payload,
                trace_id=message.trace_id,
                ts=message.ts,
                uid=message.uid,
            )

            # Make gRPC call
            logger.debug("Invoking agent via gRPC")
            grpc_response = await stub.Invoke(grpc_request, timeout=timeout)

            # Decode response payload
            # SDK returns either SuccessPayload {"result": <value>} or ErrorPayload {"error": <msg>, ...}
            result_payload = json.loads(grpc_response.result.data.decode("utf-8"))

            elapsed = (datetime.now() - start_time).total_seconds()
            logger.debug(f"Response received from {agent_name} in {elapsed:.2f}s")

            # Check if handler returned an error (SDK sets is_error=True for ErrorPayload)
            if grpc_response.is_error:
                error_msg = result_payload.get("error", "Unknown handler error")
                logger.error(f"Handler error from {agent_name}: {error_msg}")
                # Return error in result field to match expected structure
                # ErrorPayload contains: error, error_type, trace, details
                return {"result": result_payload, "status": "error"}

            logger.success(f"Successfully processed gRPC response from {agent_name}")

            # Return the handler's result directly (unwrap from SuccessPayload) with status
            return {"result": result_payload.get("result"), "status": "success"}

    except grpc.RpcError as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        status_code = e.code()
        details = e.details()
        logger.error(
            f"gRPC error {status_code} from {agent_name} after {elapsed:.2f}s: {details}"
        )
        return {"error": f"gRPC {status_code}: {details}"}

    except Exception as e:
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.error(
            f"Unexpected error sending to {agent_name} after {elapsed:.2f}s: {type(e).__name__}: {e}"
        )
        return {"error": str(e)}


@api_router.post("/events/{topic}")
async def send_event(topic: str, request: EventRequest):
    """Send an event to all agents that handle the given topic."""

    # Create message
    message = TopicMessage(
        topic=topic,
        payload=request.payload,
        uid=str(uuid.uuid4()),
        trace_id=str(uuid.uuid4()),
        sender_id=request.sender_id or "unknown",
        ts=datetime.now(UTC).isoformat(),
        parent_id=None,  # CLI router events are typically root events
    )

    # Store the message for thread tracking
    await store_message(message)

    try:
        # Route the message
        result = await route_message_to_agents(topic, message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to route message: {e}")


# Backend-compatible agent management endpoints
@api_router.get("/agents/list")
async def list_agents(limit: int | None = Query(default=None, ge=1, le=1000)):
    """List agents from in-memory subscription data.

    Only shows agents that have actively subscribed. If an agent isn't running
    and sending subscription requests, it won't appear in this list.
    """
    try:
        async with _agents_lock:
            result = list(_agents.values())

        # Apply limit if specified
        if limit is not None:
            result = result[:limit]

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {e}")


@api_router.post("/agents/{agent_name}/stop")
async def stop_agent(agent_name: str):
    """Stop a running agent by killing its process.

    Uses PID tracking as primary method for stopping agents (more reliable),
    with port-based lookup as fallback. Also removes the agent from in-memory
    storage and topic subscriptions.

    This is useful for stopping "ghost" agents from previous runs that are
    still sending subscription requests.
    """
    logger = get_logger()

    # Look up agent to get its URL (which contains the port for fallback)
    async with _agents_lock:
        agent = _agents.get(agent_name)

    # Extract port for fallback (may be None if agent not found or URL missing)
    port = None
    if agent:
        agent_url = agent.get("url", "")
        if agent_url:
            try:
                port = int(agent_url.split(":")[-1])
            except (ValueError, IndexError):
                pass

    # Use unified stop function (PID tracking first, then port fallback)
    success, message = _stop_agent_by_name_or_port(agent_name, port)
    logger.info(f"Stop agent {agent_name}: {message}")

    # Remove agent from in-memory storage regardless of kill result
    async with _agents_lock:
        _agents.pop(agent_name, None)

    # Remove agent from topic subscriptions
    async with _subscriptions_lock:
        for topic_agents in _subscriptions_by_topic.values():
            topic_agents.discard(agent_name)

    if success:
        return {"message": f"Agent '{agent_name}' stopped", "detail": message}
    else:
        # Agent removed from registry but process may still be running
        return {
            "message": f"Agent '{agent_name}' removed from registry",
            "detail": message,
            "warning": "Process may still be running (neither PID tracking nor port lookup succeeded)",
        }


@api_router.get("/events/recent")
async def get_recent_events(
    topic: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
):
    """Get recent events from in-memory storage."""
    async with _message_storage_lock:
        messages = list(_all_recent_messages)

        # Filter by topic if specified
        if topic:
            messages = [msg for msg in messages if msg["topic"] == topic]

        # Apply limit
        messages = messages[-limit:]  # Get most recent messages

        return {"events": messages}


@api_router.get("/events/thread/{trace_id}")
async def get_thread_messages(trace_id: str):
    """Get all messages in a conversation thread by trace_id."""
    async with _message_storage_lock:
        if trace_id in _messages_by_trace_id:
            messages = list(_messages_by_trace_id[trace_id])
            return {"trace_id": trace_id, "messages": messages}
        return {"trace_id": trace_id, "messages": []}


def _build_event_tree(events: list[dict]) -> list[dict]:
    """Build a tree structure from flat list of events using parent/child relationships.

    This matches the production backend's build_event_tree function.
    """
    if not events:
        return []

    # Create lookup maps
    events_by_uid = {event["uid"]: event for event in events if event.get("uid")}
    children_by_parent: dict[str, list[dict]] = {}

    # Initialize children arrays and group by parent_id
    for event in events:
        event["children"] = []
        parent_id = event.get("parent_id")
        if parent_id:
            if parent_id not in children_by_parent:
                children_by_parent[parent_id] = []
            children_by_parent[parent_id].append(event)

    # Attach children to their parents
    for parent_id, children in children_by_parent.items():
        if parent_id in events_by_uid:
            events_by_uid[parent_id]["children"] = children

    # Return only root events (no parent_id)
    return [event for event in events if not event.get("parent_id")]


def _calculate_llm_summary(events: list[dict]) -> dict:
    """Calculate summary statistics for LLM calls in a trace."""
    total_llm_calls = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost_usd = 0.0
    models_used: set[str] = set()

    for event in events:
        if event.get("message_type") == "llm_call":
            total_llm_calls += 1
            total_input_tokens += event.get("input_tokens", 0)
            total_output_tokens += event.get("output_tokens", 0)
            total_cost_usd += event.get("cost_usd", 0.0)
            model = event.get("model")
            if model:
                models_used.add(model)

    return {
        "total_llm_calls": total_llm_calls,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "total_cost_usd": round(total_cost_usd, 6),
        "models_used": sorted(models_used),
    }


@api_router.get("/events/trace/{trace_id}")
async def get_trace(trace_id: str):
    """Get trace with events formatted as a tree structure (production-compatible).

    This endpoint reconstructs the trace by:
    1. Getting all events (messages) for the trace_id
    2. Finding invocations that match the trace_id
    3. Enriching events with invocation data (status, result, etc.)
    4. Converting LLM calls to events and merging into the tree
    5. Building a tree structure with parent/child relationships
    6. Calculating LLM summary statistics

    Response format matches the production backend /events/trace/{trace_id} endpoint.
    """
    # Get events from message storage
    async with _message_storage_lock:
        if trace_id in _messages_by_trace_id:
            events = [dict(msg) for msg in _messages_by_trace_id[trace_id]]
        else:
            events = []

    # Get invocations for this trace_id
    async with _invocations_lock:
        trace_invocations = [
            inv for inv in _invocations.values() if inv.get("trace_id") == trace_id
        ]

    # Get LLM calls for this trace_id
    async with _llm_calls_lock:
        trace_llm_calls = list(_llm_calls_by_trace_id.get(trace_id, []))

    # Build invocation lookups
    invocation_by_id = {inv["invocation_id"]: inv for inv in trace_invocations}

    # Enrich events with invocation data and normalize to production format
    enriched_events = []
    for event in events:
        enriched = dict(event)

        # Normalize field names to production format
        # type -> message_type
        if "type" in enriched:
            enriched["message_type"] = enriched.pop("type")

        # ts -> timestamp (keep both for compatibility)
        if "ts" in enriched and "timestamp" not in enriched:
            enriched["timestamp"] = enriched["ts"]

        event_uid = event.get("uid")

        # Check if this event has a matching invocation by uid
        if event_uid and event_uid in invocation_by_id:
            inv = invocation_by_id[event_uid]
            enriched["invocation_id"] = inv["invocation_id"]
            enriched["invocation_status"] = inv["status"]
            enriched["target_agent"] = inv["agent_name"]
            enriched["sender_agent"] = event.get("sender_id", "unknown")
            enriched["invocation_created_at"] = inv.get("created_at")
            enriched["invocation_updated_at"] = inv.get("updated_at")

            # Calculate effective_timestamp for sorting
            if inv["status"] in (InvocationStatus.COMPLETED, InvocationStatus.ERROR):
                enriched["effective_timestamp"] = inv.get("updated_at") or inv.get(
                    "created_at"
                )
            else:
                enriched["effective_timestamp"] = inv.get("created_at")

            # Include result/error if completed
            if inv["status"] == InvocationStatus.COMPLETED and inv.get("result"):
                enriched["invocation_result"] = inv["result"]
            if inv["status"] == InvocationStatus.ERROR and inv.get("error"):
                enriched["invocation_error"] = inv["error"]
        else:
            # For non-invocation events, use timestamp as effective_timestamp
            enriched["effective_timestamp"] = enriched.get("timestamp")

        enriched_events.append(enriched)

    # Add invocations as child events for topic publishes
    existing_uids = {e.get("uid") for e in events}
    for inv in trace_invocations:
        if inv["invocation_id"] not in existing_uids:
            # Calculate effective_timestamp
            if inv["status"] in (InvocationStatus.COMPLETED, InvocationStatus.ERROR):
                effective_ts = inv.get("updated_at") or inv.get("created_at")
            else:
                effective_ts = inv.get("created_at")

            # Create a synthetic event from the invocation
            synthetic_event = {
                "uid": inv["invocation_id"],
                "message_type": "function",
                "function_name": inv["function_name"],
                "payload": inv.get("payload", {}),
                "trace_id": trace_id,
                "parent_id": inv.get("parent_id"),  # Link to parent event
                "sender_id": inv.get("sender_id", "local-router"),
                "timestamp": inv["created_at"],
                "ts": inv["created_at"],
                "effective_timestamp": effective_ts,
                "invocation_id": inv["invocation_id"],
                "invocation_status": inv["status"],
                "invocation_created_at": inv.get("created_at"),
                "invocation_updated_at": inv.get("updated_at"),
                "target_agent": inv["agent_name"],
                "sender_agent": inv.get("sender_id", "local-router"),
            }
            if inv["status"] == InvocationStatus.COMPLETED and inv.get("result"):
                synthetic_event["invocation_result"] = inv["result"]
            if inv["status"] == InvocationStatus.ERROR and inv.get("error"):
                synthetic_event["invocation_error"] = inv["error"]

            enriched_events.append(synthetic_event)

    # Convert LLM calls to event format and merge into events list
    for llm_call in trace_llm_calls:
        llm_event = {
            "uid": llm_call.get("llm_call_id"),
            "message_type": "llm_call",
            "trace_id": trace_id,
            "parent_id": llm_call.get("invocation_id"),  # Links to parent invocation
            "timestamp": llm_call.get("ts"),
            "ts": llm_call.get("ts"),
            "effective_timestamp": llm_call.get("ts"),
            # LLM-specific fields
            "model": llm_call.get("model"),
            "provider": llm_call.get("provider"),
            "request_messages": llm_call.get("input_messages"),
            "response_content": llm_call.get("response_content"),
            "response_tool_calls": llm_call.get("tool_calls"),
            "finish_reason": llm_call.get("finish_reason"),
            "input_tokens": llm_call.get("input_tokens", 0),
            "output_tokens": llm_call.get("output_tokens", 0),
            "cost_usd": llm_call.get("cost_usd", 0.0),
            "latency_ms": llm_call.get("latency_ms", 0),
            "subprocess_id": llm_call.get("subprocess_id"),
        }
        enriched_events.append(llm_event)

    # Sort events by effective_timestamp (oldest first)
    enriched_events.sort(key=lambda e: e.get("effective_timestamp") or "")

    # Build the tree structure
    tree = _build_event_tree(enriched_events)

    # Calculate LLM summary statistics
    llm_summary = _calculate_llm_summary(enriched_events)

    response = {
        "trace_id": trace_id,
        "total_events": len(enriched_events),
        "events": tree,
    }

    # Only include llm_summary if there were LLM calls
    if llm_summary["total_llm_calls"] > 0:
        response["llm_summary"] = llm_summary

    return response


# Schema endpoints - using in-memory agent data
@api_router.get("/schemas/list")
async def list_schemas():
    """List all agents with their functions.

    Returns agent data from in-memory storage including functions with their schemas.
    Only shows agents that have actively subscribed.
    """
    try:
        async with _agents_lock:
            agents = [
                {
                    "name": agent["name"],
                    "status": agent.get("status", "unknown"),
                    "url": agent.get("url", ""),
                    "functions": agent.get("functions", []),
                }
                for agent in _agents.values()
            ]

        return {"agents": agents}
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list schemas: {exc}",
        )


@api_router.get("/schemas/topics")
async def get_topic_schemas():
    """Get all schemas organized by topic.

    Returns topics with their subscribing agents and function schemas.
    Only shows data from agents that have actively subscribed.
    """
    try:
        async with _agents_lock:
            agents_copy = list(_agents.values())

        # Build topic -> agents mapping
        topic_schemas: dict[str, list] = {}
        for agent in agents_copy:
            for func in agent.get("functions", []):
                # Extract topics from triggers
                for trigger in func.get("triggers", []):
                    if trigger.get("type") == "topic" and trigger.get("topic"):
                        topic = trigger["topic"]
                        if topic not in topic_schemas:
                            topic_schemas[topic] = []

                        topic_schemas[topic].append(
                            {
                                "agent_name": agent["name"],
                                "schema": {
                                    "handler_name": func.get("name"),
                                    "handler_doc": func.get("description"),
                                    "input_schema": func.get("input_schema"),
                                    "output_schema": func.get("output_schema"),
                                },
                            }
                        )

        return {"topics": topic_schemas}
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get topic schemas: {exc}",
        )


# =============================================================================
# Invoke endpoints - Direct function invocation (@fn handlers)
# =============================================================================


@api_router.post("/invoke", response_model=InvokeFunctionResponse)
async def invoke_function(body: InvokeFunctionRequest):
    """Invoke a function on an agent directly.

    This endpoint supports @fn decorated functions. It creates an invocation record,
    executes the function via gRPC, and returns immediately with an invocation_id.
    Poll GET /invoke/{invocation_id} for results.
    """
    logger = get_logger()
    logger.info(
        f"Received invoke request: agent={body.agent_name}, function={body.function_name}"
    )

    # Look up agent from in-memory storage
    async with _agents_lock:
        agent = _agents.get(body.agent_name)

    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{body.agent_name}' not found (agent may not be running)",
        )

    agent_url = agent.get("url", "")
    if not agent_url:
        raise HTTPException(
            status_code=400,
            detail=f"Agent '{body.agent_name}' has no gRPC URL configured",
        )

    # Generate invocation_id and trace_id
    invocation_id = str(uuid.uuid4())
    trace_id = body.trace_id or str(uuid.uuid4())
    created_at = datetime.now(UTC).isoformat()

    # Create invocation record with PENDING status
    async with _invocations_lock:
        _invocations[invocation_id] = {
            "invocation_id": invocation_id,
            "status": InvocationStatus.PENDING,
            "agent_name": body.agent_name,
            "function_name": body.function_name,
            "trace_id": trace_id,
            "payload": body.payload,
            "result": None,
            "error": None,
            "created_at": created_at,
        }

    logger.info(f"Created invocation {invocation_id} for {body.function_name}")

    # Calculate timeout: use provided value, default to 1 hour
    timeout_seconds = body.timeout_seconds or 3600

    # Start async task to execute the function
    asyncio.create_task(
        _execute_function_invocation(
            invocation_id=invocation_id,
            agent_name=body.agent_name,
            agent_url=agent_url,
            function_name=body.function_name,
            payload=body.payload,
            trace_id=trace_id,
            parent_id=body.parent_id,
            timeout_seconds=timeout_seconds,
        )
    )

    return InvokeFunctionResponse(
        invocation_id=invocation_id,
        trace_id=trace_id,
        status=InvocationStatus.PENDING,
    )


@api_router.get("/invoke/{invocation_id}", response_model=InvocationStatusResponse)
async def get_invocation_status(invocation_id: str):
    """Get the status and result of a function invocation.

    Poll this endpoint until status is 'completed' or 'error'.
    """
    async with _invocations_lock:
        invocation = _invocations.get(invocation_id)

    if not invocation:
        raise HTTPException(
            status_code=404,
            detail=f"Invocation '{invocation_id}' not found",
        )

    return InvocationStatusResponse(
        invocation_id=invocation["invocation_id"],
        status=invocation["status"],
        agent_name=invocation["agent_name"],
        function_name=invocation["function_name"],
        trace_id=invocation["trace_id"],
        result=invocation["result"],
        error=invocation["error"],
        created_at=invocation["created_at"],
    )


async def _execute_function_invocation(
    invocation_id: str,
    agent_name: str,
    agent_url: str,
    function_name: str,
    payload: dict[str, Any],
    trace_id: str,
    parent_id: str | None,
    timeout_seconds: int = 3600,
) -> None:
    """Execute a function invocation asynchronously.

    Updates the invocation record with status and result/error.
    """
    logger = get_logger()

    # Update status to RUNNING
    async with _invocations_lock:
        if invocation_id in _invocations:
            _invocations[invocation_id]["status"] = InvocationStatus.RUNNING

    try:
        # Create FunctionMessage for the invocation
        message = FunctionMessage.create(
            function_name=function_name,
            payload=payload,
            sender_id="local-router",  # Local router is the sender
            trace_id=trace_id,
            parent_id=parent_id,
            _uid=invocation_id,  # Use invocation_id as message uid for correlation
        )

        # Store the message for trace tracking
        await store_message(message)

        # Send via gRPC with the specified timeout
        result = await send_message_via_grpc(
            agent_name, agent_url, message, timeout=float(timeout_seconds)
        )

        if result and result.get("status") == "success":
            # Success
            async with _invocations_lock:
                if invocation_id in _invocations:
                    _invocations[invocation_id]["status"] = InvocationStatus.COMPLETED
                    _invocations[invocation_id]["result"] = result.get("result")
            logger.success(f"Invocation {invocation_id} completed successfully")
        else:
            # Error from handler or gRPC
            # Handler errors: {"result": {"error": "...", ...}, "status": "error"}
            # gRPC errors: {"error": "gRPC ..."}
            if result and result.get("status") == "error":
                # Handler raised an exception - extract error from result payload
                error_payload = result.get("result", {})
                error_msg = error_payload.get("error", "Unknown handler error")
            else:
                # gRPC-level error or no response
                error_msg = (
                    result.get("error", "Unknown error") if result else "No response"
                )
            async with _invocations_lock:
                if invocation_id in _invocations:
                    _invocations[invocation_id]["status"] = InvocationStatus.ERROR
                    _invocations[invocation_id]["error"] = error_msg
            logger.error(f"Invocation {invocation_id} failed: {error_msg}")

    except Exception as e:
        # Unexpected error
        error_msg = f"{type(e).__name__}: {e}"
        async with _invocations_lock:
            if invocation_id in _invocations:
                _invocations[invocation_id]["status"] = InvocationStatus.ERROR
                _invocations[invocation_id]["error"] = error_msg
        logger.error(f"Invocation {invocation_id} failed with exception: {error_msg}")


# UI-specific endpoints
# =============================================================================
# LLM Config Endpoints (Local Development UI)
# =============================================================================


@app.get("/api/unstable/llm-config/local")
async def get_llm_config():
    """Get local LLM provider configuration status.

    Returns which providers are configured and where each key is stored
    (keychain, environment variable, raw secrets.yaml, etc.).
    """
    from dispatch_cli.router.local_llm import (
        PROVIDER_ENV_VARS,
        SUPPORTED_PROVIDERS,
        get_configured_providers,
    )
    from dispatch_cli.secrets import get_secret_sources

    configured = get_configured_providers()
    env_vars = [
        PROVIDER_ENV_VARS[p] for p in SUPPORTED_PROVIDERS if p in PROVIDER_ENV_VARS
    ]
    sources = get_secret_sources(required_secrets=env_vars)
    source_map = {s["name"]: s for s in sources}

    providers = []
    for provider in sorted(SUPPORTED_PROVIDERS):
        env_var = PROVIDER_ENV_VARS.get(provider, "")
        source_info = source_map.get(env_var, {})
        providers.append(
            {
                "provider": provider,
                "env_var": env_var,
                "configured": configured.get(provider, False),
                "storage_type": source_info.get("storage_type"),
            }
        )

    return {"providers": providers}


class LLMConfigAddBody(StrictBaseModel):
    """Request body for adding/updating an LLM API key."""

    provider: str
    api_key: str


@app.post("/api/unstable/llm-config/local")
async def add_llm_config(body: LLMConfigAddBody):
    """Add or update a local LLM provider API key.

    Stores the key in macOS Keychain via secrets.yaml and sets it in
    os.environ so it takes effect immediately without a router restart.
    """
    from dispatch_cli.router.local_llm import PROVIDER_ENV_VARS, SUPPORTED_PROVIDERS
    from dispatch_cli.secrets import add_secret

    if body.provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider '{body.provider}'. Supported: {sorted(SUPPORTED_PROVIDERS)}",
        )

    env_var = PROVIDER_ENV_VARS.get(body.provider)
    if not env_var:
        raise HTTPException(
            status_code=400, detail=f"No env var mapping for provider '{body.provider}'"
        )

    if not body.api_key.strip():
        raise HTTPException(status_code=400, detail="API key cannot be empty")

    success = add_secret(env_var, body.api_key.strip(), use_keychain=True)
    if not success:
        raise HTTPException(
            status_code=500, detail=f"Failed to store API key for {body.provider}"
        )

    # Set in environment immediately so the LLM proxy picks it up
    os.environ[env_var] = body.api_key.strip()

    return {
        "success": True,
        "message": f"API key for {body.provider} saved and activated",
    }


@app.delete("/api/unstable/llm-config/local/{provider}")
async def remove_llm_config(provider: str):
    """Remove a local LLM provider API key.

    Removes from Keychain/secrets.yaml and os.environ.
    """
    from dispatch_cli.router.local_llm import PROVIDER_ENV_VARS, SUPPORTED_PROVIDERS
    from dispatch_cli.secrets import remove_secret

    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown provider '{provider}'. Supported: {sorted(SUPPORTED_PROVIDERS)}",
        )

    env_var = PROVIDER_ENV_VARS.get(provider)
    if not env_var:
        raise HTTPException(
            status_code=400, detail=f"No env var mapping for provider '{provider}'"
        )

    removed = remove_secret(env_var)

    # Remove from environment
    os.environ.pop(env_var, None)

    if removed:
        return {"success": True, "message": f"API key for {provider} removed"}
    else:
        return {
            "success": True,
            "message": f"No API key found for {provider} (already removed)",
        }


@app.get("/ui/topics")
async def get_available_topics():
    """Get list of available topics from subscriptions (UI helper)."""
    try:
        async with _subscriptions_lock:
            topics = list(_subscriptions_by_topic.keys())

        topic_info = []
        for topic in topics:
            subscribed_agents = list(_subscriptions_by_topic[topic])
            topic_info.append(
                {
                    "topic": topic,
                    "subscriber_count": len(subscribed_agents),
                    "subscribers": subscribed_agents,
                }
            )

        return {"topics": topic_info, "total_topics": len(topics)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get topics: {e}")


@app.get("/ui/subscriptions")
async def get_subscriptions():
    """Get current subscription state (UI helper)."""
    try:
        async with _subscriptions_lock:
            return dict(_subscriptions_by_topic)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subscriptions: {e}")


# Memory endpoints (in-memory implementation for local development)
@api_router.put("/memory/long-term")
async def add_long_term_memory(
    memory_request: KVStoreRequest, namespace: str = DEV_NAMESPACE
):
    """Add or update long-term memory."""
    async with _memory_lock:
        key = (memory_request.agent_name, namespace, memory_request.key)
        _long_term_memory[key] = {
            "value": memory_request.value,
            "created_at": datetime.now().isoformat(),
        }
    return {"message": "Long term memory added successfully"}


@api_router.get("/memory/long-term")
async def get_long_term_memory(
    memory_request: KVStoreRequest, namespace: str = DEV_NAMESPACE
):
    """Get long-term memory value."""
    async with _memory_lock:
        memory_key = (memory_request.agent_name, namespace, memory_request.key)
        memory_data = _long_term_memory.get(memory_key, {})
        return {"value": memory_data.get("value")}


@api_router.get("/memory/long-term/agent/{agent_name}")
async def get_long_term_memories_for_agent(
    agent_name: str, namespace: str = DEV_NAMESPACE
):
    """Get all long-term memories for an agent."""
    async with _memory_lock:
        memories = []
        for (
            stored_agent_name,
            stored_namespace,
            mem_key,
        ), data in _long_term_memory.items():
            if stored_agent_name == agent_name and stored_namespace == namespace:
                memories.append(
                    {
                        "mem_key": mem_key,
                        "mem_value": data.get("value", ""),
                        "last_updated": data.get("created_at", ""),
                    }
                )
    return {"agent_name": agent_name, "memories": memories}


@api_router.delete("/memory/long-term")
async def delete_long_term_memory(
    memory_request: KVStoreRequest, namespace: str = DEV_NAMESPACE
):
    """Delete long-term memory."""
    async with _memory_lock:
        memory_key = (memory_request.agent_name, namespace, memory_request.key)
        _long_term_memory.pop(memory_key, None)
    return {"message": "Long term memory deleted successfully"}


@api_router.put("/memory/short-term")
async def add_update_short_term_memory(
    memory_request: SessionStoreRequest, namespace: str = DEV_NAMESPACE
):
    """Add or update short-term memory."""
    async with _memory_lock:
        key = (memory_request.agent_name, namespace, memory_request.session_id)
        _short_term_memory[key] = {
            "session_data": memory_request.session_data,
            "created_at": datetime.now().isoformat(),
        }
    return {"message": "Short term memory added successfully"}


@api_router.get("/memory/short-term")
async def get_short_term_memory(
    memory_request: SessionStoreRequest, namespace: str = DEV_NAMESPACE
):
    """Get short-term memory."""
    async with _memory_lock:
        memory_key = (memory_request.agent_name, namespace, memory_request.session_id)
        memory_data = _short_term_memory.get(memory_key, {})
        return {"session_data": memory_data.get("session_data", {})}


@api_router.delete("/memory/short-term")
async def delete_short_term_memory(
    memory_request: SessionStoreRequest, namespace: str = DEV_NAMESPACE
):
    """Delete short-term memory."""
    async with _memory_lock:
        memory_key = (memory_request.agent_name, namespace, memory_request.session_id)
        _short_term_memory.pop(memory_key, None)
    return {"message": "Short term memory deleted successfully"}


# =============================================================================
# LLM Inference Endpoint (Local Development)
# =============================================================================


@api_router.post("/llm/inference", response_model=LLMInferenceResponse)
async def local_llm_inference(request_data: LLMInferenceRequest):
    """Local LLM inference using environment API keys.

    In local dev mode, calls providers (OpenAI, Anthropic, Google) directly
    using API keys from environment variables (e.g., OPENAI_API_KEY).

    No SecretsManager required - just direct HTTP calls.

    Set API keys in your .env file:
    - OPENAI_API_KEY for GPT models
    - ANTHROPIC_API_KEY for Claude models
    - GOOGLE_API_KEY for Gemini models
    """
    import time

    from dispatch_cli.router.llm_pricing import calculate_cost
    from dispatch_cli.router.local_llm import (
        LocalLLMError,
        call_provider,
        get_api_key,
    )

    logger = get_logger()
    start_time = time.time()

    model = request_data.model
    provider = request_data.provider

    # Resolve defaults when model/provider not specified
    if not provider or not model:
        from dispatch_cli.router.local_llm import PROVIDER_ENV_VARS

        # Find the first configured provider
        if not provider:
            for prov, env_var in PROVIDER_ENV_VARS.items():
                if os.environ.get(env_var):
                    provider = prov
                    break
            if not provider:
                raise HTTPException(
                    status_code=400,
                    detail="No LLM provider specified and no provider API keys found in environment. "
                    "Run `dispatch llm local <provider>` to configure one.",
                )

        # Default models per provider
        if not model:
            default_models = {
                "openai": "gpt-4o",
                "anthropic": "claude-sonnet-4-5-20250929",
                "google": "gemini-2.0-flash",
            }
            model = default_models.get(provider, "gpt-4o")

    # Get API key from environment
    try:
        api_key = get_api_key(provider)
    except LocalLLMError as e:
        raise HTTPException(status_code=400, detail=e.message)

    logger.info(f"LLM inference: model={model}, provider={provider}")

    # 3. Convert messages to dicts
    messages = [m.model_dump(exclude_none=True) for m in request_data.messages]

    # 4. Call provider
    try:
        response = await call_provider(
            provider=provider,
            model=model,
            messages=messages,
            api_key=api_key,
            temperature=request_data.temperature,
            max_tokens=request_data.max_tokens,
            tools=request_data.tools,
            response_format=request_data.response_format,
        )
    except LocalLLMError as e:
        raise HTTPException(status_code=e.status_code or 500, detail=e.message)

    # 5. Calculate cost and latency
    latency_ms = int((time.time() - start_time) * 1000)
    cost_usd = calculate_cost(
        model, response["input_tokens"], response["output_tokens"]
    )

    # 6. Generate LLM call ID
    llm_call_id = str(uuid.uuid4())

    # 7. Store LLM call for trace visualization
    llm_call_data = {
        "type": "llm_call",
        "llm_call_id": llm_call_id,
        "trace_id": request_data.trace_id,
        "invocation_id": request_data.invocation_id,
        "model": model,
        "provider": provider,
        "input_tokens": response["input_tokens"],
        "output_tokens": response["output_tokens"],
        "cost_usd": cost_usd,
        "latency_ms": latency_ms,
        "finish_reason": response["finish_reason"],
        "input_messages": messages,
        "response_content": response.get("content"),
        "tool_calls": response.get("tool_calls"),
        "ts": datetime.now(UTC).isoformat(),
    }
    await store_llm_call(llm_call_data)

    logger.success(
        f"LLM call complete: {response['input_tokens']} in / {response['output_tokens']} out, "
        f"${cost_usd:.6f}, {latency_ms}ms"
    )

    # 8. Pass through tool calls (already LLMToolCall objects from provider)
    tool_calls = response.get("tool_calls")

    # 9. Return standardized response
    return LLMInferenceResponse(
        llm_call_id=llm_call_id,
        content=response.get("content"),
        tool_calls=tool_calls,
        finish_reason=response["finish_reason"],
        model=model,
        provider=provider,
        variant_name=None,
        input_tokens=response["input_tokens"],
        output_tokens=response["output_tokens"],
        cost_usd=cost_usd,
        latency_ms=latency_ms,
    )


# =============================================================================
# LLM Proxy & Passthrough Endpoints (Sidecar → Local Router)
# =============================================================================

# Provider base URLs and auth configuration for raw proxy forwarding.
# These mirror the sidecar's _PROVIDER_CONFIG but only contain what we need
# for the local router (no fallback key envs, etc.).
_PROXY_PROVIDER_CONFIG: dict[str, dict[str, Any]] = {
    "openai": {
        "base_url": "https://api.openai.com",
        "chat_endpoint": "/v1/chat/completions",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
        "extra_headers": {},
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com",
        "chat_endpoint": "/v1/messages",
        "auth_header": "x-api-key",
        "auth_prefix": "",
        "extra_headers": {"anthropic-version": "2023-06-01"},
    },
}


class _ProviderResponseInfo:
    """Parsed fields from a raw provider response, for trace logging."""

    __slots__ = (
        "model",
        "input_tokens",
        "output_tokens",
        "response_content",
        "finish_reason",
        "tool_calls",
    )

    def __init__(self) -> None:
        self.model: str = "unknown"
        self.input_tokens: int = 0
        self.output_tokens: int = 0
        self.response_content: str | None = None
        self.finish_reason: str = "stop"
        self.tool_calls: list[dict[str, Any]] | None = None


def _extract_provider_response_info(
    provider_format: str, resp_data: dict[str, Any]
) -> _ProviderResponseInfo:
    """Best-effort extraction of fields from a raw provider response.

    Extracts model, tokens, response content, finish reason, and tool calls
    for trace visualization. On any parse failure, returns sensible defaults —
    this must never fail the user's request.
    """
    info = _ProviderResponseInfo()

    try:
        if provider_format == "openai" and "output" in resp_data:
            # OpenAI Responses API format
            info.model = resp_data.get("model", "unknown")
            usage = resp_data.get("usage", {})
            info.input_tokens = usage.get("input_tokens", 0)
            info.output_tokens = usage.get("output_tokens", 0)
            # Extract text from output items
            for item in resp_data.get("output", []):
                if isinstance(item, dict) and item.get("type") == "message":
                    for content in item.get("content", []):
                        if (
                            isinstance(content, dict)
                            and content.get("type") == "output_text"
                        ):
                            info.response_content = content.get("text")
                            break
            info.finish_reason = (
                "stop"
                if resp_data.get("status") == "completed"
                else resp_data.get("status", "stop")
            )
        elif provider_format == "openai":
            # OpenAI Chat Completions format
            info.model = resp_data.get("model", "unknown")
            usage = resp_data.get("usage", {})
            info.input_tokens = usage.get("prompt_tokens", 0)
            info.output_tokens = usage.get("completion_tokens", 0)
            choices = resp_data.get("choices", [])
            if choices:
                choice = choices[0]
                msg = choice.get("message", {})
                info.response_content = msg.get("content")
                info.finish_reason = choice.get("finish_reason", "stop")
                if msg.get("tool_calls"):
                    info.tool_calls = msg["tool_calls"]
        elif provider_format == "anthropic":
            info.model = resp_data.get("model", "unknown")
            usage = resp_data.get("usage", {})
            info.input_tokens = usage.get("input_tokens", 0)
            info.output_tokens = usage.get("output_tokens", 0)
            # Extract text content from Anthropic's content blocks
            for block in resp_data.get("content", []):
                if block.get("type") == "text":
                    info.response_content = block.get("text")
                    break
            # Map Anthropic stop_reason to OpenAI-style finish_reason
            stop_reason = resp_data.get("stop_reason", "end_turn")
            finish_map = {
                "end_turn": "stop",
                "max_tokens": "length",
                "tool_use": "tool_calls",
            }
            info.finish_reason = finish_map.get(stop_reason, stop_reason)
            # Extract tool_use blocks as tool calls
            tool_uses = [
                b for b in resp_data.get("content", []) if b.get("type") == "tool_use"
            ]
            if tool_uses:
                info.tool_calls = tool_uses
    except Exception:
        pass

    return info


class LLMProxyRequest(StrictBaseModel):
    """Request from the sidecar proxy for chat/messages endpoints."""

    provider_format: str = Field(description="Provider: 'openai' or 'anthropic'")
    body: dict[str, Any] = Field(description="Raw SDK request body")
    endpoint: str = Field(
        description="Provider endpoint path, e.g. /v1/chat/completions or /v1/responses"
    )
    trace_id: str | None = Field(default=None)
    invocation_id: str | None = Field(default=None)
    subprocess_id: str | None = Field(default=None)
    extra_headers: dict[str, str] | None = Field(default=None)
    agent_name: str | None = Field(default=None)


class LLMPassthroughRequest(StrictBaseModel):
    """Request from the sidecar proxy for unsupported/passthrough endpoints."""

    provider_format: str = Field(description="Provider: 'openai' or 'anthropic'")
    path: str = Field(description="Provider API path, e.g. '/v1/embeddings'")
    method: str = Field(default="POST", description="HTTP method")
    body: dict[str, Any] | None = Field(default=None)
    query_params: dict[str, str] | None = Field(default=None)
    trace_id: str | None = Field(default=None)
    invocation_id: str | None = Field(default=None)
    extra_headers: dict[str, str] | None = Field(default=None)
    agent_name: str | None = Field(default=None)


@api_router.post("/llm/proxy")
async def llm_proxy(request_data: LLMProxyRequest):
    """Forward a raw SDK request to the LLM provider and return the raw response.

    This endpoint is called by the sidecar proxy (sdk/dispatch_agents/proxy/server.py)
    for chat completions (OpenAI) and messages (Anthropic) — the "known" endpoints
    where we can extract tokens for cost tracking.

    Unlike /llm/inference which normalizes responses into Dispatch format, this
    returns the raw provider JSON so the SDK (openai/anthropic Python package)
    can parse it directly.
    """
    import time

    from dispatch_cli.router.llm_pricing import calculate_cost
    from dispatch_cli.router.local_llm import LocalLLMError, get_api_key

    logger = get_logger()
    provider = request_data.provider_format

    config = _PROXY_PROVIDER_CONFIG.get(provider)
    if not config:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported provider_format: '{provider}'. Supported: openai, anthropic",
        )

    # Get API key from environment / Keychain
    try:
        api_key = get_api_key(provider)
    except LocalLLMError as e:
        raise HTTPException(status_code=400, detail=e.message)

    url = config["base_url"] + request_data.endpoint
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if request_data.extra_headers:
        headers.update(request_data.extra_headers)
    headers.update(config["extra_headers"])
    headers[config["auth_header"]] = f"{config['auth_prefix']}{api_key}"

    body = request_data.body

    # Streaming path — use httpx streaming and extract usage after stream completes
    if body.get("stream"):
        return await _llm_proxy_streaming(
            request_data=request_data,
            url=url,
            headers=headers,
            provider=provider,
        )

    start_time = time.time()

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(url, json=body, headers=headers)
    except (httpx.RequestError, OSError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Cannot reach {provider} API at {url}: {exc}",
        )

    latency_ms = int((time.time() - start_time) * 1000)

    # Best-effort: extract tokens, response content, and log for trace visualization
    if resp.status_code < 400:
        try:
            resp_data = resp.json()
            info = _extract_provider_response_info(provider, resp_data)
            cost_usd = calculate_cost(info.model, info.input_tokens, info.output_tokens)

            llm_call_data = {
                "type": "llm_call",
                "llm_call_id": str(uuid.uuid4()),
                "trace_id": request_data.trace_id,
                "invocation_id": request_data.invocation_id,
                "model": info.model,
                "provider": provider,
                "input_tokens": info.input_tokens,
                "output_tokens": info.output_tokens,
                "cost_usd": cost_usd,
                "latency_ms": latency_ms,
                "finish_reason": info.finish_reason,
                "input_messages": request_data.body.get("messages")
                or request_data.body.get("input", []),
                "response_content": info.response_content,
                "tool_calls": info.tool_calls,
                "subprocess_id": request_data.subprocess_id,
                "ts": datetime.now(UTC).isoformat(),
            }
            await store_llm_call(llm_call_data)

            logger.success(
                f"LLM proxy ({provider}): {info.input_tokens} in / {info.output_tokens} out, "
                f"${cost_usd:.6f}, {latency_ms}ms"
            )
        except Exception:
            # Never fail the user's request due to logging errors
            logger.debug("Failed to log LLM proxy call (best-effort)", exc_info=True)

    # Return raw provider response as-is
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type="application/json",
    )


async def _llm_proxy_streaming(
    *,
    request_data: "LLMProxyRequest",
    url: str,
    headers: dict,
    provider: str,
) -> Response:
    """Handle streaming LLM proxy request in local dev mode.

    Uses httpx streaming to the provider, buffers SSE events for usage
    extraction, and records the call after the stream completes.
    """
    import time as time_mod

    from fastapi.responses import StreamingResponse

    from dispatch_cli.router.llm_pricing import calculate_cost

    logger = get_logger()
    body = request_data.body

    # For OpenAI, inject stream_options to get usage in final chunk
    if provider == "openai":
        body = {**body, "stream_options": {"include_usage": True}}

    client = httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0))
    buffered_lines: list[str] = []
    start_time = time_mod.time()

    async def stream_and_record():
        try:
            async with client.stream("POST", url, json=body, headers=headers) as resp:
                if resp.status_code >= 400:
                    async for chunk in resp.aiter_bytes():
                        yield chunk
                    return

                async for line in resp.aiter_lines():
                    yield (line + "\n").encode()
                    buffered_lines.append(line)
        except (httpx.RequestError, OSError) as exc:
            logger.warning("Streaming provider request failed: %s", exc)
        finally:
            await client.aclose()
            # Extract usage from buffered SSE lines and record
            latency_ms = int((time_mod.time() - start_time) * 1000)
            try:
                model, inp, out, reason, resp_text = _extract_sse_usage(
                    provider, buffered_lines
                )
                cost_usd = calculate_cost(model, inp, out)

                llm_call_data = {
                    "type": "llm_call",
                    "llm_call_id": str(uuid.uuid4()),
                    "trace_id": request_data.trace_id,
                    "invocation_id": request_data.invocation_id,
                    "model": model,
                    "provider": provider,
                    "input_tokens": inp,
                    "output_tokens": out,
                    "cost_usd": cost_usd,
                    "latency_ms": latency_ms,
                    "finish_reason": reason,
                    "input_messages": request_data.body.get("messages", []),
                    "response_content": resp_text,
                    "tool_calls": None,
                    "subprocess_id": request_data.subprocess_id,
                    "ts": datetime.now(UTC).isoformat(),
                }
                logger.info(
                    f"[DEBUG] Storing streaming LLM call: "
                    f"trace_id={request_data.trace_id}, "
                    f"invocation_id={request_data.invocation_id}, "
                    f"model={model}, tokens={inp}/{out}, "
                    f"buffered_lines={len(buffered_lines)}"
                )
                await store_llm_call(llm_call_data)
                logger.success(
                    f"LLM proxy streaming ({provider}): {inp} in / {out} out, "
                    f"${cost_usd:.6f}, {latency_ms}ms"
                )
            except Exception:
                logger.debug("Failed to log streaming LLM call", exc_info=True)

    return StreamingResponse(
        stream_and_record(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


def _extract_sse_usage(
    provider_format: str, lines: list[str]
) -> tuple[str, int, int, str, str | None]:
    """Extract (model, input_tokens, output_tokens, finish_reason, response_text) from buffered SSE lines."""
    import json as _json

    model = "unknown"
    input_tokens = 0
    output_tokens = 0
    finish_reason = "stop"
    current_event_type = None
    text_parts: list[str] = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("event:"):
            current_event_type = stripped[6:].strip()
        elif stripped.startswith("data:"):
            data_str = stripped[5:].strip()
            if data_str == "[DONE]":
                continue
            try:
                ev = _json.loads(data_str)
            except _json.JSONDecodeError:
                continue

            if provider_format == "anthropic":
                model, input_tokens, output_tokens, finish_reason = (
                    _observe_anthropic_event(
                        ev,
                        current_event_type,
                        model,
                        input_tokens,
                        output_tokens,
                        finish_reason,
                        text_parts,
                    )
                )
            else:
                model, input_tokens, output_tokens, finish_reason = (
                    _observe_openai_event(
                        ev,
                        model,
                        input_tokens,
                        output_tokens,
                        finish_reason,
                        text_parts,
                    )
                )

    response_text = "".join(text_parts) if text_parts else None
    return model, input_tokens, output_tokens, finish_reason, response_text


def _observe_anthropic_event(
    ev: dict,
    current_event_type: str | None,
    model: str,
    input_tokens: int,
    output_tokens: int,
    finish_reason: str,
    text_parts: list[str],
) -> tuple[str, int, int, str]:
    ev_type = ev.get("type") or current_event_type
    if ev_type == "message_start":
        msg = ev.get("message", {})
        model = msg.get("model", model)
        usage = msg.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
    elif ev_type == "content_block_delta":
        delta = ev.get("delta", {})
        if delta.get("type") == "text_delta" and delta.get("text"):
            text_parts.append(delta["text"])
    elif ev_type == "message_delta":
        delta = ev.get("delta", {})
        if delta.get("stop_reason"):
            reason_map = {
                "end_turn": "stop",
                "max_tokens": "length",
                "tool_use": "tool_calls",
            }
            finish_reason = reason_map.get(delta["stop_reason"], delta["stop_reason"])
        usage = ev.get("usage", {})
        if usage.get("output_tokens"):
            output_tokens = usage["output_tokens"]
    return model, input_tokens, output_tokens, finish_reason


def _observe_openai_event(
    ev: dict,
    model: str,
    input_tokens: int,
    output_tokens: int,
    finish_reason: str,
    text_parts: list[str],
) -> tuple[str, int, int, str]:
    if ev.get("model"):
        model = ev["model"]
    usage = ev.get("usage")
    if usage:
        input_tokens = usage.get("prompt_tokens", input_tokens)
        output_tokens = usage.get("completion_tokens", output_tokens)
    choices = ev.get("choices", [])
    if choices:
        if choices[0].get("finish_reason"):
            finish_reason = choices[0]["finish_reason"]
        delta = choices[0].get("delta", {})
        if delta.get("content"):
            text_parts.append(delta["content"])
    return model, input_tokens, output_tokens, finish_reason


@api_router.post("/llm/passthrough")
async def llm_passthrough(request_data: LLMPassthroughRequest):
    """Forward an arbitrary SDK request to the LLM provider with credential injection.

    This endpoint handles "unsupported" SDK calls (embeddings, models list, audio,
    images, etc.) that don't fit the chat/messages observability parsing. The local
    router just injects the API key and forwards opaquely — no response parsing or
    cost tracking.

    Called by the sidecar proxy for any endpoint that doesn't match the known
    chat/messages routes.
    """
    from dispatch_cli.router.local_llm import LocalLLMError, get_api_key

    logger = get_logger()
    provider = request_data.provider_format

    config = _PROXY_PROVIDER_CONFIG.get(provider)
    if not config:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported provider_format: '{provider}'. Supported: openai, anthropic",
        )

    # Get API key from environment / Keychain
    try:
        api_key = get_api_key(provider)
    except LocalLLMError as e:
        raise HTTPException(status_code=400, detail=e.message)

    # Build full URL: base_url + path (e.g. https://api.openai.com/v1/embeddings)
    url = config["base_url"] + request_data.path
    if request_data.query_params:
        from urllib.parse import urlencode

        url += "?" + urlencode(request_data.query_params)

    # Build headers
    headers: dict[str, str] = {}
    if request_data.extra_headers:
        headers.update(request_data.extra_headers)
    headers.update(config["extra_headers"])
    headers[config["auth_header"]] = f"{config['auth_prefix']}{api_key}"
    if request_data.body is not None:
        headers["Content-Type"] = "application/json"

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.request(
                method=request_data.method,
                url=url,
                json=request_data.body if request_data.body is not None else None,
                headers=headers,
            )
    except (httpx.RequestError, OSError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Cannot reach {provider} API at {url}: {exc}",
        )

    logger.debug(
        f"LLM passthrough ({provider}): {request_data.method} {request_data.path} → {resp.status_code}"
    )

    # Return raw response with original content-type
    content_type = resp.headers.get("content-type", "application/json")
    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type=content_type,
    )


class LLMLogRequest(StrictBaseModel):
    """Request body for manually logging an LLM call."""

    input_messages: list[dict[str, Any]]
    response_content: str | None = None
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    tool_calls: list[dict[str, Any]] | None = None
    finish_reason: str = "stop"
    latency_ms: int | None = None
    trace_id: str | None = None
    invocation_id: str | None = None


class LLMLogResponse(StrictBaseModel):
    """Response from manually logging an LLM call."""

    llm_call_id: str
    cost_usd: float


@api_router.post("/llm/log", response_model=LLMLogResponse)
async def log_llm_call(request_data: LLMLogRequest):
    """Log an LLM call made to an external service for trace correlation.

    This endpoint allows agents to log LLM calls made directly to providers
    (OpenAI, Anthropic, etc.) so they appear in Dispatch traces alongside
    calls made through the llm.chat() proxy.

    Use this when:
    - Calling provider SDKs directly (openai, anthropic packages)
    - Using custom LLM integrations
    - You need features not supported by the Dispatch proxy

    The logged call will appear in the trace timeline with the same
    metrics as proxy calls (tokens, cost, latency).
    """
    logger = get_logger()
    from dispatch_cli.router.llm_pricing import calculate_cost

    # Calculate cost based on model and tokens
    cost_usd = calculate_cost(
        request_data.model, request_data.input_tokens, request_data.output_tokens
    )

    # Generate LLM call ID
    llm_call_id = str(uuid.uuid4())

    # Store LLM call for trace visualization
    llm_call_data = {
        "type": "llm_call",
        "llm_call_id": llm_call_id,
        "trace_id": request_data.trace_id,
        "invocation_id": request_data.invocation_id,
        "model": request_data.model,
        "provider": request_data.provider,
        "input_tokens": request_data.input_tokens,
        "output_tokens": request_data.output_tokens,
        "cost_usd": cost_usd,
        "latency_ms": request_data.latency_ms,
        "finish_reason": request_data.finish_reason,
        "input_messages": request_data.input_messages,
        "response_content": request_data.response_content,
        "tool_calls": request_data.tool_calls,
        "ts": datetime.now(UTC).isoformat(),
        "logged_externally": True,  # Flag to indicate this was logged manually
    }
    await store_llm_call(llm_call_data)

    logger.debug(
        f"Logged external LLM call: {request_data.model} ({request_data.provider}), "
        f"{request_data.input_tokens} in / {request_data.output_tokens} out"
    )

    return LLMLogResponse(llm_call_id=llm_call_id, cost_usd=cost_usd)


@api_router.get("/llm/calls")
async def list_recent_llm_calls(limit: int = Query(default=50, ge=1, le=100)):
    """List recent LLM calls from local storage."""
    async with _llm_calls_lock:
        calls = list(_llm_calls)[-limit:]
        calls.reverse()  # Most recent first
        return {"calls": calls}


# Include the API router
app.include_router(api_router, prefix=f"/api/unstable/namespace/{DEV_NAMESPACE}")
app.include_router(api_router, prefix="/api/unstable")

if __name__ == "__main__":
    import sys

    import uvicorn

    from dispatch_cli.commands.router import register_router, unregister_router

    logger = get_logger()
    port = LOCAL_ROUTER_PORT
    if sys.argv and len(sys.argv) > 1:
        port = int(sys.argv[1])
        if port < 1 or port > 65535:
            logger.error(f"Invalid port: {port}")
            sys.exit(1)

    # Track if cleanup has been done to avoid double-cleanup (use list for mutability)
    _cleanup_state = {"done": False}

    def _cleanup_and_exit(
        signum: int | None = None,
        frame: Any = None,  # noqa: ARG001
    ) -> None:
        """Clean up agents and exit. Called on SIGINT/SIGTERM or normal shutdown."""
        if _cleanup_state["done"]:
            return
        _cleanup_state["done"] = True

        sig_name = signal.Signals(signum).name if signum else "shutdown"
        logger.info(f"Router received {sig_name}, stopping all agents...")

        # Stop all agents
        stopped, failed = _stop_all_agents_sync()
        if stopped:
            logger.info(f"Stopped agents: {stopped}")
        if failed:
            logger.warning(f"Failed to stop some agents: {failed}")

        # Unregister router
        unregister_router(port)
        logger.debug(f"Unregistered router on port {port}")

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, _cleanup_and_exit)
    signal.signal(signal.SIGTERM, _cleanup_and_exit)

    # Register this router with tracking system
    register_router(port, os.getpid())
    logger.info(f"Starting router service on port {port}")

    # Check LLM provider configuration and warn if none are set up
    try:
        from dispatch_cli.router.local_llm import get_llm_status_message

        any_configured, status_msg = get_llm_status_message()
        if not any_configured:
            logger.warning(
                "\n"
                "⚠️  No LLM providers configured - agents using llm.chat() will fail.\n"
                "\n"
                f"{status_msg}\n"
                "\n"
                "Add API keys using the secrets command (stored securely in macOS Keychain):\n"
                "  dispatch secret local add OPENAI_API_KEY\n"
                "  dispatch secret local add ANTHROPIC_API_KEY\n"
                "\n"
                "Then restart the router.\n"
            )
        else:
            logger.info(f"LLM providers:\n{status_msg}")
    except Exception as e:
        logger.debug(f"Could not check LLM provider status: {e}")

    try:
        uvicorn.run(app, host="0.0.0.0", port=port)
    finally:
        # Final cleanup in case signals didn't trigger
        _cleanup_and_exit()
