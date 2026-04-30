"""Agent management commands."""

import concurrent.futures
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from typing import IO, Annotated, cast

import pathspec
import requests
import typer
from dispatch_agents.models import AgentContainerStatus
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.status import Status
from rich.table import Table
from watchfiles import PythonFilter, watch

from dispatch_cli.auth import get_auth_headers, handle_auth_error
from dispatch_cli.commands.router import (
    get_active_router,
    start_router_background,
)
from dispatch_cli.http_client import request_json
from dispatch_cli.logger import get_logger
from dispatch_cli.registry import (
    add_agent_to_registry,
    get_agent_from_registry,
    list_agents_from_registry,
    remove_agent_from_registry,
    update_agent_status,
)
from dispatch_cli.secrets import print_secret_sources
from dispatch_cli.utils import (
    DEFAULT_BASE_IMAGE,
    DISPATCH_API_BASE,
    DISPATCH_DIR,
    DISPATCH_LISTENER_FILE,
    LLM_PROVIDER_KEY_NAMES,
    LOCAL_ROUTER_PORT,
    LOCAL_ROUTER_URL,
    SUPPORTED_BASE_IMAGES,
    check_dotenv_has_all_secrets,
    check_env_secrets_not_in_config,
    configure_dispatch_project,
    derive_agent_name,
    extract_local_deps_from_pyproject,
    get_sdk_dependency,
    has_python_reqs,
    load_dispatch_config,
    validate_dispatch_project,
)
from dispatch_cli.version_check import (
    check_sdk_version_suggestion,
    validate_sdk_version,
)

agent_app = typer.Typer(
    name="agent",
    help="Agent lifecycle and registry management",
)

# Agent tracking directory (similar to router tracking)
AGENT_TRACKING_DIR = Path.home() / ".dispatch" / "agents"


def get_agent_tracking_file(agent_name: str) -> Path:
    """Get the path to the agent tracking file for a given agent name."""
    # Sanitize agent name for use as filename
    safe_name = agent_name.replace("/", "_").replace("\\", "_")
    return AGENT_TRACKING_DIR / f"{safe_name}.json"


def register_local_agent(
    agent_name: str, pid: int, port: int, agent_dir: str, router_port: int
) -> None:
    """Register a running local agent in the tracking directory.

    Args:
        agent_name: Name of the agent
        pid: Process ID of the agent
        port: gRPC port the agent is running on
        agent_dir: Directory containing the agent code
        router_port: Port of the router this agent is connected to
    """
    AGENT_TRACKING_DIR.mkdir(parents=True, exist_ok=True)
    tracking_file = get_agent_tracking_file(agent_name)
    tracking_data = {
        "agent_name": agent_name,
        "pid": pid,
        "port": port,
        "agent_dir": agent_dir,
        "router_port": router_port,
        "started_at": datetime.now(UTC).isoformat(),
    }
    with open(tracking_file, "w") as f:
        json.dump(tracking_data, f, indent=2)


def unregister_local_agent(agent_name: str) -> bool:
    """Remove an agent from the tracking directory.

    Args:
        agent_name: Name of the agent to unregister

    Returns:
        True if file was removed, False if it didn't exist
    """
    tracking_file = get_agent_tracking_file(agent_name)
    if tracking_file.exists():
        tracking_file.unlink()
        return True
    return False


def get_tracked_agents() -> list[dict]:
    """Get all tracked local agents.

    Returns:
        List of agent info dicts with name, pid, port, agent_dir, started_at
    """
    if not AGENT_TRACKING_DIR.exists():
        return []

    agents = []
    for tracking_file in AGENT_TRACKING_DIR.glob("*.json"):
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
                agents.append(data)
        except (json.JSONDecodeError, OSError):
            continue

    return sorted(agents, key=lambda a: a.get("agent_name", ""))


def stop_local_agent_by_name(agent_name: str) -> tuple[bool, str]:
    """Stop a local agent by name using its tracked PID.

    Args:
        agent_name: Name of the agent to stop

    Returns:
        Tuple of (success, message)
    """
    logger = get_logger()
    tracking_file = get_agent_tracking_file(agent_name)

    if not tracking_file.exists():
        return False, f"Agent '{agent_name}' not found in tracking directory"

    try:
        with open(tracking_file) as f:
            data = json.load(f)
            pid = data.get("pid")
            if not pid:
                unregister_local_agent(agent_name)
                return False, f"Agent '{agent_name}' has no PID recorded"

            try:
                # Send SIGTERM to the process
                os.kill(pid, signal.SIGTERM)
                # Give it a moment to terminate
                time.sleep(0.5)
                # Check if still running
                try:
                    os.kill(pid, 0)
                    # Still running, send SIGKILL
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass  # Process has terminated

                unregister_local_agent(agent_name)
                return True, f"Stopped agent '{agent_name}' (PID {pid})"

            except ProcessLookupError:
                unregister_local_agent(agent_name)
                return (
                    True,
                    f"Agent '{agent_name}' was already stopped (cleaned up stale tracking file)",
                )
            except PermissionError:
                return False, f"No permission to kill agent process {pid}"

    except (json.JSONDecodeError, OSError) as e:
        logger.debug(f"Error reading tracking file: {e}")
        return False, f"Error reading tracking file for '{agent_name}'"


def stop_all_local_agents() -> list[tuple[str, bool, str]]:
    """Stop all tracked local agents.

    Returns:
        List of (agent_name, success, message) tuples
    """
    results = []
    agents = get_tracked_agents()

    for agent in agents:
        agent_name = agent.get("agent_name")
        if agent_name:
            success, message = stop_local_agent_by_name(agent_name)
            results.append((agent_name, success, message))

    return results


def find_available_port(start_port=50051):
    """Find an available port starting from the given port."""

    port = start_port
    while port < start_port + 100:  # Check up to 100 ports
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("localhost", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError(
        f"No available ports found in range {start_port}-{start_port + 100}"
    )


def get_agent_name_from_project(path: str, config: dict) -> str:
    """Get agent name from project, shared between run and dev commands."""

    return derive_agent_name(path, config)


def get_sdk_version_from_agent(agent_path: str) -> str | None:
    """Detect SDK version from agent project's virtual environment.

    Uses 'uv run' within the agent's directory to ensure we check
    the agent's venv, not the CLI's venv.

    Args:
        agent_path: Path to the agent project directory

    Returns:
        SDK version string, or None if detection fails
    """
    try:
        # Use 'uv run python' in the agent's directory to run within the agent's venv
        # This ensures we get the SDK version from the agent's environment, not CLI's
        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-c",
                'from importlib.metadata import version; print(version("dispatch-agents"))',
            ],
            capture_output=True,
            text=True,
            timeout=15,
            cwd=agent_path,
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            if version:
                return version
    except (subprocess.TimeoutExpired, subprocess.SubprocessError):
        pass

    return None


def _check_and_suggest_sdk_update(
    agent_path: str, force: bool = False, warn_only: bool = False
) -> bool:
    """Check agent's SDK version and suggest update if outdated.

    This provides a quick local check comparing the agent's SDK version
    with the CLI's bundled SDK version. Displays update command if needed.

    Args:
        agent_path: Path to the agent project directory
        force: If True, warn but don't block on outdated SDK (user explicitly bypassed)
        warn_only: If True, only warn (don't block) - for commands like init

    Returns:
        True if execution should continue, False if it should be blocked
    """

    logger = get_logger()

    detected_version = get_sdk_version_from_agent(agent_path)
    status, message = check_sdk_version_suggestion(detected_version)

    if status == "outdated" and message:
        # Extract command from message (after "To update, run:\n")
        parts = message.split("To update, run:\n")
        warning_msg = parts[0].strip()
        update_cmd = parts[1].strip() if len(parts) > 1 else ""

        if warn_only:
            logger.warning(warning_msg)
        else:
            logger.error(warning_msg)

        if update_cmd:
            logger.code(update_cmd, "bash", "To update, run:")

        if warn_only:
            # Just warn, don't block
            return True
        elif force:
            logger.warning("Continuing with outdated SDK due to --force flag.")
            return True
        else:
            logger.info("Use --force to continue anyway with the outdated SDK.")
            return False

    elif status == "not_installed" and message:
        # SDK not found - this shouldn't happen after init, but handle it
        parts = message.split("To add it, run:\n")
        warning_msg = parts[0].strip()
        update_cmd = parts[1].strip() if len(parts) > 1 else ""

        if warn_only:
            logger.warning(warning_msg)
        else:
            logger.error(warning_msg)

        if update_cmd:
            logger.code(update_cmd, "bash", "To add it, run:")

        if warn_only:
            return True
        elif force:
            logger.warning("Continuing without SDK due to --force flag.")
            return True
        else:
            logger.info("Use --force to continue anyway without the SDK.")
            return False

    elif status == "error" and message:
        logger.debug(f"SDK version check: {message}")

    # For "current", "newer", and "error" status, continue
    return True


