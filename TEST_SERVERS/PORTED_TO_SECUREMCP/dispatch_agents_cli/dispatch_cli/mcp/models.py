"""Shared Pydantic models for MCP client and tools."""

from typing import Any, Literal

from pydantic import BaseModel, Field

# Schedule Request Models


class CreateScheduleRequest(BaseModel):
    """Request payload for creating a schedule."""

    agent_name: str = Field(description="Target agent name")
    function_name: str = Field(description="Function to invoke on each trigger")
    cron_expression: str = Field(
        description="Cron expression (e.g., '0 9 * * MON-FRI' for weekdays at 9am, '*/5 * * * *' for every 5 minutes)"
    )
    timezone: str = Field(
        default="UTC",
        description="Timezone for the cron expression (e.g., 'America/New_York', 'Europe/London')",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Static payload to pass to the function on each invocation",
    )
    description: str | None = Field(
        default=None, description="Human-readable description of the schedule"
    )
    timeout_seconds: int | None = Field(
        default=None,
        description="Timeout for each invocation in seconds (1-86400, max 24 hours)",
    )
    namespace: str = Field(description="Dispatch namespace")


class ListSchedulesRequest(BaseModel):
    """Request payload for listing schedules."""

    agent_name: str | None = Field(
        default=None, description="Filter schedules by agent name"
    )
    namespace: str = Field(description="Dispatch namespace")


class GetScheduleRequest(BaseModel):
    """Request payload for getting a schedule."""

    schedule_id: str = Field(description="Schedule ID to retrieve")
    namespace: str = Field(description="Dispatch namespace")


class UpdateScheduleRequest(BaseModel):
    """Request payload for updating a schedule."""

    schedule_id: str = Field(description="Schedule ID to update")
    cron_expression: str | None = Field(default=None, description="New cron expression")
    timezone: str | None = Field(default=None, description="New timezone")
    payload: dict[str, Any] | None = Field(default=None, description="New payload")
    description: str | None = Field(default=None, description="New description")
    is_paused: bool | None = Field(
        default=None, description="Set to true to pause, false to resume"
    )
    namespace: str = Field(description="Dispatch namespace")


class DeleteScheduleRequest(BaseModel):
    """Request payload for deleting a schedule."""

    schedule_id: str = Field(description="Schedule ID to delete")
    namespace: str = Field(description="Dispatch namespace")


# Schedule Response Models


class CreateScheduleResponse(BaseModel):
    """Response from creating a schedule."""

    schedule_id: str = Field(description="Unique identifier for the created schedule")
    message: str = Field(description="Success message")


class ScheduleInfo(BaseModel):
    """Information about a schedule."""

    schedule_id: str = Field(description="Unique schedule identifier")
    agent_name: str = Field(description="Target agent name")
    function_name: str = Field(description="Function to invoke")
    cron_expression: str = Field(description="Cron expression")
    timezone: str = Field(description="Timezone for the cron expression")
    payload: dict[str, Any] = Field(description="Payload passed on each invocation")
    is_paused: bool = Field(description="Whether the schedule is paused")
    next_run: str | None = Field(default=None, description="Next scheduled run time")
    last_run: str | None = Field(default=None, description="Last run time")
    last_run_status: str | None = Field(
        default=None,
        description="Status of the last run (PENDING, RUNNING, COMPLETED, ERROR)",
    )
    last_run_trace_id: str | None = Field(
        default=None, description="Trace ID of the last run"
    )
    description: str | None = Field(default=None, description="Schedule description")


class ListSchedulesResponse(BaseModel):
    """Response from listing schedules."""

    schedules: list[ScheduleInfo] = Field(description="List of schedules")
    total: int = Field(description="Total number of schedules")


class GetScheduleResponse(ScheduleInfo):
    """Response from getting a schedule (same as ScheduleInfo)."""

    pass


class UpdateScheduleResponse(ScheduleInfo):
    """Response from updating a schedule (same as ScheduleInfo)."""

    pass


class DeleteScheduleResponse(BaseModel):
    """Response from deleting a schedule."""

    message: str = Field(description="Confirmation message")


# Agent Lifecycle Models


class StopAgentResponse(BaseModel):
    """Response from stopping an agent."""

    status: str = Field(description="Stop status")
    agent_name: str = Field(description="Name of the stopped agent")


class RebootAgentResponse(BaseModel):
    """Response from rebooting an agent."""

    status: str = Field(description="Reboot status")
    agent_name: str = Field(description="Name of the agent being rebooted")
    job_id: str = Field(
        description="Deployment job ID for polling status with get_deploy_status"
    )
    version: str = Field(description="Agent version being deployed")


# Topic & Event Models


class SubscribedHandler(BaseModel):
    """A handler subscribed to a topic."""

    agent_name: str
    handler_name: str


class TopicListItem(BaseModel):
    """A topic item as returned by the list topics endpoint."""

    topic: str
    topic_id: str | None = None
    created_at: str | None = None
    namespace: str | None = None
    webhook_enabled: bool | None = None
    webhook_provider: str | None = None
    subscribers: list[str] = []
    subscribed_handlers: list[SubscribedHandler] = []
    integration: str | None = None
    schema_: dict[str, Any] | None = Field(default=None, alias="schema")
    schema_locked: bool = False
    description: str | None = None
    sdk_docs_url: str | None = None

    model_config = {"populate_by_name": True}


class EventRecord(BaseModel):
    """A single event record from the event history."""

    uid: str | None = None
    message_type: str | None = None
    topic: str | None = None
    function_name: str | None = None
    schedule_name: str | None = None
    source: str | None = None
    timestamp: str | None = None
    trace_id: str | None = None
    parent_id: str | None = None
    payload: dict[str, Any] | None = None


class TraceSummary(BaseModel):
    """Summary of a trace (session) with agent invocations."""

    trace_id: str
    first_event_timestamp: str
    event_count: int
    trigger: str
    trigger_type: Literal["topic", "function", "schedule", "unknown"]
    trigger_agent: str | None = None
    trigger_function: str | None = None
    schedule_name: str | None = None
    last_activity: str
    root_event_uid: str | None = None
    root_topic: str | None = None
    agents_involved: list[str]


class RecentTracesResponse(BaseModel):
    """Response from the recent traces endpoint."""

    total_events: int
    unique_traces: int
    traces: list[TraceSummary]


class EventTraceResponse(BaseModel):
    """Response from the event trace endpoint."""

    events: list[dict[str, Any]] = Field(
        description="Tree-structured events with invocation enrichment"
    )
    llm_summary: dict[str, Any] | None = None


# Memory Models


class MemoryEntry(BaseModel):
    """A single long-term memory entry."""

    mem_key: str = Field(description="Memory key")
    mem_value: str = Field(description="Memory value")
    last_updated: str | None = Field(
        default=None, description="Last update timestamp (ISO 8601)"
    )


class ListLongTermMemoriesResponse(BaseModel):
    """Response from listing long-term memories."""

    agent_name: str = Field(description="Agent name")
    memories: list[MemoryEntry] = Field(description="List of memory entries")
