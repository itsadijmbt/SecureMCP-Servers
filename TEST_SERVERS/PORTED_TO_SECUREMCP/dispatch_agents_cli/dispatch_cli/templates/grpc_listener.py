import asyncio
import importlib.util
import logging
import os
import re
import sys
import threading
import time
from pathlib import Path

import httpx
import tomlkit
import yaml

# check if the /app folder exists for local development
if not os.path.exists("/app"):
    print("Warning: /app folder not found, assuming local development", flush=True)
    # Check if we're running from project root (dispatch.yaml exists in current dir)
    if os.path.exists("./dispatch.yaml"):
        root_path = "."
    else:
        # Fallback to parent directory (this shouldn't typically happen)
        root_path = ".."
else:
    root_path = "/app"

sys.path.append(root_path)

# Configure logging for container environments (ECS/CloudWatch) and local development
# Use stdout (ECS captures more reliably than stderr) and force=True to reconfigure
# This ensures all loggers (including those in handler code) output to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
    force=True,
)

# Ensure the root logger has a handler (for libraries that don't propagate)
root_logger = logging.getLogger()
if not root_logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    root_logger.addHandler(handler)

logger = logging.getLogger(__name__)

AGENT_NAME = None


# Read configuration from pyproject.toml / dispatch.yaml
def load_config():
    config: dict = {}
    pyproject = None
    pyproject_path = f"{root_path}/pyproject.toml"
    if os.path.exists(pyproject_path):
        with open(pyproject_path, "rb") as f:
            pyproject = tomlkit.load(f)
    yaml_path = os.path.join(root_path, "dispatch.yaml")
    if os.path.exists(yaml_path):
        try:
            with open(yaml_path, encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f) or {}
            if isinstance(yaml_data, dict):
                config.update(yaml_data)
            else:
                print(
                    f"Warning: {yaml_path} did not contain a mapping; ignoring its contents.",
                    flush=True,
                )
        except Exception as exc:
            print(f"Warning: Failed to parse {yaml_path}: {exc}", flush=True)

    dispatch_config = pyproject.get("tool", {}).get("dispatch", {}) if pyproject else {}
    if dispatch_config:
        for key, value in dispatch_config.items():
            config.setdefault(key, value)

    candidate_name = config.get("agent_name")
    if not candidate_name and pyproject:
        project_section = pyproject.get("project", {})
        candidate_name = project_section.get("name")
    if not candidate_name:
        candidate_name = os.path.basename(root_path)

    agent_name = re.sub(r"[^a-z0-9-]", "-", str(candidate_name).lower()).strip("-")
    agent_name = agent_name or "dispatch-agent"

    global AGENT_NAME
    AGENT_NAME = agent_name
    print(f"Agent name: {AGENT_NAME}", flush=True)

    config.setdefault("entrypoint", "agent.py")

    return config


config = load_config()
entrypoint_file = config.get("entrypoint", "agent.py")

# Point the SDK runtime config at the same dispatch.yaml we loaded
yaml_path = os.path.join(root_path, "dispatch.yaml")
os.environ.setdefault("DISPATCH_CONFIG_PATH", yaml_path)

# Backend configuration and agent identity
backend_base_url = os.getenv("BACKEND_URL", "http://dispatch.api:8000")
backend_url = f"{backend_base_url}/api/unstable"

# ── LLM Sidecar Proxy ──────────────────────────────────────────────────
# Start before user code imports so OPENAI_BASE_URL is set before any
# OpenAI/Anthropic SDK initialization.

_proxy_thread: threading.Thread | None = None