def parallel_multipart_upload(
    file_path: str, part_urls: dict, progress: Progress
) -> list[dict]:
    """Upload all parts in parallel using ThreadPoolExecutor for true concurrency."""

    # Thread-safe progress updates
    progress_lock = threading.Lock()

    def thread_safe_add_task(description, total):
        with progress_lock:
            return progress.add_task(description, total=total)

    def thread_safe_update(task_id, **kwargs):
        with progress_lock:
            progress.update(task_id, **kwargs)

    def upload_part_sync(part_url, chunk_data, part_number, task_id):
        """Upload a single part using requests with progress tracking."""
        start_time = time.time()
        try:
            # Create progress-tracking file object
            class ProgressFile:
                def __init__(self, data):
                    self.data = BytesIO(data)
                    self.uploaded = 0

                def read(self, size=-1):
                    chunk = self.data.read(size)
                    if chunk:
                        self.uploaded += len(chunk)
                        thread_safe_update(task_id, completed=self.uploaded)
                    return chunk

                def __len__(self):
                    return len(self.data.getvalue())

            progress_file = ProgressFile(chunk_data)

            response = requests.put(
                part_url,
                data=progress_file,
                timeout=300,  # 5 minute timeout
                headers={"Content-Length": str(len(chunk_data))},
            )

            if response.status_code != 200:
                end_time = time.time()
                logger = get_logger()
                logger.error(
                    f"Part {part_number}: Failed after {end_time - start_time:.2f}s - HTTP {response.status_code}"
                )
                raise RuntimeError(
                    f"Upload part {part_number} failed with status {response.status_code}: {response.text}"
                )

            etag = response.headers.get("ETag", "").strip('"')
            end_time = time.time()
            logger = get_logger()
            logger.debug(
                f"Part {part_number}: Completed after {end_time - start_time:.2f}s"
            )
            thread_safe_update(
                task_id, description=f"[green]Part {part_number} ✓[/green]"
            )
            return part_number, etag

        except Exception as exc:
            end_time = time.time()
            logger = get_logger()
            logger.error(
                f"Part {part_number}: Exception after {end_time - start_time:.2f}s - {exc}"
            )
            raise

    # Pre-read all chunks and prepare tasks
    upload_tasks = []
    with open(file_path, "rb") as f:
        for part_num_str, part_info in part_urls.items():
            part_number = int(part_num_str)
            part_size = part_info["size"]
            part_url = part_info["url"]

            # Read the chunk for this part
            chunk_data = f.read(part_size)
            if len(chunk_data) == 0:
                break

            # Create progress bar for this part
            task_id = thread_safe_add_task(f"Part {part_number}", total=part_size)

            upload_tasks.append((part_url, chunk_data, part_number, task_id))

    logger = get_logger()
    logger.debug(f"Starting {len(upload_tasks)} parallel uploads...")

    # Use ThreadPoolExecutor for true parallel uploads
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=min(len(upload_tasks), 5)
    ) as executor:
        future_to_part = {
            executor.submit(upload_part_sync, *task): task[2]  # task[2] is part_number
            for task in upload_tasks
        }

        completed_parts = []
        for future in concurrent.futures.as_completed(future_to_part):
            part_number = future_to_part[future]
            try:
                part_num, etag = future.result()
                completed_parts.append({"PartNumber": part_num, "ETag": etag})
            except Exception as exc:
                logger = get_logger()
                logger.error(f"Part {part_number} generated an exception: {exc}")
                raise exc

    # Sort by part number
    completed_parts.sort(key=lambda x: x["PartNumber"])
    return completed_parts


_NAMESPACED_PREFIXES = (
    "/agents",
    "/events",
    "/llm-config",
    "/llm",
    "/logs",
    "/memory",
    "/secrets",
    "/tools",
)


def build_namespaced_url(endpoint: str, namespace: str) -> str:
    """Build a namespaced API URL for deployment endpoints."""
    for prefix in _NAMESPACED_PREFIXES:
        if endpoint.startswith(prefix):
            return f"{DISPATCH_API_BASE}/api/unstable/namespace/{namespace}{endpoint}"
    raise ValueError(f"Unmapped endpoint prefix: {endpoint!r}")


def uv_is_installed() -> bool:
    """Check if 'uv' CLI is installed."""

    logger = get_logger()
    uv_executable = shutil.which("uv")
    if not uv_executable:
        logger.error("'uv' CLI is required for this command.")
        logger.info("Install it from https://docs.astral.sh/uv/ and try again.")
        return False
    return True


def validate_python_version_compatibility(
    project_path: str, warn_only: bool = True
) -> bool:
    """Check if requires-python is compatible with default base image.

    Args:
        project_path: Path to project directory
        warn_only: If True, only warn. If False, raise error on mismatch.

    Returns:
        True if compatible or no pyproject.toml, False if incompatible (when warn_only=False)
    """

    default_python_version = SUPPORTED_BASE_IMAGES.get(DEFAULT_BASE_IMAGE, "3.13")

    import tomlkit

    pyproject_path = os.path.join(project_path, "pyproject.toml")
    if not os.path.exists(pyproject_path):
        return True

    try:
        with open(pyproject_path) as f:
            doc = tomlkit.parse(f.read())
        requires = doc.get("project", {}).get("requires-python", "")
        if requires and isinstance(requires, str):
            # Check if it excludes the default Python version
            if (
                f"<{default_python_version}" in requires
                or f"<3.{default_python_version.split('.')[1]}" in requires
            ):
                logger = get_logger()
                msg = (
                    f"requires-python '{requires}' may not work with default base image (Python {default_python_version}). "
                    f"Consider updating requires-python or setting base_image in .dispatch.yaml"
                )
                if warn_only:
                    logger.warning(msg)
                    return True
                logger.error(msg)
    except Exception:
        pass  # Don't fail on parse errors
    return True


@agent_app.command("init")
def init(
    assume_yes: Annotated[
        bool,
        typer.Option(
            "--assume-yes",
            "-y",
        ),
    ] = False,
    path: Annotated[str, typer.Option()] = ".",
):
    """Initialize dispatch agent project by creating .dispatch/ folder with generated files."""

    logger = get_logger()
    if not uv_is_installed():
        return False
    logger.info(f"Initializing dispatch agent in {os.path.abspath(path)}...")

    if not os.path.isdir(path):
        logger.error(f"{path} is not a directory.")
        return False

    if not has_python_reqs(path, warn=False):
        logger.warning("No Python dependencies detected (pyproject.toml).")
        if assume_yes or typer.confirm(
            f"Would you like to create a new agent in this directory ({os.path.abspath(path)})?",
            default=True,
        ):
            # Run 'uv init --bare' to create a minimal pyproject.toml
            logger.debug("Creating minimal pyproject.toml using 'uv init --bare'...")

            # Get Python version from DEFAULT_BASE_IMAGE for requires-python

            default_python_version = SUPPORTED_BASE_IMAGES.get(
                DEFAULT_BASE_IMAGE, "3.13"
            )

            # Use -p flag to set Python version
            subprocess.run(
                [
                    "uv",
                    "init",
                    "--bare",
                    "--no-workspace",
                    "-p",
                    default_python_version,
                ],
                check=True,
                cwd=path,
            )

            # Update requires-python to use ~= (compatible release) instead of >=
            import tomlkit

            pyproject_path = os.path.join(path, "pyproject.toml")
            if os.path.exists(pyproject_path):
                with open(pyproject_path) as f:
                    doc = tomlkit.parse(f.read())
                if "project" not in doc:
                    doc["project"] = cast(dict, {})
                project = cast(dict, doc["project"])
                project["requires-python"] = f"~={default_python_version}.0"
                with open(pyproject_path, "w") as f:
                    f.write(tomlkit.dumps(doc))
                logger.info(
                    f"Set requires-python = '~={default_python_version}.0' to match base image"
                )

            sdk_dep = get_sdk_dependency()
            if assume_yes or typer.confirm(f"Adding {sdk_dep}...", default=True):
                subprocess.run(["uv", "add", sdk_dep], check=True, cwd=path)
    else:  # has pyproject.toml
        try:
            subprocess.run(
                ["uv", "pip", "show", "dispatch_agents"], check=True, cwd=path
            )
        except subprocess.CalledProcessError:
            sdk_dep = get_sdk_dependency()
            if assume_yes or typer.confirm(f"Adding {sdk_dep}...", default=True):
                subprocess.run(["uv", "add", sdk_dep], check=True, cwd=path)
        logger.success("Python dependencies detected.")

        # Warn if requires-python incompatible with default base image
        validate_python_version_compatibility(path, warn_only=True)

    config = configure_dispatch_project(path, assume_yes)
    agent_name = get_agent_name_from_project(path, config)

    logger.info("")
    logger.info(
        f"[bold green]Agent Name:[/bold green] [bold cyan]{agent_name}[/bold cyan]"
    )
    logger.info("   (update agent_name in dispatch.yaml if you need to override)")
    logger.info("")

    # Create .dispatch directory
    dispatch_dir = os.path.join(path, DISPATCH_DIR)
    os.makedirs(dispatch_dir, exist_ok=True)

    # Create entrypoint file if it doesn't exist
    entrypoint_file = config.get("entrypoint", "agent.py")
    entrypoint_path = os.path.join(path, entrypoint_file)
    logger.debug(f"Using entrypoint: {entrypoint_file}")
    if not os.path.exists(entrypoint_path):
        logger.info(f"Creating entrypoint file: {entrypoint_file}")
        with open(entrypoint_path, "w") as f:
            f.write(
                f'''"""Generated agent entrypoint."""

import os

from dispatch_agents import fn, BasePayload

# Access agent name from environment (auto-set by Dispatch)
AGENT_NAME = os.environ.get("DISPATCH_AGENT_NAME", "unknown-agent")


class HelloWorldRequest(BasePayload):
    """Input payload for the hello_world function."""
    text: str


class HelloWorldResponse(BasePayload):
    """Output payload for the hello_world function."""
    response: str
    agent_name: str


@fn()
async def hello_world(payload: HelloWorldRequest) -> HelloWorldResponse:
    """Sample function that can be invoked by other agents.

    This function is callable via:
        result = await invoke("{agent_name}", "hello_world", {{"text": "Hello!"}})

    The payload parameter is automatically validated against the HelloWorldRequest schema.
    The return value must match the HelloWorldResponse schema.
    """
    # Example: Using long-term memory for persistence (requires backend connection)
    # from dispatch_agents import memory
    # await memory.long_term.add(mem_key="last_message", mem_val=payload.text)

    return HelloWorldResponse(
        response=f"Hello from {{AGENT_NAME}}! Received: {{payload.text}}",
        agent_name=AGENT_NAME,
    )
'''
            )

    # Create listener in .dispatch/
    listener_path = os.path.join(dispatch_dir, DISPATCH_LISTENER_FILE)
    logger.debug(f"Creating {listener_path}")
    template_dir = Path(__file__).parent.parent / "templates"
    shutil.copy(template_dir / "grpc_listener.py", listener_path)

    # Create schema extraction script in .dispatch/
    schema_path = os.path.join(dispatch_dir, "extract_schemas.py")
    logger.debug(f"Creating {schema_path}")
    shutil.copy(template_dir / "extract_schemas.py", schema_path)

    # add a .gitignore file so that .dispatch/ is not committed
    gitignore_path = os.path.join(dispatch_dir, ".gitignore")
    logger.debug(f"Creating {gitignore_path}")
    with open(gitignore_path, "w") as f:
        f.write("*\n")

    logger.success(f"Initialized! Files created in {dispatch_dir}")

    # Check for .gitignore and add .env if not present
    gitignore_main = os.path.join(path, ".gitignore")
    with open(gitignore_main, "a+") as f:
        f.seek(0)  # Move to beginning of file to read existing content
        content = f.read()
        existing_lines = {line.strip() for line in content.splitlines()}
        gitignore_main_items = [".venv/", "__pycache__", ".env", ".dispatch/"]
        for ignoree in gitignore_main_items:
            if ignoree.strip() not in existing_lines:
                f.write(ignoree + "\n")

    # Check for .env file, if missing create
    dotenv_path = os.path.join(path, ".env")
    if not os.path.exists(dotenv_path):
        with open(dotenv_path, "w+") as f:
            f.write(
                """# Put your secrets here. Local development will use this file, but deployed agents will never include this file for security reasons.
# To inject secrets in your deployed agent, use the `secrets` field of the .dispatch.yaml.
# OPENAI_API_KEY = ???
"""
            )

    # Create AGENTS.md if it doesn't exist
    agents_md_path = os.path.join(path, "AGENTS.md")
    if not os.path.exists(agents_md_path):
        with open(agents_md_path, "w") as f:
            f.write(
                "# Dispatch Agents\n\n"
                "For Dispatch Agents platform documentation, see https://dispatchagents.ai/llms.txt\n"
            )

    # Create CLAUDE.md if it doesn't exist
    claude_md_path = os.path.join(path, "CLAUDE.md")
    if not os.path.exists(claude_md_path):
        with open(claude_md_path, "w") as f:
            f.write("Read @./AGENTS.md\n")

    logger.success("Agent Created!")
    logger.info(f"You successfully created {agent_name}.")
    logger.info(f"Take a look in {entrypoint_file} to see the agent code.")
    logger.info("Run the following commands to get started:")
    logger.code(
        """dispatch router start    # In one terminal
dispatch agent dev --reload      # In another terminal""",
        "bash",
        title="Local Development",
    )
    logger.info("To deploy to production:")
    logger.code(
        """dispatch agent deploy""",
        "bash",
        title="Production Deployment",
    )


