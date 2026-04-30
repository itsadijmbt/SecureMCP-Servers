"""Router management commands."""

import json
import os
import signal
import socket
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import requests
import typer
from dispatch_agents.models import TopicMessage

from dispatch_cli.logger import get_logger
from dispatch_cli.utils import LOCAL_ROUTER_PORT, LOCAL_ROUTER_URL

from ..registry import get_agent_from_registry

router_app = typer.Typer(name="router", help="Multi-agent router management")

# Router tracking directory
ROUTER_TRACKING_DIR = Path.home() / ".dispatch" / "routers"

# Router log directory
ROUTER_LOG_DIR = Path.home() / ".dispatch" / "logs"


def get_router_tracking_file(port: int) -> Path:
    """Get the path to the router tracking file for a given port."""
    return ROUTER_TRACKING_DIR / f"{port}.json"


def get_router_log_file(port: int) -> Path:
    """Get the path to the router log file for a given port."""
    return ROUTER_LOG_DIR / f"router-{port}.log"


def register_router(port: int, pid: int) -> None:
    """Register a running router in the tracking directory.

    Args:
        port: Port the router is running on
        pid: Process ID of the router
    """
    ROUTER_TRACKING_DIR.mkdir(parents=True, exist_ok=True)
    tracking_file = get_router_tracking_file(port)
    tracking_data = {
        "port": port,
        "pid": pid,
        "started_at": datetime.now(UTC).isoformat(),
    }
    with open(tracking_file, "w") as f:
        json.dump(tracking_data, f, indent=2)


def unregister_router(port: int) -> bool:
    """Remove a router from the tracking directory.

    Args:
        port: Port of the router to unregister

    Returns:
        True if file was removed, False if it didn't exist
    """
    tracking_file = get_router_tracking_file(port)
    if tracking_file.exists():
        tracking_file.unlink()
        return True
    return False


def get_tracked_routers() -> list[dict]:
    """Get all tracked routers.

    Returns:
        List of router info dicts with port, pid, and started_at
    """
    if not ROUTER_TRACKING_DIR.exists():
        return []

    routers = []
    for tracking_file in ROUTER_TRACKING_DIR.glob("*.json"):
        try:
            with open(tracking_file) as f:
                data = json.load(f)
                # Verify process is still running
                pid = data.get("pid")
                if pid:
                    try:
                        os.kill(pid, 0)  # Check if process exists
                        data["running"] = True
                    except OSError:
                        data["running"] = False
                routers.append(data)
        except (json.JSONDecodeError, OSError):
            continue

    return sorted(routers, key=lambda r: r.get("port", 0))


def get_active_router() -> dict | None:
    """Get the currently running router, if any.

    Returns:
        Router info dict with port, pid, started_at, running=True, or None.
    """
    routers = get_tracked_routers()
    running = [r for r in routers if r.get("running")]
    if not running:
        return None
    # Return the most recently started one
    return max(running, key=lambda r: r.get("started_at", ""))


def stop_router_by_port(port: int) -> tuple[bool, str]:
    """Stop a router on a specific port.

    Args:
        port: Port of the router to stop

    Returns:
        Tuple of (success, message)
    """
    logger = get_logger()

    # First try graceful shutdown via HTTP
    try:
        response = requests.post(f"{LOCAL_ROUTER_URL}:{port}/shutdown", timeout=2)
        if response.status_code == 200:
            unregister_router(port)
            return True, f"Stopped router on port {port}"
    except requests.exceptions.RequestException as e:
        logger.warning(f"Error stopping router: {e}")
        logger.warning("Router might not be responding, trying PID-based shutdown")
        pass  # Router might not be responding, try PID-based shutdown

    # Try to stop via PID file
    tracking_file = get_router_tracking_file(port)
    if tracking_file.exists():
        try:
            with open(tracking_file) as f:
                data = json.load(f)
                pid = data.get("pid")
                if pid:
                    try:
                        os.killpg(os.getpgid(pid), signal.SIGTERM)
                        unregister_router(port)
                        return True, f"Stopped router on port {port} (PID {pid})"
                    except ProcessLookupError:
                        unregister_router(port)
                        return (
                            True,
                            f"Router on port {port} was already stopped (cleaned up stale tracking file)",
                        )
                    except PermissionError:
                        return False, f"No permission to kill router process {pid}"
        except (json.JSONDecodeError, OSError) as e:
            logger.debug(f"Error reading tracking file: {e}")

    return False, f"No router found on port {port}"