def _start_llm_proxy(agent_config: dict) -> None:
    """Start the LLM sidecar proxy and configure env vars."""
    global _proxy_thread

    if os.environ.get("DISPATCH_LLM_INSTRUMENT", "true").lower() == "false":
        print(
            "LLM instrumentation disabled (DISPATCH_LLM_INSTRUMENT=false)", flush=True
        )
        return

    proxy_port = int(os.environ.get("DISPATCH_LLM_PROXY_PORT", "8780"))
    proxy_url = f"http://127.0.0.1:{proxy_port}"

    # Start proxy in a daemon thread (avoids macOS multiprocessing spawn issues)
    def _run_proxy():
        from dispatch_agents.proxy.server import run_server

        run_server(port=proxy_port)

    _proxy_thread = threading.Thread(target=_run_proxy, daemon=True, name="llm-proxy")
    _proxy_thread.start()
    print(f"LLM sidecar proxy starting on {proxy_url}", flush=True)

    # Wait for proxy to be ready
    max_wait = 5.0
    start = time.monotonic()
    ready = False
    while time.monotonic() - start < max_wait:
        try:
            resp = httpx.get(f"{proxy_url}/health", timeout=0.5)
            if resp.status_code == 200:
                ready = True
                break
        except (httpx.ConnectError, httpx.TimeoutException):
            # Expected while proxy is starting up — keep polling
            time.sleep(0.1)
            continue
        time.sleep(0.1)

    if ready:
        print(f"LLM sidecar proxy ready ({time.monotonic() - start:.1f}s)", flush=True)
    else:
        print("Warning: LLM proxy not ready after 5s, continuing anyway", flush=True)

    # Set env vars so LLM SDKs route through the proxy.
    # The proxy forwards to the backend (/llm/inference) which handles
    # credentials, LLM routing, cost tracking, and telemetry.
    # We force-set these to ensure the proxy is used. Users who need direct
    # provider access can set DISPATCH_LLM_INSTRUMENT=false.
    os.environ["DISPATCH_LLM_PROXY_URL"] = proxy_url

    # Save original API keys before overriding — the proxy uses these as
    # fallback credentials when the backend has no LLM provider configured.
    for var in [
        "OPENAI_API_KEY",
        "OPENAI_BASE_URL",
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_BASE_URL",
    ]:
        original = os.environ.get(var)
        if original:
            os.environ[f"_DISPATCH_ORIGINAL_{var}"] = original

    for var, val in [
        ("OPENAI_BASE_URL", f"{proxy_url}/openai/v1"),
        ("OPENAI_API_KEY", "dispatch-proxy"),
        ("ANTHROPIC_BASE_URL", f"{proxy_url}/anthropic"),
        ("ANTHROPIC_API_KEY", "dispatch-proxy"),
    ]:
        existing = os.environ.get(var)
        if existing and existing != val:
            print(
                f"Info: routing {var} through Dispatch LLM proxy "
                f"(original key saved for fallback). "
                f"Set DISPATCH_LLM_INSTRUMENT=false to disable.",
                flush=True,
            )
        os.environ[var] = val

    # Set agent name for trace context
    if AGENT_NAME:
        os.environ.setdefault("DISPATCH_AGENT_NAME", AGENT_NAME)

    # Enable auto-instrumentation (patches httpx/requests for trace headers)
    from dispatch_agents.instrument import auto_instrument

    auto_instrument()


_start_llm_proxy(config)

# get the agent name from the pyproject.toml
print(f"Agent name: {AGENT_NAME}", flush=True)
# Import the entrypoint file to register event handlers
try:
    entrypoint_path = f"{root_path}/{entrypoint_file}"

    if os.path.exists(entrypoint_path):
        spec = importlib.util.spec_from_file_location(
            "entrypoint_module", entrypoint_path
        )
        if spec is None:
            raise ImportError(f"Cannot load module from {entrypoint_path}")
        entrypoint_module = importlib.util.module_from_spec(spec)
        sys.modules["entrypoint_module"] = entrypoint_module

        if spec.loader is None:
            raise ImportError(f"No loader available for {entrypoint_path}")
        spec.loader.exec_module(entrypoint_module)
        print(f"Successfully imported entrypoint: {entrypoint_file}", flush=True)

        # Import from dispatch_agents to verify registration
        from dispatch_agents.events import REGISTERED_HANDLERS, TOPIC_HANDLERS

        print(f"Registered handlers: {list(REGISTERED_HANDLERS.keys())}", flush=True)
        print(f"Topic triggers: {list(TOPIC_HANDLERS.keys())}", flush=True)
    else:
        print(f"Warning: Entrypoint file not found: {entrypoint_path}", flush=True)
        raise FileNotFoundError(f"Entrypoint file not found: {entrypoint_path}")

except Exception as e:
    print(f"Error importing entrypoint: {e}", flush=True)
    raise e


async def main(port=50051):
    """Start the gRPC server for the agent."""
    from dispatch_agents.grpc_server import serve

    logger.info(f"Starting gRPC server for agent '{AGENT_NAME}'...")

    # Note: The serve() function automatically subscribes the agent to
    # all registered topics with the backend on startup

    # Enable mTLS if DISPATCH_CERT_DIR is set (configured by ECS task definition)
    cert_dir = os.getenv("DISPATCH_CERT_DIR")
    if cert_dir is not None and not Path(cert_dir, "ca.crt").exists():
        logger.error(
            "DISPATCH_CERT_DIR=%s is set but ca.crt not found — refusing to "
            "start in insecure mode",
            cert_dir,
        )
        sys.exit(1)
    use_tls = cert_dir is not None

    try:
        await serve(
            agent_name=AGENT_NAME, port=port, insecure=not use_tls, cert_dir=cert_dir
        )
    except KeyboardInterrupt:
        logger.info("Shutting down gRPC server...")
    except Exception as e:
        logger.error(f"Error running gRPC server: {e}", exc_info=True)
        raise
    finally:
        # Proxy thread is a daemon — it exits when the main process exits
        if _proxy_thread and _proxy_thread.is_alive():
            logger.info("LLM sidecar proxy thread will exit with process")


if __name__ == "__main__":
    import sys

    port = 50051
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    asyncio.run(main(port))