def _run_agent_process(
    cmd: list[str],
    cwd: str,
    env: dict[str, str],
    log_file: IO[str],
    is_interactive: bool,
    watch_path: str | None = None,
    agent_name: str | None = None,
    agent_port: int | None = None,
    router_port: int | None = None,
) -> None:
    """Run the agent process, optionally with hot-reload.

    Args:
        cmd: Command to run the agent.
        cwd: Working directory for the agent.
        env: Environment variables for the agent.
        log_file: File to write logs to.
        is_interactive: Whether to also print output to terminal.
        watch_path: If provided, watch this path for .py changes and restart.
        agent_name: Name of the agent (for PID tracking).
        agent_port: Port the agent is running on (for PID tracking).
        router_port: Port of the router (for PID tracking).
    """
    logger = get_logger()
    # Event to signal the output thread to stop
    stop_event = threading.Event()

    def start_process() -> subprocess.Popen[str]:
        return subprocess.Popen(
            args=cmd,
            cwd=cwd,
            text=True,
            bufsize=1,  # Line-buffered for real-time output
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

    def stop_process(proc: subprocess.Popen[str]) -> None:
        """Gracefully stop the process."""
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

    def stream_output(proc: subprocess.Popen[str]) -> None:
        """Stream output from process until it ends or stop_event is set.

        Uses readline() instead of iteration to avoid read-ahead buffering,
        ensuring output appears in real-time.
        """
        if proc.stdout is None:
            return
        # Use readline() instead of `for line in proc.stdout:` to avoid
        # Python's read-ahead buffering which can delay output significantly
        while True:
            if stop_event.is_set():
                break
            line = proc.stdout.readline()
            if not line:  # EOF
                break
            if is_interactive:
                print(line, end="", flush=True)
            log_file.write(line)
            log_file.flush()

    def register_process(proc: subprocess.Popen[str]) -> None:
        """Register the agent process for tracking."""
        if agent_name and proc.pid and agent_port and router_port:
            register_local_agent(
                agent_name=agent_name,
                pid=proc.pid,
                port=agent_port,
                agent_dir=os.path.abspath(cwd),
                router_port=router_port,
            )
            logger.debug(f"Registered agent {agent_name} with PID {proc.pid}")

    process = start_process()
    register_process(process)

    try:
        if watch_path:
            # Hot-reload mode: use a thread to stream output while watching files
            logger.info("🔄 Hot-reload enabled. Watching for .py file changes...")

            output_thread = threading.Thread(
                target=stream_output, args=(process,), daemon=True
            )
            output_thread.start()

            for changes in watch(watch_path, watch_filter=PythonFilter()):
                # Restart if files changed
                if changes:
                    changed = [str(c[1]) for c in changes]
                    logger.info(f"🔄 Detected changes: {', '.join(changed)}")
                    logger.info("🔄 Restarting agent...")
                    stop_event.set()
                    stop_process(process)
                    output_thread.join(timeout=2)

                    # Reset for next process
                    stop_event.clear()
                    process = start_process()
                    register_process(process)  # Re-register with new PID
                    output_thread = threading.Thread(
                        target=stream_output, args=(process,), daemon=True
                    )
                    output_thread.start()
        else:
            # Normal mode: just stream output until process exits
            stream_output(process)
            return_code = process.wait()
            if return_code != 0:
                raise subprocess.CalledProcessError(return_code, cmd)

    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down...")
    finally:
        stop_event.set()
        if process.poll() is None:
            stop_process(process)
        # Unregister agent when process stops
        if agent_name:
            unregister_local_agent(agent_name)
            logger.debug(f"Unregistered agent {agent_name}")


@agent_app.command("dev")
def dev(
    path: Annotated[str, typer.Option()] = ".",
    agent_port: Annotated[
        int | None,
        typer.Option("--agent-port", help="Port for the agent gRPC server"),
    ] = None,
    router_port: Annotated[int | None, typer.Option()] = None,
    reload: Annotated[bool, typer.Option()] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Enable verbose logging (shows subscribe events, debug info)",
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help="Continue even if SDK version is outdated",
        ),
    ] = False,
    allow_arbitrary_writes: Annotated[
        bool,
        typer.Option(
            "--allow-arbitrary-writes",
            help="Allow agent to write to any location (dangerous - disables filesystem isolation)",
        ),
    ] = False,
):
    """Run agent locally for development.

    Use --reload to automatically restart the agent when Python files change.
    Use --verbose/-v to show all SDK logs including subscription events.
    """

    logger = get_logger()
    if not validate_dispatch_project(path):
        raise typer.Exit(1)

    # Check if agent's SDK version matches CLI's suggested version
    if not _check_and_suggest_sdk_update(path, force=force):
        raise typer.Exit(1)

    # Load config and get agent name (same as run command)
    abs_path = os.path.abspath(path)
    config = load_dispatch_config(abs_path)
    agent_name = get_agent_name_from_project(abs_path, config)

    # Use dynamic port allocation for agent if not specified
    if agent_port is None:
        agent_port = find_available_port()
        logger.debug(f"Using port {agent_port} for agent {agent_name}")
    else:
        logger.debug(f"Using specified port {agent_port}")

    # Resolve router: use existing running router, or start one
    if router_port is not None:
        # Explicit port — check it's running
        if not check_router_running(router_port=router_port):
            logger.info("Router not running, starting it in the background...")
            if not start_router_background(port=router_port):
                logger.error(
                    "Failed to start router. Try running `dispatch router start` manually."
                )
                raise typer.Exit(1)
    else:
        # No port specified — check for an active router first
        active = get_active_router()
        if active:
            router_port = active["port"]
            logger.success(f"Using running router on port {router_port}")
        else:
            # Try to start on the default port
            router_port = LOCAL_ROUTER_PORT
            logger.info("No router running, starting one in the background...")
            if not start_router_background(port=router_port):
                logger.error(
                    f"Failed to start router on default port {router_port}.\n"
                    "  Try: dispatch agent dev --router-port <free-port>"
                )
                raise typer.Exit(1)

    # Pre-register agent URL with router (so it knows the correct gRPC port)
    agent_url = f"127.0.0.1:{agent_port}"
    try:
        register_url = f"{LOCAL_ROUTER_URL}:{router_port}/api/unstable/agents/register"
        resp = requests.post(
            register_url,
            json={"agent_name": agent_name, "url": agent_url},
            timeout=5,
        )
        resp.raise_for_status()
        logger.debug(f"Pre-registered agent {agent_name} at {agent_url}")
    except requests.RequestException as e:
        logger.warning(f"Failed to pre-register agent with router: {e}")
        # Continue anyway - router will fall back to default port

    # Generate schemas for local development
    try:
        generate_schemas_for_dev(abs_path, agent_name)
    except Exception as e:
        logger.warning(f"Schema generation failed: {e}")

    # Register agent in local SQLite database (same as run command)
    try:
        existing_agent = get_agent_from_registry(agent_name)
        if existing_agent:
            logger.debug(f"Updating existing agent: {agent_name}")
            update_agent_status(
                agent_name, AgentContainerStatus.DEPLOYED, {"url": agent_url}
            )
        else:
            logger.debug(f"Registering new agent: {agent_name}")
            add_agent_to_registry(
                agent_name, [], AgentContainerStatus.DEPLOYED, {"url": agent_url}
            )
    except Exception as e:
        logger.warning(f"Failed to register agent in database: {e}")

    uv_executable = shutil.which("uv")
    if not uv_executable:
        logger.error("'uv' CLI is required for `dispatch agent dev`.")
        logger.info("Install it from https://docs.astral.sh/uv/ and try again.")
        # TODO: fallback to creating a lightweight virtualenv with pip-installed requirements.
        raise typer.Exit(1)

    listener_rel_path = os.path.join(DISPATCH_DIR, DISPATCH_LISTENER_FILE)
    uv_args = []
    # Add required dependencies for the listener script
    uv_args.extend(["--with", "tomlkit", "--with", "pyyaml"])
    # if there is a .env file, load it with uv --env-file
    if os.path.exists(os.path.join(abs_path, ".env")):
        uv_args.extend(["--env-file", ".env"])
    check_dotenv_has_all_secrets(path, config)
    unconfigured_secrets = check_env_secrets_not_in_config(abs_path, config)
    if unconfigured_secrets:
        logger.info(
            "Local development will use the .env file, but these secrets will not be available in production unless they are added to .dispatch.yaml."
        )

    # Print the source of each secret for transparency
    configured_secrets = [s["name"] for s in (config.get("secrets") or [])]
    agent_env_file = os.path.join(abs_path, ".env")
    if configured_secrets:
        print_secret_sources(
            required_secrets=configured_secrets,
            agent_env_path=agent_env_file if os.path.exists(agent_env_file) else None,
        )

    cmd = [
        uv_executable,
        "run",
        *uv_args,
        "python",
        listener_rel_path,
        str(agent_port),
    ]
    logger.debug(
        f"Launching listener with uv: {' '.join(cmd)} (cwd={os.path.abspath(path)})"
    )

    # Create logs directory and log file
    logs_dir = os.path.join(abs_path, ".dispatch", "logs")
    os.makedirs(logs_dir, exist_ok=True)
    log_file_path = os.path.join(logs_dir, "agent.log")

    # Detect if we're running interactively or via MCP (piped)
    is_interactive = sys.stdout.isatty()

    # Common environment for the agent process
    # Start from the current environment so system PATH, HOME, etc. are preserved.
    # Agents may need system binaries (e.g. node for MCP servers).
    agent_env = os.environ.copy()
    agent_env.update(
        {
            "BACKEND_URL": LOCAL_ROUTER_URL + f":{router_port}",
            "DISPATCH_NAMESPACE": "dev",
            "DISPATCH_API_KEY": "local-dev-key",
            # Enable local dev mode behaviors (e.g., auto-shutdown on backend connection failure)
            "DISPATCH_LOCAL_DEV": "true",
            # Force unbuffered Python output so logs stream in real-time
            "PYTHONUNBUFFERED": "1",
        }
    )

    # Allow arbitrary writes if explicitly requested (dangerous)
    if allow_arbitrary_writes:
        agent_env["DISPATCH_ALLOW_ARBITRARY_WRITES"] = "1"
        logger.warning(
            "Arbitrary writes enabled - filesystem isolation is disabled. "
            "The agent can write to any location on your machine."
        )

    # Set up mock volume directory for local development
    volumes = config.get("volumes", [])
    if volumes:
        # Create a local directory to simulate the volume mount
        dev_data_dir = os.path.join(abs_path, ".dispatch", "dev-data")
        os.makedirs(dev_data_dir, exist_ok=True)

        # For each volume, create the mount path structure under dev-data
        for vol in volumes:
            mount_path = vol.get("mountPath", "/data")
            # Strip leading slash and create relative path
            relative_path = mount_path.lstrip("/")
            vol_dir = os.path.join(dev_data_dir, relative_path)
            os.makedirs(vol_dir, exist_ok=True)

        # Set environment variable for the agent to discover the dev data directory
        # The agent SDK can use this to redirect /data writes in local dev mode
        agent_env["DISPATCH_DEV_DATA_DIR"] = dev_data_dir

        # Disable Python bytecode caching to prevent .pyc writes that would
        # trigger the filesystem isolation audit hook
        agent_env["PYTHONDONTWRITEBYTECODE"] = "1"

        logger.info(f"Dev data directory: {dev_data_dir}")

    # Enable verbose SDK logging if requested
    if verbose:
        agent_env["DISPATCH_VERBOSE"] = "1"
        logger.info("Verbose mode enabled - showing all SDK logs")

    try:
        with open(file=log_file_path, mode="w") as log_f:
            _run_agent_process(
                cmd=cmd,
                cwd=path,
                env=agent_env,
                log_file=log_f,
                is_interactive=is_interactive,
                watch_path=abs_path if reload else None,
                agent_name=agent_name,
                agent_port=agent_port,
                router_port=router_port,
            )
    except subprocess.CalledProcessError as exc:
        logger.error(f"Listener process exited with status {exc.returncode}")
        raise typer.Exit(exc.returncode)


