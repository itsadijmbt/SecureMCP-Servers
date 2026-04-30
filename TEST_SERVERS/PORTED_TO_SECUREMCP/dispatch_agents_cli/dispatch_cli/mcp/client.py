"""Dispatch API client for MCP server."""

from __future__ import annotations

from typing import Any, Protocol

import httpx

from dispatch_cli.http_client import get_api_headers

from .config import MCPConfig
from .models import (
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


class AgentBackendClient(Protocol):
    """Backend operations needed by the agent MCP server."""

    def get_agent_info(self, agent_id: str, namespace: str | None = None) -> dict: ...

    async def invoke_function_async(
        self,
        agent_name: str,
        function_name: str,
        payload: dict,
        namespace: str | None = None,
        timeout_seconds: int | None = None,
    ) -> dict: ...

    async def get_invocation_status_async(
        self, invocation_id: str, namespace: str | None = None
    ) -> dict: ...


class OperatorBackendClient(AgentBackendClient, Protocol):
    """Backend operations needed by the operator MCP server."""

    def close(self) -> None: ...

    def list_namespaces(self) -> dict: ...

    def list_agents(
        self, namespace: str | None = None, limit: int = 50
    ) -> list[dict]: ...

    def delete_agent(self, agent_id: str, namespace: str | None = None) -> dict: ...

    def stop_agent(
        self, agent_name: str, namespace: str | None = None
    ) -> StopAgentResponse: ...

    def reboot_agent(
        self, agent_name: str, namespace: str | None = None
    ) -> RebootAgentResponse: ...

    def get_agent_logs(
        self,
        agent_name: str,
        version: str = "latest",
        namespace: str | None = None,
        limit: int = 100,
        **kwargs: Any,
    ) -> dict: ...

    def publish_event(
        self,
        topic: str,
        payload: dict,
        namespace: str | None = None,
        sender_id: str = "mcp-cli",
        **kwargs: Any,
    ) -> dict: ...

    def get_topic_schema(self, topic: str, namespace: str | None = None) -> dict: ...

    def list_topics(self, namespace: str) -> list[TopicListItem]: ...

    def get_recent_events(
        self,
        namespace: str,
        topic: str | None = None,
        limit: int = 20,
    ) -> list[EventRecord]: ...

    def get_event_trace(self, trace_id: str, namespace: str) -> EventTraceResponse: ...

    def get_recent_traces(
        self,
        namespace: str,
        topic: str | None = None,
        limit: int = 50,
    ) -> RecentTracesResponse: ...

    def get_invocation_status(
        self, invocation_id: str, namespace: str | None = None
    ) -> dict: ...

    async def get_deploy_status_async(
        self, job_id: str, namespace: str | None = None
    ) -> dict: ...

    def list_long_term_memories(
        self, agent_name: str, namespace: str
    ) -> ListLongTermMemoriesResponse: ...

    async def create_schedule(
        self, request: CreateScheduleRequest
    ) -> CreateScheduleResponse: ...

    async def list_schedules(
        self, request: ListSchedulesRequest
    ) -> ListSchedulesResponse: ...

    async def get_schedule(
        self, request: GetScheduleRequest
    ) -> GetScheduleResponse: ...

    async def update_schedule(
        self, request: UpdateScheduleRequest
    ) -> UpdateScheduleResponse: ...

    async def delete_schedule(
        self, request: DeleteScheduleRequest
    ) -> DeleteScheduleResponse: ...

    async def submit_feedback(self, payload: dict[str, Any]) -> None: ...


class DispatchAPIClient:
    """Client for Dispatch backend API.

    Provides sync methods for most operations and async methods for MCP tools
    that need non-blocking behavior. Schedule operations are async-only.
    """

    def __init__(self, config: MCPConfig):
        self.config = config
        self.client = httpx.Client(timeout=30.0)
        self._async_client: httpx.AsyncClient | None = None

    def close(self) -> None:
        """Close the sync HTTP client."""
        self.client.close()

    async def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create the async client (lazy initialization)."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(timeout=30.0)
        return self._async_client

    async def close_async(self) -> None:
        """Close the async client if it exists."""
        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None

    def _namespaced_url(self, endpoint: str, namespace: str | None = None) -> str:
        """Build namespaced API URL."""
        ns = namespace or self.config.namespace
        return f"{self.config.deploy_url}/namespace/{ns}{endpoint}"

    def _global_url(self, endpoint: str) -> str:
        """Build global API URL."""
        return f"{self.config.deploy_url}{endpoint}"

    def _headers(self) -> dict[str, str]:
        """Resolve fresh auth headers for each request."""
        credential = self.config.credential_provider.resolve()
        return get_api_headers(credential.access_token)

    def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make a sync request with the current resolved credential."""
        return self.client.request(method, url, headers=self._headers(), **kwargs)

    async def _request_async(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make an async request with the current resolved credential."""
        client = await self._get_async_client()
        return await client.request(method, url, headers=self._headers(), **kwargs)

    # Namespace Operations
    def list_namespaces(self) -> dict:
        """List all accessible namespaces."""
        url = self._global_url("/namespaces/list")
        resp = self._request("GET", url)
        resp.raise_for_status()
        return resp.json()

    # Agent Operations
    def list_agents(self, namespace: str | None = None, limit: int = 50) -> list[dict]:
        """List agents in namespace."""
        url = self._namespaced_url("/agents/list", namespace)
        resp = self._request("GET", url, params={"limit": limit})
        resp.raise_for_status()
        return resp.json()

    def get_agent_info(self, agent_id: str, namespace: str | None = None) -> dict:
        """Get agent details and schema."""
        url = self._namespaced_url(f"/agents/{agent_id}", namespace)
        # Use custom timeout for faster failure
        resp = self._request("GET", url, timeout=5.0)
        resp.raise_for_status()
        return resp.json()

    def delete_agent(self, agent_id: str, namespace: str | None = None) -> dict:
        """Delete agent."""
        url = self._namespaced_url(f"/agents/{agent_id}", namespace)
        resp = self._request("DELETE", url)
        resp.raise_for_status()
        return resp.json()

    def stop_agent(
        self, agent_name: str, namespace: str | None = None
    ) -> StopAgentResponse:
        """Stop agent by scaling to 0 instances and marking as disabled."""
        url = self._namespaced_url(f"/agents/{agent_name}/stop", namespace)
        resp = self._request("POST", url)
        resp.raise_for_status()
        return StopAgentResponse.model_validate(resp.json())

    def reboot_agent(
        self, agent_name: str, namespace: str | None = None
    ) -> RebootAgentResponse:
        """Reboot agent by rebuilding from source and redeploying."""
        url = self._namespaced_url(f"/agents/{agent_name}/reboot", namespace)
        resp = self._request("POST", url)
        resp.raise_for_status()
        return RebootAgentResponse.model_validate(resp.json())

    def get_agent_logs(
        self,
        agent_name: str,
        version: str = "latest",
        namespace: str | None = None,
        limit: int = 100,
        **kwargs,
    ) -> dict:
        """Get agent logs from CloudWatch."""
        url = self._namespaced_url(f"/logs/{agent_name}/{version}", namespace)
        params = {"limit": limit, **kwargs}
        resp = self._request("GET", url, params=params)
        resp.raise_for_status()
        return resp.json()

    # Event Operations
    def publish_event(
        self,
        topic: str,
        payload: dict,
        namespace: str | None = None,
        sender_id: str = "mcp-cli",
        **kwargs,
    ) -> dict:
        """Publish event to topic."""
        url = self._namespaced_url("/events/publish", namespace)
        data = {
            "topic": topic,
            "payload": payload,
            "sender_id": sender_id,
            **kwargs,
        }
        resp = self._request("POST", url, json=data)
        resp.raise_for_status()
        return resp.json()

    def get_topic_schema(self, topic: str, namespace: str | None = None) -> dict:
        """Get topic schema details."""
        url = self._namespaced_url(f"/events/schemas/{topic}", namespace)
        resp = self._request("GET", url)
        resp.raise_for_status()
        return resp.json()

    def list_topics(self, namespace: str) -> list[TopicListItem]:
        """List all topics in namespace."""
        url = self._namespaced_url("/events/topics", namespace)
        resp = self._request("GET", url)
        resp.raise_for_status()
        return [TopicListItem.model_validate(t) for t in resp.json()]

    def get_recent_events(
        self,
        namespace: str,
        topic: str | None = None,
        limit: int = 20,
    ) -> list[EventRecord]:
        """Get recent events, optionally filtered by topic."""
        url = self._namespaced_url("/events/recent", namespace)
        params: dict[str, str | int] = {"limit": limit}
        if topic:
            params["topic"] = topic
        resp = self._request("GET", url, params=params)
        resp.raise_for_status()
        return [EventRecord.model_validate(e) for e in resp.json()]

    def get_event_trace(self, trace_id: str, namespace: str) -> EventTraceResponse:
        """Get full event trace by trace ID."""
        url = self._namespaced_url(f"/events/trace/{trace_id}", namespace)
        resp = self._request("GET", url)
        resp.raise_for_status()
        return EventTraceResponse.model_validate(resp.json())

    def get_recent_traces(
        self,
        namespace: str,
        topic: str | None = None,
        limit: int = 50,
    ) -> RecentTracesResponse:
        """Get recent trace summaries."""
        url = self._namespaced_url("/events/traces/recent", namespace)
        params: dict[str, str | int] = {"limit": limit}
        if topic:
            params["topic"] = topic
        resp = self._request("GET", url, params=params)
        resp.raise_for_status()
        return RecentTracesResponse.model_validate(resp.json())

    # Invoke Operations
    def invoke_function(
        self,
        agent_name: str,
        function_name: str,
        payload: dict,
        namespace: str | None = None,
        timeout_seconds: int | None = None,
    ) -> dict:
        """Start a function invocation (returns invocation_id for polling).

        Args:
            agent_name: Target agent name
            function_name: Function to invoke
            payload: Input payload for the function
            namespace: Namespace (uses config default if not provided)
            timeout_seconds: Optional timeout for the invocation

        Returns:
            dict with invocation_id and initial status
        """
        url = self._namespaced_url("/invoke", namespace)
        data: dict[str, str | dict | int] = {
            "agent_name": agent_name,
            "function_name": function_name,
            "payload": payload,
        }
        if timeout_seconds is not None:
            data["timeout_seconds"] = timeout_seconds
        resp = self._request("POST", url, json=data)
        resp.raise_for_status()
        return resp.json()

    def get_invocation_status(
        self, invocation_id: str, namespace: str | None = None
    ) -> dict:
        """Get the status and result of an invocation.

        Args:
            invocation_id: The invocation ID returned from invoke_function
            namespace: Namespace (uses config default if not provided)

        Returns:
            dict with status, result (if completed), error (if failed)
        """
        url = self._namespaced_url(f"/invoke/{invocation_id}", namespace)
        resp = self._request("GET", url)
        resp.raise_for_status()
        return resp.json()

    def get_invocation_history(
        self,
        agent_name: str,
        function_name: str,
        namespace: str | None = None,
        limit: int = 20,
    ) -> dict:
        """Get invocation history for a function.

        Args:
            agent_name: Target agent name
            function_name: Function name
            namespace: Namespace (uses config default if not provided)
            limit: Maximum number of invocations to return

        Returns:
            dict with list of historical invocations
        """
        url = self._namespaced_url(
            f"/invoke/history/{agent_name}/{function_name}", namespace
        )
        resp = self._request("GET", url, params={"limit": limit})
        resp.raise_for_status()
        return resp.json()

    # Memory Operations
    def list_long_term_memories(
        self, agent_name: str, namespace: str
    ) -> ListLongTermMemoriesResponse:
        """List all long-term memories for an agent."""
        url = self._namespaced_url(f"/memory/long-term/agent/{agent_name}", namespace)
        resp = self._request("GET", url)
        resp.raise_for_status()
        return ListLongTermMemoriesResponse.model_validate(resp.json())

    # Async Invoke Operations (for MCP tools that need non-blocking behavior)
    async def invoke_function_async(
        self,
        agent_name: str,
        function_name: str,
        payload: dict,
        namespace: str | None = None,
        timeout_seconds: int | None = None,
    ) -> dict:
        """Start a function invocation asynchronously.

        Args:
            agent_name: Target agent name
            function_name: Function to invoke
            payload: Input payload for the function
            namespace: Namespace (uses config default if not provided)
            timeout_seconds: Optional timeout for the invocation

        Returns:
            dict with invocation_id and initial status
        """
        url = self._namespaced_url("/invoke", namespace)
        data: dict[str, str | dict | int] = {
            "agent_name": agent_name,
            "function_name": function_name,
            "payload": payload,
        }
        if timeout_seconds is not None:
            data["timeout_seconds"] = timeout_seconds
        resp = await self._request_async("POST", url, json=data)
        resp.raise_for_status()
        return resp.json()

    async def get_invocation_status_async(
        self, invocation_id: str, namespace: str | None = None
    ) -> dict:
        """Get the status and result of an invocation asynchronously.

        Args:
            invocation_id: The invocation ID returned from invoke_function
            namespace: Namespace (uses config default if not provided)

        Returns:
            dict with status, result (if completed), error (if failed)
        """
        url = self._namespaced_url(f"/invoke/{invocation_id}", namespace)
        resp = await self._request_async("GET", url)
        resp.raise_for_status()
        return resp.json()

    # Deploy Status Operations (async - used by MCP tools)
    async def get_deploy_status_async(
        self, job_id: str, namespace: str | None = None
    ) -> dict:
        """Get the status of a deployment job.

        Args:
            job_id: The deployment job ID returned from deploy
            namespace: Namespace (uses config default if not provided)

        Returns:
            dict with status, version, stages, logs, and error fields
        """
        url = self._namespaced_url(f"/agents/deployments/{job_id}", namespace)
        resp = await self._request_async("GET", url)
        resp.raise_for_status()
        return resp.json()

    # Schedule Operations (async only - used by MCP tools)
    async def create_schedule(
        self, request: CreateScheduleRequest
    ) -> CreateScheduleResponse:
        """Create a new function schedule.

        Args:
            request: CreateScheduleRequest with schedule configuration

        Returns:
            CreateScheduleResponse with schedule_id and message
        """
        url = self._namespaced_url("/schedules", request.namespace)
        data: dict = {
            "agent_name": request.agent_name,
            "function_name": request.function_name,
            "cron_expression": request.cron_expression,
            "timezone": request.timezone,
        }
        if request.payload:
            data["payload"] = request.payload
        if request.description is not None:
            data["description"] = request.description
        if request.timeout_seconds is not None:
            data["timeout_seconds"] = request.timeout_seconds
        resp = await self._request_async("POST", url, json=data)
        resp.raise_for_status()
        return CreateScheduleResponse.model_validate(resp.json())

    async def list_schedules(
        self, request: ListSchedulesRequest
    ) -> ListSchedulesResponse:
        """List schedules in namespace.

        Args:
            request: ListSchedulesRequest with optional agent_name filter

        Returns:
            ListSchedulesResponse with schedules list and total count
        """
        url = self._namespaced_url("/schedules", request.namespace)
        params = {}
        if request.agent_name:
            params["agent_name"] = request.agent_name
        resp = await self._request_async("GET", url, params=params)
        resp.raise_for_status()
        return ListSchedulesResponse.model_validate(resp.json())

    async def get_schedule(self, request: GetScheduleRequest) -> GetScheduleResponse:
        """Get details for a specific schedule.

        Args:
            request: GetScheduleRequest with schedule_id

        Returns:
            GetScheduleResponse with schedule details
        """
        url = self._namespaced_url(
            f"/schedules/{request.schedule_id}", request.namespace
        )
        resp = await self._request_async("GET", url)
        resp.raise_for_status()
        return GetScheduleResponse.model_validate(resp.json())

    async def update_schedule(
        self, request: UpdateScheduleRequest
    ) -> UpdateScheduleResponse:
        """Update a schedule's configuration.

        Args:
            request: UpdateScheduleRequest with schedule_id and fields to update

        Returns:
            UpdateScheduleResponse with updated schedule details
        """
        url = self._namespaced_url(
            f"/schedules/{request.schedule_id}", request.namespace
        )
        data: dict = {}
        if request.cron_expression is not None:
            data["cron_expression"] = request.cron_expression
        if request.timezone is not None:
            data["timezone"] = request.timezone
        if request.payload is not None:
            data["payload"] = request.payload
        if request.description is not None:
            data["description"] = request.description
        if request.is_paused is not None:
            data["is_paused"] = request.is_paused
        resp = await self._request_async("PATCH", url, json=data)
        resp.raise_for_status()
        return UpdateScheduleResponse.model_validate(resp.json())

    async def delete_schedule(
        self, request: DeleteScheduleRequest
    ) -> DeleteScheduleResponse:
        """Delete a schedule.

        Args:
            request: DeleteScheduleRequest with schedule_id

        Returns:
            DeleteScheduleResponse with confirmation message
        """
        url = self._namespaced_url(
            f"/schedules/{request.schedule_id}", request.namespace
        )
        resp = await self._request_async("DELETE", url)
        resp.raise_for_status()
        return DeleteScheduleResponse.model_validate(resp.json())

    async def submit_feedback(self, payload: dict[str, Any]) -> None:
        """Submit platform feedback asynchronously."""
        url = self._global_url("/feedback/")
        resp = await self._request_async("POST", url, json=payload)
        resp.raise_for_status()


def default_operator_backend_client(config: MCPConfig) -> OperatorBackendClient:
    """Build the default operator backend client for MCP runtime paths."""
    return DispatchAPIClient(config)