def stop_all_routers() -> list[tuple[int, bool, str]]:
    """Stop all tracked routers.

    Returns:
        List of (port, success, message) tuples
    """
    results = []
    routers = get_tracked_routers()

    for router in routers:
        port = router.get("port")
        if port:
            success, message = stop_router_by_port(port)
            results.append((port, success, message))

    return results


@router_app.command("start")
def start_router(
    port: Annotated[
        int, typer.Option(help="Port to expose the router on")
    ] = LOCAL_ROUTER_PORT,
):
    """Start the multi-agent router in the background."""
    logger = get_logger()

    # Check if router is already running on this port
    try:
        resp = requests.get(f"{LOCAL_ROUTER_URL}:{port}/health", timeout=1.0)
        resp.raise_for_status()
        if resp.json().get("service") == "dispatch-local-router":
            logger.success(f"Router is already running on port {port}")
            logger.info("  • View logs: dispatch router logs")
            logger.info(f"  • View local dashboard: {LOCAL_ROUTER_URL}:{port}")
            return
    except Exception:
        logger.debug(f"No existing router found on port {port}, starting new one")

    if not start_router_background(port=port):
        raise typer.Exit(1)


def _dump_router_log(logger, log_file_path: Path, label: str) -> None:
    """Read the router log file and print its contents as error context."""
    try:
        content = log_file_path.read_text().strip()
        if content:
            logger.error(f"{label}:")
            for line in content.splitlines()[-10:]:
                logger.error(f"  {line}")
    except OSError:
        logger.debug(f"Could not read log file: {log_file_path}")


def start_router_background(port: int = LOCAL_ROUTER_PORT) -> bool:
    """Start the router as a background process, logging to a file.

    Returns True if the router started successfully, False otherwise.
    """
    logger = get_logger()
    router_service_py = (
        os.path.dirname(os.path.dirname(__file__)) + "/router/service.py"
    )
    router_cmd = [
        sys.executable,
        router_service_py,
        str(port),
    ]

    # Stop any existing router on a different port to enforce single-router
    active = get_active_router()
    if active and active["port"] != port:
        old_port = active["port"]
        logger.info(f"Stopping existing router on port {old_port}...")
        stop_router_by_port(old_port)

    # Check if something else is already using this port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        if s.connect_ex(("localhost", port)) == 0:
            logger.error(f"Port {port} is already in use")
            logger.info(
                f"Another process is listening on port {port}. "
                f"Either stop it or use a different port: dispatch router start --port <port>"
            )
            return False

    ROUTER_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file_path = get_router_log_file(port)
    log_f = open(log_file_path, "w")

    process = subprocess.Popen(
        router_cmd,
        stdout=log_f,
        stderr=subprocess.STDOUT,
        text=True,
        start_new_session=True,
    )

    # Wait for the router to become healthy
    max_wait = 10.0
    poll_interval = 0.2
    elapsed = 0.0
    while elapsed < max_wait:
        # Check if process died
        if process.poll() is not None:
            log_f.close()
            exit_code = process.returncode
            logger.error(f"Router process exited with code {exit_code}")
            _dump_router_log(logger, log_file_path, "Router output")
            return False

        try:
            resp = requests.get(f"{LOCAL_ROUTER_URL}:{port}/health", timeout=1.0)
            resp.raise_for_status()
            if resp.json().get("service") == "dispatch-local-router":
                logger.success(
                    f"Router started in background (port {port}, PID {process.pid})"
                )
                logger.info("  • View logs: dispatch router logs")
                logger.info(f"  • View local dashboard: {LOCAL_ROUTER_URL}:{port}")
                return True
        except Exception:
            logger.debug("Router not ready yet, retrying...")

        time.sleep(poll_interval)
        elapsed += poll_interval

    # Timed out — flush and show whatever we got
    log_f.flush()
    logger.error("Router failed to become healthy within 10s")
    _dump_router_log(logger, log_file_path, "Router output")
    logger.info("Full logs: dispatch router logs")
    return False