def generate_schemas_for_dev(abs_path: str, agent_name: str) -> None:
    # Create a dispatch directory for schemas
    dispatch_dir = os.path.join(abs_path, DISPATCH_DIR)
    os.makedirs(dispatch_dir, exist_ok=True)

    # Create a temporary directory for schema extraction
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy the existing extract_schemas.py template and modify it for local use
        template_dir = Path(__file__).parent.parent / "templates"
        schema_template = template_dir / "extract_schemas.py"
        local_extract_script = os.path.join(temp_dir, "extract_schemas_local.py")

        if not schema_template.exists():
            raise RuntimeError(f"Schema template not found at {schema_template}")

        # Read the template and modify it for local development
        template_content = schema_template.read_text()

        # Find the actual listener file path for more robust imports
        listener_file = None
        dispatch_dir_path = os.path.join(abs_path, DISPATCH_DIR)

        # Look for the listener file in .dispatch directory
        if os.path.exists(dispatch_dir_path):
            listener_path = os.path.join(dispatch_dir_path, DISPATCH_LISTENER_FILE)
            if os.path.exists(listener_path):
                listener_file = listener_path

        # If not found, look in the main directory (for agent.py, etc.)
        if not listener_file:
            for possible_name in ["agent.py", "agent_main.py", "main.py"]:
                candidate = os.path.join(abs_path, possible_name)
                if os.path.exists(candidate):
                    listener_file = candidate
                    break

        if not listener_file:
            raise RuntimeError(f"Could not find agent entry point in {abs_path}")

        # Extract module name from the listener file
        listener_module_name = os.path.splitext(os.path.basename(listener_file))[0]

        # Replace Docker-specific paths with local paths
        local_content = (
            template_content.replace(
                'sys.path.append("/app/.dispatch")', f'sys.path.insert(0, "{abs_path}")'
            )
            .replace(
                "from __dispatch_listener__ import entrypoint_module",
                f"import {listener_module_name} as entrypoint_module",
            )
            .replace(
                'os.makedirs("/app/.dispatch", exist_ok=True)',
                f'os.makedirs("{temp_dir}", exist_ok=True)',
            )
            .replace(
                'with open("/app/.dispatch/schemas.json", "w") as f:',
                f'with open(os.path.join("{temp_dir}", "schemas.json"), "w") as f:',
            )
        )

        # Write the modified script
        with open(local_extract_script, "w") as f:
            f.write(local_content)

        # Set up environment for schema extraction
        env = os.environ.copy()
        env["PYTHONPATH"] = abs_path

        # Add .env file support if present
        env_file = os.path.join(abs_path, ".env")
        if os.path.exists(env_file):
            # Load .env file manually since we're not using Docker
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env[key.strip()] = value.strip().strip("\"'")

        try:
            # Run schema extraction using uv to ensure proper dependencies
            logger = get_logger()
            uv_executable = shutil.which("uv")
            if uv_executable:
                cmd = [uv_executable, "run", "python", local_extract_script]
                logger.debug("Running schema extraction with uv...")
            else:
                # Fallback to direct Python execution
                cmd = [sys.executable, local_extract_script]
                logger.debug(
                    "Running schema extraction with system Python (uv not found)..."
                )

            result = subprocess.run(
                cmd, cwd=abs_path, env=env, capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                # Copy extracted schemas to dispatch directory
                temp_schemas = os.path.join(temp_dir, "schemas.json")
                if os.path.exists(temp_schemas):
                    final_schemas = os.path.join(dispatch_dir, "schemas.json")
                    shutil.copy(temp_schemas, final_schemas)
                    logger.success(f"Generated schemas: {final_schemas}")

                    # Show summary from the extraction output
                    if result.stdout:
                        # Look for the summary lines in stdout
                        for line in result.stdout.split("\n"):
                            if line.startswith("✓") or line.startswith("⚠"):
                                logger.info(line)
                else:
                    logger.warning(
                        "Schema extraction completed but no schemas.json found"
                    )
            else:
                logger.warning(f"Schema extraction failed: {result.stderr}")
                if result.stdout:
                    logger.debug(f"Output: {result.stdout}")

        except subprocess.TimeoutExpired:
            logger.warning("Schema extraction timed out")
        except Exception as e:
            logger.warning(f"Schema extraction error: {e}")


def validate_namespace(namespace: str, auth_headers: dict[str, str]) -> bool:
    """Validate that the namespace exists for the user's organization."""
    logger = get_logger()
    try:
        with Status("Validating namespace...", spinner="dots"):
            namespaces_data = request_json(
                "GET",
                f"{DISPATCH_API_BASE}/api/unstable/namespaces/list",
                auth_headers=auth_headers,
            )
            valid_namespaces = namespaces_data.get("namespaces", [])

            if namespace in valid_namespaces:
                return True

        # Namespace doesn't exist - show available namespaces and fail
        logger.error(f"Namespace '{namespace}' does not exist in your organization.")

        if valid_namespaces:
            logger.info("")
            logger.info("Available namespaces:")
            for ns in sorted(valid_namespaces):
                logger.info(f"  • {ns}")
            logger.info("")
            logger.info(
                "Please update the 'namespace' field in your dispatch.yaml "
                "to use one of the namespaces above."
            )
        else:
            logger.warning("No namespaces found in your organization.")
            logger.info("Please contact your organization admin to create a namespace.")

        return False

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            handle_auth_error("Invalid or expired API key")
        logger.error(f"Failed to validate namespace: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to validate namespace: {e}")
        return False


def check_required_secrets(
    config: dict,
    auth_headers: dict[str, str],
    namespace: str,
) -> bool:
    """Check if all required secrets from the YAML config exist in remote storage."""
    logger = get_logger()
    secrets_config = config.get("secrets", [])
    if not secrets_config:
        return True  # No secrets required

    logger.info("Checking required secrets...")

    # Extract secret paths from config, skipping LLM provider keys
    # (those are managed by the LLM gateway, not Secrets Manager)
    secret_paths = []
    for secret in secrets_config:
        if isinstance(secret, dict) and "secret_id" in secret:
            if secret.get("name") in LLM_PROVIDER_KEY_NAMES:
                continue
            secret_paths.append(secret["secret_id"])

    if not secret_paths:
        return True  # No secret paths to check

    try:
        # Check secrets existence using the backend API
        with Status("Checking secrets...", spinner="dots"):
            check_result = request_json(
                "POST",
                build_namespaced_url("/secrets/check", namespace),
                auth_headers=auth_headers,
                json={"secret_paths": secret_paths},
            )
        missing_secrets = []
        error_secrets = []

        for secret_status in check_result.get("secrets", []):
            if not secret_status.get("exists", False):
                if secret_status.get("error"):
                    error_secrets.append(
                        f"  • {secret_status['secret_path']}: {secret_status['error']}"
                    )
                else:
                    missing_secrets.append(f"  • {secret_status['secret_path']}")

        if error_secrets:
            logger.error("Errors checking secrets:")
            for error in error_secrets:
                logger.error(error)
            return False

        if missing_secrets:
            logger.error("Missing required secrets:")
            for missing in missing_secrets:
                logger.error(missing)
            logger.info("")
            logger.warning("Please upload the missing secrets using:")
            logger.code("dispatch secret manage --upload", "bash")
            return False

        logger.success(f"All {len(secret_paths)} required secrets found")
        return True

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            handle_auth_error("Authentication failed while checking secrets")
        logger.error(f"Failed to check secrets: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to check secrets: {e}")
        return False


def check_github_integration_if_needed(
    agent_schemas: dict,
    auth_headers: dict[str, str],
) -> list[str]:
    """Check if GitHub integration is installed when agent uses GitHub topics.

    This is a warning-only check. If the agent subscribes to github.* topics but
    no GitHub App installation is found, we warn the user but don't block deployment.

    Args:
        agent_schemas: Dict mapping topics to handler info
        auth_headers: Authentication headers for API requests

    Returns:
        List of warning messages (empty if no warnings)
    """
    logger = get_logger()
    warnings: list[str] = []

    # Find handlers subscribing to github.* topics
    github_topics: set[str] = set()
    for topic in agent_schemas.keys():
        if topic.startswith("github."):
            github_topics.add(topic)

    if not github_topics:
        return []  # No GitHub topics, no validation needed

    logger.debug(f"Agent subscribes to GitHub topics: {sorted(github_topics)}")

    # Check if GitHub integration is installed
    try:
        with Status("Checking GitHub integration...", spinner="dots"):
            data = request_json(
                "GET",
                f"{DISPATCH_API_BASE}/api/unstable/integrations/github/installations",
                auth_headers=auth_headers,
            )
            installations = data.get("installations", [])

            if not installations:
                warnings.append(
                    f"Agent subscribes to GitHub topics ({', '.join(sorted(github_topics))}) "
                    "but no GitHub App installation found. "
                    "Install the GitHub integration first via the Dispatch dashboard."
                )
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            warnings.append(
                "Could not verify GitHub integration: authentication failed"
            )
        else:
            warnings.append(
                f"Could not verify GitHub integration: HTTP {e.response.status_code}"
            )
    except Exception as e:
        warnings.append(f"Could not verify GitHub integration: {e}")

    return warnings


def check_required_mcp_servers(
    config: dict,
    auth_headers: dict[str, str],
    namespace: str,
) -> bool:
    """Check if all required MCP servers from the YAML config are installed in the namespace.

    The 'server' field in mcp_servers config refers to installation_name, not server_name.
    """
    logger = get_logger()
    mcp_servers_config = config.get("mcp_servers", [])
    if not mcp_servers_config:
        return True  # No MCP servers required

    logger.info("Checking required MCP servers...")

    # Extract installation names from config (the 'server' field is the installation name)
    required_installations = []
    for server_entry in mcp_servers_config:
        if isinstance(server_entry, dict) and "server" in server_entry:
            required_installations.append(server_entry["server"])
        elif isinstance(server_entry, str):
            required_installations.append(server_entry)

    if not required_installations:
        return True  # No installation names to check

    # Determine MCP registry URL
    if "localhost" in DISPATCH_API_BASE or "127.0.0.1" in DISPATCH_API_BASE:
        mcp_registry_url = os.getenv("MCP_REGISTRY_URL", "http://localhost:8081")
    else:
        mcp_registry_url = os.getenv("MCP_REGISTRY_BASE", DISPATCH_API_BASE)

    try:
        # List installed MCP servers in the namespace
        with Status("Checking MCP servers...", spinner="dots"):
            result = request_json(
                "GET",
                f"{mcp_registry_url}/api/v1/mcp/namespaces/{namespace}/servers",
                auth_headers=auth_headers,
            )
        # Response can be either {"installations": [...]} or {"servers": [...]}
        servers_list = result.get("installations", result.get("servers", []))
        # Check for installation_name (new field) or fall back to server_name
        installed_installations = set()
        for installation in servers_list:
            installation_name = installation.get(
                "installation_name", installation.get("server_name")
            )
            if installation_name:
                installed_installations.add(installation_name)

        missing_installations = []
        for installation_name in required_installations:
            if installation_name not in installed_installations:
                missing_installations.append(f"  • {installation_name}")

        if missing_installations:
            logger.error("Missing required MCP server installations:")
            for missing in missing_installations:
                logger.error(missing)
            logger.info("")
            if installed_installations:
                logger.info("Installed MCP servers in this namespace:")
                for installation in sorted(installed_installations):
                    logger.info(f"  • {installation}")
                logger.info("")
            logger.warning("Please install the required MCP servers using:")
            logger.code(
                f"dispatch mcp registry install <installation_name> --server <server_name> --namespace {namespace}",
                "bash",
            )
            return False

        logger.success(
            f"All {len(required_installations)} required MCP server installations found"
        )
        return True

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            handle_auth_error("Authentication failed while checking MCP servers")
        logger.error(f"Failed to check MCP servers: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to check MCP servers: {e}")
        return False


def check_router_running(router_port: int) -> bool:
    """Check if the router service is running on the given port."""
    try:
        resp = requests.get(f"{LOCAL_ROUTER_URL}:{router_port}/health", timeout=2.0)
        resp.raise_for_status()
        return resp.json().get("service") == "dispatch-local-router"
    except Exception:
        return False


def create_source_package(abs_path: str, config: dict) -> str:
    """Create source package for remote builds.

    Returns path to created source-package.tar.gz file.
    """
    logger = get_logger()
    dispatch_dir = os.path.join(abs_path, DISPATCH_DIR)
    agent_name = get_agent_name_from_project(abs_path, config)

    logger.info("Creating source package for remote build...")

    # Create temporary directory for package contents
    with tempfile.TemporaryDirectory() as temp_dir:
        package_dir = os.path.join(temp_dir, "package")
        os.makedirs(package_dir)

        # 1. Copy agent source code (respecting .gitignore)
        agent_dest = os.path.join(package_dir, "agent")
        logger.debug("  Copying agent source code...")

        # Parse .gitignore if present
        gitignore_spec: pathspec.PathSpec | None = None
        gitignore_path = os.path.join(abs_path, ".gitignore")
        if os.path.isfile(gitignore_path):
            with open(gitignore_path) as f:
                gitignore_spec = pathspec.PathSpec.from_lines("gitignore", f)
            ignored_count = sum(
                1
                for root, _dirs, files in os.walk(abs_path)
                for fn in files
                if gitignore_spec.match_file(
                    os.path.relpath(os.path.join(root, fn), abs_path)
                )
            )
            logger.info(f"  Ignoring {ignored_count} file(s) from .gitignore")

        def ignore_artifacts(directory: str, files: list[str]) -> list[str]:
            """Exclude build artifacts and gitignored files."""
            ignored = []
            rel_dir = os.path.relpath(directory, abs_path)
            for f in files:
                # Always ignore these regardless of .gitignore
                if f == ".dispatch":
                    ignored.append(f)
                elif f in {
                    "__pycache__",
                    ".git",
                    ".venv",
                    "venv",
                    ".env",
                    ".mypy_cache",
                    ".ruff_cache",
                    ".pytest_cache",
                }:
                    ignored.append(f)
                elif f.endswith(".pyc"):
                    ignored.append(f)
                # Also ignore files matched by .gitignore
                elif gitignore_spec:
                    rel_path = f if rel_dir == "." else os.path.join(rel_dir, f)
                    # Match both file path and directory path (with trailing /)
                    full_path = os.path.join(directory, f)
                    if os.path.isdir(full_path):
                        rel_path += "/"
                    if gitignore_spec.match_file(rel_path):
                        ignored.append(f)
            return ignored

        shutil.copytree(abs_path, agent_dest, ignore=ignore_artifacts)

        # 2. Build dependencies as wheels (local paths + git repos)
        # Extract from pyproject.toml (returns path str or git dict)
        pyproject_deps = extract_local_deps_from_pyproject(abs_path)

        # Also check config for backward compatibility (only supports path)
        config_deps = config.get("local_dependencies") or {}
        bundled_deps = {**pyproject_deps, **config_deps}

        # Always create dependencies directory (Dockerfile expects it to exist)
        dependencies_dir = os.path.join(agent_dest, "dependencies")
        os.makedirs(dependencies_dir, exist_ok=True)

        if bundled_deps:
            logger.debug("  Building dependencies as wheels...")

            for dep_name, dep_config in bundled_deps.items():
                # Handle path dependencies (local directory)
                if isinstance(dep_config, str):
                    if not os.path.isabs(dep_config):
                        abs_dep_path = os.path.join(abs_path, dep_config)
                    else:
                        abs_dep_path = dep_config

                    if os.path.exists(abs_dep_path):
                        logger.debug(f"    - Building local dependency: {dep_name}")
                        subprocess.run(
                            [
                                "uv",
                                "build",
                                "--wheel",
                                "--out-dir",
                                dependencies_dir,
                                abs_dep_path,
                            ]
                        )

                # Handle git dependencies (remote repo)
                elif isinstance(dep_config, dict) and "git" in dep_config:
                    # Skip dispatch-agents and dispatch-cli - backend provides these
                    if str(dep_name).replace("_", "-") in (
                        "dispatch-agents",
                        "dispatch-cli",
                    ):
                        logger.debug(
                            f"    - Skipping {dep_name} (provided by backend infrastructure)"
                        )
                        continue

                    git_url = dep_config["git"]
                    subdirectory = dep_config.get("subdirectory", "")
                    rev = dep_config.get("rev", "")

                    logger.debug(f"    - Downloading git dependency: {dep_name}")

                    # Create a temporary directory to clone the repo
                    clone_dir = os.path.join(temp_dir, f"git-{dep_name}")
                    try:
                        # Clone the repo
                        clone_cmd = ["git", "clone", git_url, clone_dir]
                        if rev:
                            clone_cmd.extend(["--branch", rev, "--depth", "1"])
                        subprocess.run(clone_cmd, check=True, capture_output=True)

                        # Build the wheel from the cloned repo
                        build_path = (
                            os.path.join(clone_dir, subdirectory)
                            if subdirectory
                            else clone_dir
                        )
                        build_result = subprocess.run(
                            [
                                "uv",
                                "build",
                                "--wheel",
                                "--out-dir",
                                dependencies_dir,
                                build_path,
                            ]
                        )
                        if build_result.returncode != 0:
                            logger.warning(
                                f"    Warning: Failed to build {dep_name}, build may fail"
                            )
                    except subprocess.CalledProcessError as e:
                        logger.warning(f"    Warning: Failed to clone {dep_name}: {e}")
                    except Exception as e:
                        logger.warning(
                            f"    Warning: Failed to process {dep_name}: {e}"
                        )

        # 2b. Pre-build all dependencies as wheels locally.
        # This ensures CodeBuild never runs setup.py from untrusted packages.
        # Any sdist-only packages get built here (on the user's machine) and
        # shipped as wheels in the source package.
        logger.debug("  Pre-building all dependencies as wheels...")
        try:
            compile_result = subprocess.run(
                [
                    "uv",
                    "pip",
                    "compile",
                    os.path.join(agent_dest, "pyproject.toml"),
                    "--output-file",
                    os.path.join(agent_dest, "requirements.txt"),
                ],
                capture_output=True,
                text=True,
                cwd=abs_path,
            )
            if compile_result.returncode == 0:
                # Download and build all deps as wheels
                download_result = subprocess.run(
                    [
                        "uv",
                        "pip",
                        "download",
                        "--requirement",
                        os.path.join(agent_dest, "requirements.txt"),
                        "--dest",
                        dependencies_dir,
                        "--only-binary",
                        ":all:",
                    ],
                    capture_output=True,
                    text=True,
                    cwd=abs_path,
                )
                if download_result.returncode != 0:
                    # Some packages may not have wheels — build them from sdist
                    logger.debug("  Some packages need sdist build, retrying...")
                    subprocess.run(
                        [
                            "uv",
                            "pip",
                            "download",
                            "--requirement",
                            os.path.join(agent_dest, "requirements.txt"),
                            "--dest",
                            dependencies_dir,
                        ],
                        capture_output=True,
                        text=True,
                        cwd=abs_path,
                    )
                # Clean up temp requirements file
                req_file = os.path.join(agent_dest, "requirements.txt")
                if os.path.exists(req_file):
                    os.remove(req_file)
        except Exception as e:
            logger.warning(f"  Warning: Failed to pre-build dependencies: {e}")
            logger.warning("  Build will attempt to install on the server")

        # 3. Clean pyproject.toml (remove all custom sources)
        # This prevents uv from trying to resolve local/git dependencies in Docker
        if bundled_deps:
            pyproject_path = os.path.join(agent_dest, "pyproject.toml")
            if os.path.exists(pyproject_path):
                import tomlkit

                try:
                    with open(pyproject_path) as f:
                        content = f.read()
                    doc = tomlkit.parse(content)

                    # Remove tool.uv.sources if it exists
                    if "tool" in doc:
                        tool_section = cast(dict, doc["tool"])
                        if "uv" in tool_section:
                            uv_section = cast(dict, tool_section["uv"])
                            if "sources" in uv_section:
                                del uv_section["sources"]
                                logger.debug(
                                    "  Removed [tool.uv.sources] from pyproject.toml (using wheels instead)"
                                )

                    with open(pyproject_path, "w") as f:
                        f.write(tomlkit.dumps(doc))
                except Exception as e:
                    logger.warning(f"  Warning: Could not clean pyproject.toml: {e}")

            # Remove uv.lock since it contains path/git references
            # uv sync will regenerate it from pyproject.toml + bundled wheels
            uv_lock_path = os.path.join(agent_dest, "uv.lock")
            if os.path.exists(uv_lock_path):
                os.remove(uv_lock_path)
                logger.debug("  Removed uv.lock (will regenerate from bundled wheels)")

        # 4. Extract schemas locally (no Docker needed, user trusts their own code)
        logger.debug("  Extracting schemas...")
        try:
            generate_schemas_for_dev(abs_path, agent_name)

            # Copy schemas.json to package
            schemas_src = os.path.join(dispatch_dir, "schemas.json")
            if os.path.exists(schemas_src):
                schemas_dest = os.path.join(agent_dest, ".dispatch")
                os.makedirs(schemas_dest, exist_ok=True)
                shutil.copy(schemas_src, os.path.join(schemas_dest, "schemas.json"))
                logger.success("  Schemas extracted and bundled")
            else:
                logger.warning(
                    "  Warning: No schemas.json generated, build will create empty schemas"
                )
        except Exception as e:
            logger.warning(f"  Warning: Schema extraction failed: {e}")
            logger.warning("  Build will proceed without pre-generated schemas")

        # 5. Create tarball
        output_path = os.path.join(dispatch_dir, "source-package.tar.gz")
        logger.debug(f"  Creating tarball: {output_path}")

        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(package_dir, arcname=".")

        # Get file size for reporting
        file_size = os.path.getsize(output_path)
        size_mb = file_size / (1024 * 1024)
        logger.success(f"Source package created: {size_mb:.2f} MB")

        return output_path


@agent_app.command("deploy")
def deploy(
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace to deploy the agent to (should be configured in .dispatch.yaml)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
    path: Annotated[str, typer.Option()] = ".",
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help="Skip schema compatibility warnings and deploy anyway",
        ),
    ] = False,
    no_wait: Annotated[
        bool,
        typer.Option(
            "--no-wait",
            help="Exit after uploading the agent image without waiting for deployment to complete. Prints DEPLOY_JOB_ID and DEPLOY_NAMESPACE for status polling.",
        ),
    ] = False,
):
    """Deploy the agent to a remote server."""
    abs_path = os.path.abspath(path)
    if not validate_dispatch_project(abs_path):
        raise typer.Exit(1)

    config = load_dispatch_config(abs_path)
    logger = get_logger()

    # Check if .env has secrets not configured in .dispatch.yaml
    unconfigured_secrets = check_env_secrets_not_in_config(abs_path, config)
    if unconfigured_secrets and not force:
        logger.error("Deployment blocked: unconfigured secrets found in .env file.")
        logger.info(
            "Add these secrets to dispatch.yaml or use --force to deploy anyway."
        )
        raise typer.Exit(1)

    # Warn if dispatch.yaml secrets include LLM provider API keys
    # These work as fallback credentials but the preferred approach is the LLM gateway
    config_secrets = config.get("secrets", []) or []
    conflicting_keys = [
        s.get("name") for s in config_secrets if s.get("name") in LLM_PROVIDER_KEY_NAMES
    ]
    if conflicting_keys:
        logger.warning(
            f"Found LLM provider keys in dispatch.yaml secrets: {conflicting_keys}. "
            "If the namespace has an LLM provider configured via `dispatch llm setup`, "
            "these keys are unused — the platform credential takes priority. "
            "If no platform credential is configured, these keys will be used as a fallback. "
            "To manage LLM credentials at the platform level, run `dispatch llm setup`."
        )

    # Get namespace from CLI option, environment variable, or config file
    if not namespace:
        namespace = config.get("namespace")

    if not namespace:
        logger.error("Namespace is required but not found in .dispatch.yaml.")
        logger.info(
            "Run 'dispatch agent init' to configure your namespace, or set DISPATCH_NAMESPACE environment variable."
        )
        raise typer.Exit(1)
    agent_name = get_agent_name_from_project(abs_path, config)

    # Check SDK version (every deploy)
    detected_sdk_version = get_sdk_version_from_agent(abs_path)
    if detected_sdk_version:
        logger.info(f"Detected SDK version: {detected_sdk_version}")
        status, message = validate_sdk_version(detected_sdk_version, DISPATCH_API_BASE)

        if status == "blocked":
            if not message:
                logger.error("SDK version check failed")
                raise typer.Exit(1)

            # Extract command from message (after "To update, run:\n")
            parts = message.split("To update, run:\n")
            error_msg = parts[0].strip()
            update_cmd = parts[1].strip() if len(parts) > 1 else ""

            logger = get_logger()
            logger.error(error_msg)

            if update_cmd:
                logger.code(update_cmd, "bash", "To update, run:")

            raise typer.Exit(1)
        elif status == "outdated":
            if not message:
                logger.warning("SDK version may be outdated")
            else:
                # Extract command from message
                parts = message.split("To update, run:\n")
                warning_msg = parts[0].strip()
                update_cmd = parts[1].strip() if len(parts) > 1 else ""

                logger = get_logger()
                logger.warning(warning_msg)

                if update_cmd:
                    logger.code(update_cmd, "bash", "To update, run:")

            if not force:
                user_confirmed = typer.confirm(
                    "Continue with deployment anyway?", default=True
                )
                if not user_confirmed:
                    logger.warning("Deployment cancelled.")
                    raise typer.Exit(0)
        elif status == "error":
            logger.warning(f"{message}")
    else:
        logger.warning(
            "Could not detect SDK version from agent project. "
            "Proceeding with deployment."
        )

    # Create source package for remote build
    tar_path = create_source_package(abs_path, config)
    content_type = "application/gzip"

    file_size = os.path.getsize(tar_path)
    logger.info(f"Agent name: {agent_name}")
    logger.info(f"Package size: {file_size / (1024 * 1024):.2f} MB")

    auth_headers = get_auth_headers()

    # Run validation checks
    logger.info("Running pre-deployment validation...")
    if not force:
        try:
            validate(namespace=namespace, path=path, force=force)
        except typer.Exit as e:
            logger.warning("Deployment cancelled due to validation failures.")
            logger.info("Use --force flag to skip validation checks.")
            raise e

    # Step 1: request upload URL
    # Always use multipart upload for reliability (works with any size)
    MULTIPART_THRESHOLD = 0  # 0 means always use multipart
    use_multipart = file_size > MULTIPART_THRESHOLD

    try:
        with Status("Requesting upload URL...", spinner="dots"):
            presign_resp = requests.post(
                build_namespaced_url("/agents/get_upload_url", namespace),
                data={
                    "agent_name": agent_name,
                    "namespace": namespace,
                    "content_type": content_type,
                    "multipart": str(use_multipart).lower(),
                    "file_size": str(file_size),
                },
                headers=auth_headers,
                timeout=60,
            )
            presign_resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:  # Unauthorized
            handle_auth_error("Invalid or expired API key")
        logger.error(f"Failed to get upload URL: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Failed to get upload URL: {e}")
        raise typer.Exit(1)

    payload = presign_resp.json()

    # Step 2: upload the tarball
    try:
        logger.info(f"Multipart upload ({file_size / (1024 * 1024):.2f}MB)")

        upload_id = payload.get("upload_id")
        bucket = payload.get("bucket")
        key = payload.get("key")
        part_urls = payload.get("part_urls", {})

        if not upload_id or not part_urls:
            logger.error("Backend did not return multipart upload info")
            raise typer.Exit(1)

        logger.info(f"Starting parallel multipart upload with {len(part_urls)} parts")

        # Use parallel upload with rich progress bars
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("•"),
            TextColumn("[blue]{task.completed}/{task.total} bytes"),
        ) as progress:
            completed_parts = parallel_multipart_upload(tar_path, part_urls, progress)

        # Complete the multipart upload
        with Status("Completing multipart upload...", spinner="dots"):
            complete_resp = requests.post(
                build_namespaced_url("/agents/complete_multipart", namespace),
                data={
                    "bucket": bucket,
                    "key": key,
                    "upload_id": upload_id,
                    "parts": json.dumps(completed_parts),
                },
                headers=auth_headers,
                timeout=60,
            )
            complete_resp.raise_for_status()
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise typer.Exit(1)

    logger.success("Upload complete")
    # Step 3: Push the image via codebuild
    # Note: secrets and other config are now read from dispatch.yaml in the uploaded source package
    try:
        with Status("Building and checking in image to production...", spinner="dots"):
            push_resp = requests.post(
                build_namespaced_url("/agents/push_image_via_codebuild", namespace),
                data={
                    "agent_name": agent_name,
                    "namespace": namespace,
                },
                headers=auth_headers,
                timeout=600,
            )
            push_resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:  # Unauthorized
            handle_auth_error("Invalid or expired API key")
        if e.response.status_code == 409:
            logger.error(
                f"A deployment is already in progress for agent '{agent_name}'. "
                "Wait for it to finish or cancel it before deploying again."
            )
            raise typer.Exit(1)
        logger.error(f"Failed to push image to production: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Failed to push image to production: {e}")
        raise typer.Exit(1)

    logger.success("Agent image built and checked in")
    job_id = push_resp.json().get("job_id")
    logger.info(f"Job ID: {job_id}")

    # Check if namespace has LLM providers configured (non-blocking)
    try:
        llm_resp = requests.get(
            build_namespaced_url("/llm-config/providers", namespace),
            headers=auth_headers,
            timeout=10,
        )
        if llm_resp.ok:
            llm_data = llm_resp.json()
            if not llm_data.get("providers"):
                logger.warning(
                    "No LLM providers configured for this namespace. "
                    "If your agent uses LLM calls, run `dispatch llm setup` to configure."
                )
    except Exception:
        pass  # Best-effort — don't block deploy

    # If you change any of this code, please update the MCP tool stdin parsing logic as well.
    if no_wait:
        logger.info(f"DEPLOY_JOB_ID={job_id}")
        logger.info(f"DEPLOY_NAMESPACE={namespace}")
        logger.info(
            "Deployment submitted. Use the get_deploy_status tool with the returned job_id and namespace to check progress."
        )
        return

    try:
        # Step 4: poll until the image is deployed, streaming logs in real-time
        job_status_url = build_namespaced_url(
            f"/agents/deployments/{job_id}", namespace
        )
        seen_logs = 0
        logger.info("Deploying agent...")
        while True:
            try:
                response = requests.get(
                    job_status_url, headers=auth_headers, timeout=15
                )
                response.raise_for_status()
                data = response.json()
                job_status = data.get("status")

                # Stream new log lines as they arrive
                logs = data.get("logs", [])
                for line in logs[seen_logs:]:
                    logger.info(f"  > {line}")
                seen_logs = len(logs)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 401:  # Unauthorized
                    handle_auth_error("Invalid or expired API key")
                else:
                    logger.warning(f"Polling error: {e}")
                    job_status = None
            except Exception as e:
                logger.warning(f"Polling error: {e}")
                job_status = None

            if job_status == "completed":
                logger.success(f"Agent deployed to remote server: {agent_name}")
                logger.info(f"You can see its status on {DISPATCH_API_BASE}")
                break
            elif job_status == "failed":
                error = data.get("error", "Unknown error")
                logger.error(f"Deployment failed: {error}")
                raise typer.Exit(1)
            elif job_status == "cancelled":
                logger.warning("Deployment was cancelled.")
                raise typer.Exit(1)
            time.sleep(2)
    except typer.Exit:
        raise
    except Exception as e:
        logger.error(f"Agent image failed to be deployed to production: {e}")
        raise typer.Exit(1)


