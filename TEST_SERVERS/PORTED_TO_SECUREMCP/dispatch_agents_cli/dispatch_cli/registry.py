"""Agent registry operations."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from dispatch_agents.models import Agent, AgentContainerStatus

REGISTRY_PATH = Path.home() / ".dispatch_agents" / "default" / "registry.db"
REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Ensure the registry database has the expected schema."""
    columns = conn.execute("PRAGMA table_info(agents)").fetchall()
    column_names = {col[1] for col in columns}
    if column_names and column_names != {"uid", "payload"}:
        conn.execute("DROP TABLE IF EXISTS agents")
        conn.commit()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS agents (
            uid TEXT PRIMARY KEY,
            payload TEXT NOT NULL
        )
        """
    )
    conn.commit()


@contextmanager
def _registry_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(REGISTRY_PATH)
    try:
        _ensure_schema(conn)
        yield conn
    finally:
        conn.close()


def _agent_to_row(agent: Agent) -> tuple[str, str]:
    payload = agent.model_dump(mode="json")
    return agent.uid, json.dumps(payload)


def add_agent_to_registry(
    name: str,
    topics: list[str] | None = None,
    status: str = AgentContainerStatus.BUILDING.value,
    metadata: dict | None = None,
) -> str:
    """Add agent to registry and return agent ID.

    Note: topics parameter is deprecated but kept for backward compatibility.
    Agents should register with functions instead.
    """
    metadata = metadata or {}
    agent = Agent.create(
        name=name,
        functions=[],  # Functions will be registered via separate endpoint
        status=status,
        metadata=metadata,
        org_id="local",  # Simple local router doesn't use orgs
        namespace="default",  # Simple local router doesn't use namespaces
    )
    if url := metadata.get("url"):
        agent.url = url

    with _registry_conn() as conn:
        conn.execute(
            "REPLACE INTO agents (uid, payload) VALUES (?, ?)",
            _agent_to_row(agent),
        )
        conn.commit()

    return agent.uid


def remove_agent_from_registry(name_or_id: str) -> bool:
    """Remove agent from registry by name or id. Returns True if found and removed."""
    agent = get_agent_from_registry(name_or_id)
    if not agent:
        return False

    with _registry_conn() as conn:
        conn.execute("DELETE FROM agents WHERE uid = ?", (agent.uid,))
        conn.commit()
    return True


def list_agents_from_registry() -> list[Agent]:
    """List all agents in registry as SDK Agent objects."""
    with _registry_conn() as conn:
        rows = conn.execute("SELECT uid, payload FROM agents ORDER BY uid").fetchall()

    agents = []
    for _, payload in rows:
        try:
            # Try to load agent directly
            agents.append(Agent.model_validate_json(payload))
        except Exception:
            # If validation fails (e.g., missing org_id/namespace from old data),
            # add defaults and retry
            data = json.loads(payload)
            if "org_id" not in data:
                data["org_id"] = "local"
            if "namespace" not in data:
                data["namespace"] = "default"
            agents.append(Agent.model_validate(data))

    return agents


def get_agent_from_registry(name_or_id: str) -> Agent | None:
    """Get specific agent by name or id as SDK Agent object."""
    with _registry_conn() as conn:
        row = conn.execute(
            "SELECT uid, payload FROM agents WHERE uid = ? OR json_extract(payload, '$.name') = ?",
            (name_or_id, name_or_id),
        ).fetchone()

    if not row:
        return None

    try:
        return Agent.model_validate_json(row[1])
    except Exception:
        # If validation fails (e.g., missing org_id/namespace from old data),
        # add defaults and retry
        data = json.loads(row[1])
        if "org_id" not in data:
            data["org_id"] = "local"
        if "namespace" not in data:
            data["namespace"] = "default"
        return Agent.model_validate(data)


def update_agent_status(
    name_or_id: str, status: str, metadata: dict | None = None
) -> bool:
    """Update agent status and metadata. Returns True if agent found and updated."""
    agent = get_agent_from_registry(name_or_id)
    if not agent:
        return False

    agent.status = AgentContainerStatus(status)
    now = datetime.now(UTC).isoformat()
    agent.last_heartbeat = now
    agent.last_updated = now

    metadata = metadata or {}
    merged_metadata = dict(agent.metadata or {})
    merged_metadata.update(metadata)
    agent.metadata = merged_metadata

    if metadata.get("url"):
        agent.url = metadata["url"]

    with _registry_conn() as conn:
        conn.execute(
            "REPLACE INTO agents (uid, payload) VALUES (?, ?)",
            _agent_to_row(agent),
        )
        conn.commit()

    return True