@router_app.command("stop")
def stop_router():
    """Stop all running routers."""
    logger = get_logger()
    try:
        results = stop_all_routers()
        if not results:
            logger.info("No running routers found")
        else:
            for _, success, message in results:
                if success:
                    logger.success(message)
                else:
                    logger.warning(message)

    except Exception as e:
        logger.error(f"Failed to stop: {e}")
        raise typer.Exit(1)


@router_app.command("status")
def router_status():
    """Show the status of the local router."""
    logger = get_logger()
    active = get_active_router()

    if not active:
        logger.info("No router running")
        logger.info("Start one with: dispatch router start")
        return

    port = active.get("port", "?")
    pid = active.get("pid", "?")
    started_at = active.get("started_at", "?")

    logger.success(f"Router running on port {port} (PID {pid})")
    logger.info(f"  Started: {started_at}")
    logger.info(f"  Dashboard: {LOCAL_ROUTER_URL}:{port}")
    logger.info("  Logs: dispatch router logs")


def _resolve_router_log_file() -> Path:
    """Find the most recent router log file.

    Prefers logs from running routers, falls back to most recently modified.
    """
    logger = get_logger()

    if not ROUTER_LOG_DIR.exists():
        logger.error("No router logs found")
        logger.info("Start a router with: dispatch router start")
        raise typer.Exit(1)

    log_files = list(ROUTER_LOG_DIR.glob("router-*.log"))
    if not log_files:
        logger.error("No router logs found")
        logger.info("Start a router with: dispatch router start")
        raise typer.Exit(1)

    # Prefer the running router's log, otherwise most recently modified
    active = get_active_router()
    if active:
        active_log = get_router_log_file(active["port"])
        if active_log.exists():
            return active_log

    return max(log_files, key=lambda f: f.stat().st_mtime)


@router_app.command("logs")
def router_logs(
    follow: Annotated[
        bool, typer.Option("--follow", "-f", help="Follow log output in real-time")
    ] = False,
    tail: Annotated[
        int, typer.Option(help="Number of lines to show from the end of the log")
    ] = 100,
):
    """View router logs."""
    log_file = _resolve_router_log_file()

    if follow:
        # Tail -f style: print last N lines then follow
        try:
            with open(log_file) as f:
                # Read existing lines and print the last `tail` lines
                lines = f.readlines()
                for line in lines[-tail:]:
                    print(line, end="")

                # Follow new output
                while True:
                    line = f.readline()
                    if line:
                        print(line, end="")
                    else:
                        time.sleep(0.1)
        except KeyboardInterrupt:
            pass
    else:
        # Print last N lines
        with open(log_file) as f:
            lines = f.readlines()
            for line in lines[-tail:]:
                print(line, end="")