@agent_app.command("unregister")
def unregister_agent():
    """Unregister current agent project from the local registry."""
    logger = get_logger()
    try:
        project_path = os.path.abspath(os.getcwd())

        # Find agent by project path
        agents = list_agents_from_registry()
        agent = None
        for a in agents:
            if a.name and os.path.abspath(a.name) == project_path:
                agent = a
                break

        if not agent:
            logger.warning(f"No agent registered for current directory: {project_path}")
            return

        if remove_agent_from_registry(agent.name):
            logger.success(f"Unregistered agent: {agent.name}")
        else:
            logger.warning(f"Failed to remove agent: {agent.name}")
    except Exception as e:
        logger.error(f"Failed to unregister agent: {e}")
        raise typer.Exit(1)


@agent_app.command("status")
def agent_status():
    """Show status of current agent project."""
    logger = get_logger()
    try:
        project_path = os.path.abspath(os.getcwd())

        # Find agent by project path
        agents = list_agents_from_registry()
        agent = None
        for a in agents:
            if a.name and os.path.abspath(a.name) == project_path:
                agent = a
                break

        if not agent:
            logger.warning(f"No agent registered for current directory: {project_path}")
            logger.info(
                "Run 'dispatch agent register --topics <topics>' to register this agent."
            )
            return

        logger.info("")
        logger.info(f"{agent.name}")
        logger.info(f"  Agent UID: {agent.uid}")
        logger.info(f"  Network URL: {agent.get_network_url()}")
        logger.info(f"  Status: {agent.status}")
        logger.info(f"  Created: {agent.created_at}")
        if agent.last_heartbeat:
            logger.info(f"  Last Heartbeat: {agent.last_heartbeat}")
        if agent.topics:
            logger.info(f"  Topics: {', '.join(agent.topics)}")
        else:
            logger.info("  Topics: None registered")
        if agent.metadata:
            logger.info(f"  Metadata: {agent.metadata}")
    except Exception as e:
        logger.error(f"Failed to get agent status: {e}")
        raise typer.Exit(1)


def extract_handler_schemas_from_agent(agent_path: str) -> dict:
    """Extract handler schemas from built agent (reads from .dispatch/schemas.json)."""
    import json

    logger = get_logger()
    try:
        # Read schemas from the local .dispatch directory (written during Docker build)
        schemas_path = os.path.join(agent_path, ".dispatch", "schemas.json")

        if not os.path.exists(schemas_path):
            # TODO(matt): Update CLI/web docs and remaining user-facing messages to
            # remove build-mode references now that `dispatch agent build` is gone.
            logger.warning("No schemas.json found. Run 'dispatch agent build' first.")
            return {}

        with open(schemas_path) as f:
            artifact = json.load(f)

        # Check if extraction was successful
        if not artifact.get("extraction_success", False):
            error_msg = artifact.get("error", {}).get("message", "Unknown error")
            logger.warning(f"Schema extraction failed during build: {error_msg}")
            return {}

        # Return just the schemas part to maintain API compatibility
        return artifact.get("schemas", {})

    except Exception as e:
        logger.warning(f"Failed to read schemas from {agent_path}: {e}")
        return {}


@agent_app.command("validate")
def validate(
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace to validate against (should be configured in .dispatch.yaml)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
    path: Annotated[str, typer.Option()] = ".",
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            help="Skip interactive prompts and auto-confirm actions",
        ),
    ] = False,
):
    """Validate agent configuration, namespace, and schema compatibility."""
    logger = get_logger()
    abs_path = os.path.abspath(path)
    if not validate_dispatch_project(abs_path):
        raise typer.Exit(1)

    config = load_dispatch_config(abs_path)

    # Get namespace from CLI option, environment variable, or config file
    if not namespace:
        namespace = config.get("namespace")

    if not namespace:
        logger.error("Namespace is required but not found in .dispatch.yaml.")
        logger.info(
            "Run 'dispatch agent init' to configure your namespace, or set DISPATCH_NAMESPACE environment variable."
        )
        raise typer.Exit(1)

    agent_name = get_agent_name_from_project(abs_path, config)
    logger.info(f"Agent name: {agent_name}")
    logger.info(f"Namespace: {namespace}")

    auth_headers = get_auth_headers()

    validation_passed = True

    # 1. Validate that the namespace exists
    logger.info("")
    logger.info("1. Validating namespace...")
    ns_valid = validate_namespace(namespace, auth_headers)
    if not ns_valid:
        validation_passed = False

    # 2. Check required secrets
    logger.info("")
    logger.info("2. Checking required secrets...")
    secrets_valid = check_required_secrets(config, auth_headers, namespace)
    if not secrets_valid:
        validation_passed = False

    # 3. Check required MCP servers
    logger.info("")
    logger.info("3. Checking required MCP servers...")
    mcp_valid = check_required_mcp_servers(config, auth_headers, namespace)
    if not mcp_valid:
        validation_passed = False

    # 4. Validating schema availability
    logger.info("")
    logger.info("4. Validating schema availability...")

    # Check if schemas already exist (from source package creation)
    schemas_path = os.path.join(abs_path, ".dispatch", "schemas.json")

    if os.path.exists(schemas_path):
        logger.debug(f"Using existing schemas from: {schemas_path}")
        logger.success("Schemas available.")
    else:
        logger.error(f"schemas.json not found at {schemas_path}")
        validation_passed = False

    # 5. Check dependencies resolve for linux (deployment target)
    logger.info("")
    logger.info("5. Checking dependencies resolve for linux...")
    try:
        dep_check = subprocess.run(
            [
                "uv",
                "sync",
                "--dry-run",
                "--python-platform",
                "linux",
                "--no-install-project",
            ],
            capture_output=True,
            text=True,
            cwd=abs_path,
        )
        if dep_check.returncode != 0:
            stderr = dep_check.stderr.strip()
            logger.error("Some dependencies don't have linux wheels:")
            for line in stderr.splitlines():
                if "error:" in line or "hint:" in line:
                    logger.error(f"  {line.strip()}")
            logger.info(
                "Add tool.uv.required-environments to your pyproject.toml "
                "to ensure your dependencies have linux wheels:"
            )
            logger.info(
                "  [tool.uv]\n"
                "  required-environments = [\"sys_platform == 'linux'"
                " and platform_machine == 'x86_64'\"]"
            )
            validation_passed = False
        else:
            logger.success("All dependencies have linux-compatible packages.")
    except FileNotFoundError:
        logger.debug("uv not found, skipping linux dependency check.")

    # 6. Check handler schemas and typed payloads
    logger.info("")
    logger.info("6. Checking handler schemas and typed payloads...")
    try:
        agent_schemas = extract_handler_schemas_from_agent(abs_path)
        if not agent_schemas:
            logger.debug("No handler schemas found in agent.")
        else:
            logger.info(f"Found {len(agent_schemas)} handler(s):")
            for handler_name, handler_info in agent_schemas.items():
                topics = handler_info.get("topics", [handler_name])
                topics_str = ", ".join(topics) if topics else handler_name
                logger.info(f"  • {handler_name} → {topics_str}")

            # Check for typed payload compliance
            if not check_typed_payload_compliance(abs_path):
                validation_passed = False
    except Exception as e:
        logger.error(f"Handler schema validation failed: {e}")
        validation_passed = False

    # 7. Check schema compatibility
    logger.info("")
    logger.info("7. Checking schema compatibility...")
    try:
        if not agent_schemas:
            agent_schemas = extract_handler_schemas_from_agent(abs_path)

        if agent_schemas:
            if not check_schema_compatibility_for_validation(
                agent_schemas, namespace, auth_headers, agent_name, force
            ):
                validation_passed = False
        else:
            logger.debug("No schemas to check compatibility for.")
    except Exception as e:
        logger.error(f"Schema validation failed: {e}")
        validation_passed = False

    # 8. Check GitHub integration if agent uses GitHub topics
    logger.info("")
    logger.info("8. Checking GitHub integration requirements...")
    try:
        if agent_schemas:
            github_warnings = check_github_integration_if_needed(
                agent_schemas, auth_headers
            )
            for warning in github_warnings:
                logger.warning(warning)
            if not github_warnings:
                logger.success("GitHub integration check passed.")
        else:
            logger.debug("No schemas to check GitHub integration for.")
    except Exception as e:
        logger.warning(f"Could not check GitHub integration: {e}")

    # Summary
    logger.info("")
    logger.info("Validation Summary:")
    if validation_passed:
        logger.success("All validations passed!")
        logger.info("Agent is ready for deployment.")
    else:
        logger.error("Some validations failed.")
        logger.info("Fix the issues above before deploying.")
        raise typer.Exit(1)