@router_app.command("test")
def test_topic(
    topic: Annotated[str, typer.Argument(help="Topic to route to agents")],
    payload: Annotated[str, typer.Option(help="JSON payload")] = "{}",
    agent: Annotated[
        str | None,
        typer.Option(help="Optional: Test specific agent instead of routing"),
    ] = None,
    timeout: Annotated[int, typer.Option(help="Request timeout in seconds")] = 30,
    router_port: Annotated[
        int, typer.Option(help="Port to test the router on")
    ] = LOCAL_ROUTER_PORT,
):
    """Test routing a message by topic to all matching agents, or to a specific agent."""
    logger = get_logger()
    try:
        # Parse payload
        try:
            payload_dict = json.loads(payload)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON payload: {e}")
            raise typer.Exit(1)

        if agent:
            # Test specific agent directly (legacy mode)
            agent_obj = get_agent_from_registry(agent)
            if not agent_obj:
                logger.error(f"Agent not found: {agent}")
                raise typer.Exit(1)

            # Check if agent handles this topic
            if agent_obj.handles_topic(topic):
                logger.success(f"Agent '{agent_obj.name}' handles topic '{topic}'")
            else:
                logger.warning(
                    f"Agent '{agent_obj.name}' doesn't handle topic '{topic}'"
                )
                # Extract topics from agent functions
                agent_topics = [
                    trigger.topic
                    for func in agent_obj.functions
                    for trigger in func.triggers
                    if trigger.type == "topic" and trigger.topic
                ]
                logger.info(f"  Agent topics: {', '.join(agent_topics)}")

            logger.info("Testing agent directly (bypassing subscription system)")

            # Create message
            message = TopicMessage.create(
                topic=topic,
                payload=payload_dict,
                # uid=str(uuid.uuid4()),
                trace_id=str(uuid.uuid4()),
                sender_id="cli-test",
                # ts=datetime.now(UTC).isoformat(),
                parent_id=None,  # CLI test events are root events
            )

            logger.info(f"Testing agent '{agent_obj.name}' directly")
            logger.info(f"  Topic: {topic}")
            logger.info(f"  Payload: {json.dumps(payload_dict, indent=2)}")
            logger.info(f"  URL: {agent_obj.get_network_url()}")

            # Send request directly to agent
            try:
                response = requests.post(
                    agent_obj.get_network_url(),
                    headers={"Content-Type": "application/json"},
                    data=message.model_dump_json(),
                    timeout=timeout,
                )
                response.raise_for_status()
                result = response.json()

                logger.success("Response received:")
                logger.info(json.dumps(result, indent=2))

            except requests.exceptions.ConnectionError:
                logger.error("Connection failed - is the agent running?")
                logger.info("Try:")
                logger.info("  dispatch router status")
                raise typer.Exit(1)
            except requests.exceptions.Timeout:
                logger.error(f"Request timed out after {timeout}s")
                raise typer.Exit(1)
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error {response.status_code}: {e}")
                if response.text:
                    logger.info(f"Response: {response.text}")
                raise typer.Exit(1)
        else:
            # Route via router service (default mode)

            logger.info("Routing message via router service")
            logger.info(f"  Topic: {topic}")
            logger.info(f"  Payload: {json.dumps(payload_dict, indent=2)}")
            logger.info(f"  Router URL: {LOCAL_ROUTER_URL}:{router_port}")

            # Send request to router service
            event_data = {"payload": payload_dict, "sender_id": "cli-test"}

            try:
                response = requests.post(
                    f"{LOCAL_ROUTER_URL}:{router_port}/api/unstable/events/{topic}",
                    headers={"Content-Type": "application/json"},
                    json=event_data,
                    timeout=timeout,
                )
                response.raise_for_status()
                result = response.json()

                logger.success("Routing result:")
                logger.info(f"  Status: {result.get('status', 'unknown')}")
                logger.info(f"  Message: {result.get('message', 'No message')}")

                routed_to = result.get("routed_to", [])
                if routed_to:
                    logger.info(f"  Routed to {len(routed_to)} agent(s):")
                    for agent_info in routed_to:
                        logger.info(
                            f"    • {agent_info['name']} (topics: {', '.join(agent_info['topics'])})"
                        )

                responses = result.get("responses", {})
                if responses:
                    logger.info("Agent Responses:")
                    for agent_name, agent_response in responses.items():
                        logger.info(f"  {agent_name}:")
                        if (
                            isinstance(agent_response, dict)
                            and "error" in agent_response
                        ):
                            logger.error(f"    Error: {agent_response['error']}")
                        else:
                            logger.info(f"    {json.dumps(agent_response, indent=6)}")

            except requests.exceptions.ConnectionError:
                logger.error("Connection failed - is the router service running?")
                logger.info("Try:")
                logger.info("  dispatch router status")
                raise typer.Exit(1)
            except requests.exceptions.Timeout:
                logger.error(f"Request timed out after {timeout}s")
                raise typer.Exit(1)
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error {response.status_code}: {e}")
                if response.text:
                    logger.info(f"Response: {response.text}")
                raise typer.Exit(1)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise typer.Exit(1)