def check_schema_compatibility_for_validation(
    agent_schemas: dict,
    namespace: str,
    auth_headers: dict,
    agent_name: str,
    force: bool = False,
) -> bool:
    """Check schema compatibility for validation command (non-interactive version)."""
    logger = get_logger()

    compatibility_issues = []
    new_topics = []
    existing_topics = []

    for handler_name, handler_info in agent_schemas.items():
        # Get topics from handler_info, fallback to handler_name for legacy support
        topics = handler_info.get("topics", [handler_name])
        if not topics:
            topics = [handler_name]

        for topic in topics:
            try:
                # Fetch existing topic schema from backend
                response = requests.get(
                    build_namespaced_url(f"/events/schemas/{topic}", namespace),
                    headers=auth_headers,
                    timeout=30,
                )

                if response.status_code == 404:
                    # New topic - no compatibility issues
                    new_topics.append(topic)
                    continue
                elif response.status_code == 200:
                    existing_topics.append(topic)
                    topic_data = response.json()

                    # Look for incompatible handlers
                    incompatible_handlers = [
                        h
                        for h in topic_data.get("handlers", [])
                        if not h.get("compatible", True)
                    ]

                    if incompatible_handlers:
                        # Get detailed incompatibility information
                        handler_details = []
                        for ih in incompatible_handlers:
                            ih_agent_name = ih.get("agent_name", "unknown")
                            ih_handler_name = ih.get("handler_name", "unknown")
                            differences = ih.get("differences", [])
                            handler_details.append(
                                f"{ih_agent_name}:{ih_handler_name} ({len(differences)} differences)"
                            )

                        compatibility_issues.append(
                            {
                                "topic": topic,
                                "handler": handler_name,
                                "issue": "Topic has existing incompatible handlers",
                                "details": f"{len(incompatible_handlers)} incompatible handler(s)",
                                "incompatible_handlers": handler_details,
                                "current_canonical_schema": topic_data.get(
                                    "canonical_schema", {}
                                ),
                                "proposed_input_schema": handler_info.get(
                                    "input_schema", {}
                                ),
                            }
                        )

            except requests.RequestException as e:
                logger.warning(f"Could not check topic '{topic}': {e}")
                continue

    # Show results
    if new_topics:
        logger.success(f"New topics (no conflicts): {', '.join(new_topics)}")

    if compatibility_issues:
        logger.error("Schema compatibility issues found:")
        for issue in compatibility_issues:
            topic_url = (
                f"{DISPATCH_API_BASE}/namespaces/{namespace}/topic/{issue['topic']}"
            )
            logger.error(f"  • Topic '{issue['topic']}': {issue['issue']}")
            logger.info(f"    Handler: {issue['handler']}")
            logger.info(f"    Details: {issue['details']}")
            logger.info(f"    View topic schema: {topic_url}")

            # Show more details if available
            if "incompatible_handlers" in issue:
                logger.info(
                    f"    Incompatible handlers: {', '.join(issue['incompatible_handlers'])}"
                )

            if "current_canonical_schema" in issue and "proposed_input_schema" in issue:
                logger.info(
                    f"    Current canonical schema keys: {list(issue['current_canonical_schema'].get('input_schema', {}).get('properties', {}).keys())}"
                )
                logger.info(
                    f"    Proposed input schema keys: {list(issue['proposed_input_schema'].get('properties', {}).keys())}"
                )
        return False
    else:
        if existing_topics:
            logger.success(
                f"Compatible with existing topics: {', '.join(existing_topics)}"
            )
        return True


def check_typed_payload_compliance(agent_path: str) -> bool:
    """Check if agent handlers use proper typed payloads by reading from .dispatch/schemas.json.

    Returns True if all handlers have proper type annotations.
    Returns False if any handlers lack proper typing.
    """
    import json

    logger = get_logger()
    try:
        # Read compliance issues from the local .dispatch directory
        schemas_path = os.path.join(agent_path, ".dispatch", "schemas.json")

        if not os.path.exists(schemas_path):
            logger.warning("No schemas.json found. Run 'dispatch agent build' first.")
            return True  # If we can't check, don't fail

        with open(schemas_path) as f:
            artifact = json.load(f)

        # Check if extraction was successful
        if not artifact.get("extraction_success", False):
            error_msg = artifact.get("error", {}).get("message", "Unknown error")
            logger.warning(f"Schema extraction failed during build: {error_msg}")
            return True

        # Get compliance issues from the artifact
        compliance_issues = artifact.get("compliance_issues", [])

        if compliance_issues:
            logger.error("Typed payload compliance issues found:")
            for issue in compliance_issues:
                logger.error(
                    f"  • Handler '{issue['handler']}' (topic: {issue['topic']}):"
                )
                for problem in issue["issues"]:
                    logger.error(f"    - {problem}")

            logger.warning("")
            logger.warning("Fix Required.")
            return False

        return True

    except Exception as e:
        logger.warning(f"Failed to check compliance from {agent_path}: {e}")
        return True


@agent_app.command("list-local")
def list_local():
    """List all locally running agents started with 'dispatch agent dev'.

    Shows agents tracked by the CLI, including their PID, port, and running status.
    Stale tracking entries (for processes that have exited) are marked as not running.
    """

    logger = get_logger()
    agents = get_tracked_agents()

    if not agents:
        logger.info("No local agents currently tracked.")
        logger.info("Start an agent with: dispatch agent dev")
        return

    console = Console()
    table = Table(title="Local Development Agents")
    table.add_column("Agent Name", style="cyan")
    table.add_column("PID", style="white")
    table.add_column("Port", style="white")
    table.add_column("Router", style="white")
    table.add_column("Status", style="white")
    table.add_column("Started", style="dim")

    for agent in agents:
        status = (
            "[green]Running[/green]" if agent.get("running") else "[red]Stopped[/red]"
        )
        started = agent.get("started_at", "")
        if started:
            # Parse ISO timestamp and format nicely
            try:
                dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
                started = dt.strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                pass

        table.add_row(
            agent.get("agent_name", "unknown"),
            str(agent.get("pid", "?")),
            str(agent.get("port", "?")),
            str(agent.get("router_port", "?")),
            status,
            started,
        )

    console.print(table)

    # Show count summary
    running_count = sum(1 for a in agents if a.get("running"))
    total_count = len(agents)
    logger.info(f"\n{running_count}/{total_count} agents running")


@agent_app.command("stop-local")
def stop_local(
    agent_name: Annotated[
        str | None,
        typer.Argument(
            help="Name of a specific agent to stop (omit to stop all local agents)"
        ),
    ] = None,
):
    """Stop locally running agents started with 'dispatch agent dev'.

    If an agent name is provided, stops only that agent.
    If no name is provided, stops all locally running agents.
    """
    logger = get_logger()

    if agent_name:
        # Stop a specific agent
        success, message = stop_local_agent_by_name(agent_name)
        if success:
            logger.success(message)
        else:
            logger.error(message)
            raise typer.Exit(1)
    else:
        # Stop all agents (default behavior)
        results = stop_all_local_agents()
        if not results:
            logger.info("No local agents to stop.")
            return

        success_count = sum(1 for _, success, _ in results if success)
        for name, success, message in results:
            if success:
                logger.success(message)
            else:
                logger.warning(message)

        logger.info(f"\nStopped {success_count}/{len(results)} agents")
