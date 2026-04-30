"""MCP server management commands."""

import json
import os
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import httpx
import tomlkit
import typer

from dispatch_cli.auth import handle_auth_error
from dispatch_cli.auth_provider import (
    CredentialResolver,
    MissingAuthenticationError,
    ResolvedCredential,
    StaticCredentialProvider,
    default_credential_provider,
)
from dispatch_cli.logger import get_logger
from dispatch_cli.mcp.agent.server import run_agent_server
from dispatch_cli.mcp.client import (
    OperatorBackendClient,
    default_operator_backend_client,
)
from dispatch_cli.mcp.config import MCPConfig
from dispatch_cli.mcp.operator.server import run_operator_server
from dispatch_cli.utils import load_dispatch_config

mcp_app = typer.Typer(name="mcp", help="MCP server management")
serve_app = typer.Typer(name="serve", help="Start MCP servers")
mcp_app.add_typer(serve_app)


class RegisterMode(StrEnum):
    """MCP client registration mode."""

    AUTO = "auto"
    CLAUDE = "claude"
    CURSOR = "cursor"
    CODEX = "codex"


def find_git_root() -> Path | None:
    """Find the root of the git repository."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_claude_code_config_paths() -> list[Path]:
    """Get Claude Code MCP config file paths (project-level only)."""
    git_root = find_git_root()
    if git_root:
        project_config = git_root / ".mcp.json"
    else:
        project_config = Path(".mcp.json")
    return [project_config]


def get_cursor_config_paths() -> list[Path]:
    """Get Cursor MCP config file paths (project-level only)."""
    git_root = find_git_root()
    if git_root:
        cursor_dir = git_root / ".cursor"
    else:
        cursor_dir = Path(".cursor")

    project_config = cursor_dir / "mcp.json"
    return [project_config] if cursor_dir.exists() else []


def get_codex_config_paths() -> list[Path]:
    """Get Codex MCP config file paths (project-level only)."""
    git_root = find_git_root()
    if git_root:
        codex_dir = git_root / ".codex"
    else:
        codex_dir = Path(".codex")

    config_path = codex_dir / "config.toml"
    return [config_path] if codex_dir.exists() else []


def find_mcp_config_files() -> list[tuple[str, Path]]:
    """Find all existing MCP config files.

    Returns list of (client_name, path) tuples.
    """
    configs = []

    # Check Claude Code config (project-level only)
    for claude_path in get_claude_code_config_paths():
        if claude_path.exists():
            configs.append(("claude", claude_path))

    # Check Cursor configs (project-level only)
    for cursor_path in get_cursor_config_paths():
        if cursor_path.exists():
            configs.append(("cursor", cursor_path))

    # Check Codex configs (project-level only)
    for codex_path in get_codex_config_paths():
        if codex_path.exists():
            configs.append(("codex", codex_path))

    return configs


def write_json_mcp_config(
    config_path: Path, server_name: str, server_config: dict
) -> None:
    """Write an MCP server entry to a JSON config file (Claude, Cursor)."""
    if config_path.exists():
        with open(config_path) as f:
            config_data = json.load(f)
    else:
        config_data = {}

    if "mcpServers" not in config_data:
        config_data["mcpServers"] = {}

    config_data["mcpServers"][server_name] = server_config

    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=2)
        f.write("\n")


def write_toml_mcp_config(
    config_path: Path, server_name: str, server_config: dict
) -> None:
    """Write an MCP server entry to a TOML config file (Codex)."""
    if config_path.exists():
        with open(config_path) as f:
            config_data = tomlkit.load(f)
    else:
        config_data = tomlkit.document()

    if "mcp_servers" not in config_data:
        config_data["mcp_servers"] = tomlkit.table(is_super_table=True)

    mcp_servers = config_data["mcp_servers"]
    if not isinstance(mcp_servers, dict):
        raise RuntimeError(f"Expected mcp_servers to be a table in {config_path}")
    mcp_servers[server_name] = server_config

    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w") as f:
        tomlkit.dump(config_data, f)


def update_mcp_config(
    client_name: str, config_path: Path, server_name: str, server_config: dict
) -> None:
    """Write an MCP server entry to the appropriate config file format."""
    if client_name == "codex":
        write_toml_mcp_config(config_path, server_name, server_config)
    else:
        write_json_mcp_config(config_path, server_name, server_config)


def build_registered_server_config(args: list[str]) -> dict[str, object]:
    """Build an MCP client config entry for launching the Dispatch CLI."""
    server_config: dict[str, object] = {
        "command": "dispatch",
        "args": args,
    }

    deploy_url = os.getenv("DISPATCH_DEPLOY_URL")
    if deploy_url:
        server_config["env"] = {"DISPATCH_DEPLOY_URL": deploy_url}

    return server_config


def require_mcp_credential_provider() -> CredentialResolver:
    """Resolve and validate auth up front for local MCP flows."""
    provider = default_credential_provider()
    credential = provider.resolve()
    verify_mcp_backend_auth(credential)
    return provider


def verify_mcp_backend_auth(credential: ResolvedCredential) -> None:
    """Verify that the resolved credential is accepted by the backend."""
    client: OperatorBackendClient = default_operator_backend_client(
        MCPConfig(credential_provider=StaticCredentialProvider(credential))
    )

    try:
        client.list_namespaces()
    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 401:
            handle_auth_error("Authentication could not be verified with the backend")

        detail = exc.response.text.strip()
        if detail:
            raise RuntimeError(
                f"Could not verify authentication with the Dispatch backend: {detail}"
            ) from exc

        raise RuntimeError(
            "Could not verify authentication with the Dispatch backend."
        ) from exc
    except httpx.HTTPError as exc:
        raise RuntimeError(
            "Could not verify authentication with the Dispatch backend."
        ) from exc
    finally:
        client.close()


@serve_app.command("agent")
def serve_agent(
    namespace: Annotated[
        str | None, typer.Option(help="Namespace (auto-discovered if not provided)")
    ] = None,
    agent: Annotated[
        str | None, typer.Option(help="Agent name (auto-discovered if not provided)")
    ] = None,
    experimental_tasks: Annotated[
        bool,
        typer.Option(
            help="Enable experimental task support for async agent function execution"
        ),
    ] = False,
    register: RegisterMode | None = typer.Option(
        None, help="Register MCP server in .mcp.json and exit"
    ),
):
    """Start MCP server for a specific Dispatch agent.

    The server exposes agent-specific functions as MCP tools that can be used
    by AI assistants like Claude Desktop.

    Examples:
        # Auto-discover namespace and agent from .dispatch.yaml
        dispatch mcp serve agent

        # Explicit namespace and agent
        dispatch mcp serve agent --namespace production --agent hello_world
    """
    try:
        # Try to auto-discover from dispatch.yaml if not provided
        if namespace is None or agent is None:
            try:
                dispatch_config = load_dispatch_config(".", apply_defaults=False)
                discovered_namespace = dispatch_config.get("namespace")
                discovered_agent = dispatch_config.get("agent_name")

                if namespace is None and discovered_namespace:
                    namespace = discovered_namespace
                    get_logger().info(f"Auto-discovered namespace: {namespace}")

                if agent is None and discovered_agent:
                    agent = discovered_agent
                    get_logger().info(f"Auto-discovered agent: {agent}")
            except Exception:
                # If auto-discovery fails, that's ok - we'll check for explicit flags below
                pass

        # Validate required parameters
        if not namespace:
            get_logger().error(
                "Namespace is required (provide --namespace or run from an agent directory with .dispatch.yaml)"
            )
            raise typer.Exit(1)

        if not agent:
            get_logger().error(
                "Agent name is required (provide --agent or run from an agent directory with .dispatch.yaml)"
            )
            raise typer.Exit(1)

        # Handle registration mode
        if register is not None:
            # Verify the user is authenticated before writing config
            get_logger().info("Authenticating...")
            require_mcp_credential_provider()
            get_logger().success("Authentication verified")

            # Determine which configs to update
            match register:
                case RegisterMode.CLAUDE:
                    claude_paths = get_claude_code_config_paths()
                    configs_to_update = [("claude", claude_paths[0])]
                case RegisterMode.CURSOR:
                    cursor_paths = get_cursor_config_paths()
                    if not cursor_paths:
                        get_logger().error("No .cursor directory found")
                        raise typer.Exit(1)
                    configs_to_update = [("cursor", cursor_paths[0])]
                case RegisterMode.CODEX:
                    codex_paths = get_codex_config_paths()
                    if not codex_paths:
                        # Explicit --register codex: create .codex/ dir
                        git_root = find_git_root()
                        base = git_root if git_root else Path(".")
                        codex_paths = [base / ".codex" / "config.toml"]
                    configs_to_update = [("codex", codex_paths[0])]
                case RegisterMode.AUTO:
                    configs_to_update = find_mcp_config_files()
                    if not configs_to_update:
                        get_logger().error("No MCP config files found")
                        raise typer.Exit(1)

            # Build server config
            server_config = build_registered_server_config(
                [
                    "mcp",
                    "serve",
                    "agent",
                    "--namespace",
                    namespace,
                    "--agent",
                    agent,
                ]
                + (["--experimental-tasks"] if experimental_tasks else [])
            )

            # Update configs
            for client_name, config_path in configs_to_update:
                if client_name == "codex":
                    server_name = f"dispatch_agent_{namespace}_{agent}"
                else:
                    server_name = f"dispatch-agent-{namespace}-{agent}"

                update_mcp_config(client_name, config_path, server_name, server_config)
                get_logger().success(f"Updated {client_name} config: {config_path}")

            get_logger().info("")
            get_logger().success("Agent MCP server registered")
            return

        credential_provider = require_mcp_credential_provider()

        # Create config for agent server
        config = MCPConfig(
            credential_provider=credential_provider,
            namespace=namespace,
            agent_name=agent,
            use_tasks=experimental_tasks,
            server_type="agent",
        )

        # Print startup info
        get_logger().info("Starting Dispatch Agent MCP Server")
        get_logger().info(f"  Namespace: {namespace}")
        get_logger().info(f"  Agent: {agent}")
        get_logger().info(f"  Backend: {config.api_base}")
        get_logger().info("")

        # Run agent server (blocking)
        # This will raise RuntimeError if agent can't be reached
        run_agent_server(config)

    except KeyboardInterrupt:
        get_logger().warning("\nShutting down MCP server...")
    except typer.Exit:
        raise
    except MissingAuthenticationError as e:
        get_logger().error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        get_logger().error(f"Error: {e}")
        raise typer.Exit(1)


@serve_app.command("operator")
def serve_operator(
    namespace: Annotated[
        str | None, typer.Option(help="Default namespace for operations")
    ] = None,
    register: RegisterMode | None = typer.Option(
        None, help="Register MCP server in .mcp.json and exit"
    ),
):
    """Start MCP server for Dispatch platform operations.

    The server exposes platform management tools for creating, deploying,
    and managing agents across namespaces.

    Examples:
        # Start operator server for examples namespace
        dispatch mcp serve operator --namespace examples
    """
    try:
        # Handle registration mode
        if register is not None:
            # Verify the user is authenticated before writing config
            get_logger().info("Authenticating...")
            require_mcp_credential_provider()
            get_logger().success("Authentication verified")

            # Determine which configs to update
            match register:
                case RegisterMode.CLAUDE:
                    claude_paths = get_claude_code_config_paths()
                    configs_to_update = [("claude", claude_paths[0])]
                case RegisterMode.CURSOR:
                    cursor_paths = get_cursor_config_paths()
                    if not cursor_paths:
                        get_logger().error("No .cursor directory found")
                        raise typer.Exit(1)
                    configs_to_update = [("cursor", cursor_paths[0])]
                case RegisterMode.CODEX:
                    codex_paths = get_codex_config_paths()
                    if not codex_paths:
                        # Explicit --register codex: create .codex/ dir
                        git_root = find_git_root()
                        base = git_root if git_root else Path(".")
                        codex_paths = [base / ".codex" / "config.toml"]
                    configs_to_update = [("codex", codex_paths[0])]
                case RegisterMode.AUTO:
                    configs_to_update = find_mcp_config_files()
                    if not configs_to_update:
                        get_logger().error("No MCP config files found")
                        raise typer.Exit(1)

            # Build server config
            args = ["mcp", "serve", "operator"]
            if namespace:
                args.extend(["--namespace", namespace])

            server_config = build_registered_server_config(args)

            # Update configs
            for client_name, config_path in configs_to_update:
                if client_name == "codex":
                    server_name = (
                        f"dispatch_operator_{namespace}"
                        if namespace
                        else "dispatch_operator"
                    )
                else:
                    server_name = (
                        f"dispatch-operator-{namespace}"
                        if namespace
                        else "dispatch-operator"
                    )

                update_mcp_config(client_name, config_path, server_name, server_config)
                get_logger().success(f"Updated {client_name} config: {config_path}")

            get_logger().info("")
            get_logger().success("Operator MCP server registered")
            return

        # Defer auth resolution for the operator server until a tool is invoked.
        # Static tool registration can complete without backend access, which lets
        # MCP clients finish startup and surface actionable auth errors on use
        # instead of reporting a generic handshake failure.
        credential_provider = default_credential_provider()

        # Create config for operator server
        config = MCPConfig(
            credential_provider=credential_provider,
            namespace=namespace,
            agent_name=None,
            use_tasks=False,  # Operator tools don't need tasks
            server_type="operator",
        )

        # Print startup info
        get_logger().info("Starting Dispatch Operator MCP Server")
        get_logger().info(f"  Namespace: {namespace}")
        get_logger().info(f"  Backend: {config.api_base}")
        get_logger().info("")

        # Run operator server (blocking)
        run_operator_server(config)

    except KeyboardInterrupt:
        get_logger().warning("\nShutting down MCP server...")
    except typer.Exit:
        raise
    except MissingAuthenticationError as e:
        get_logger().error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        get_logger().error(f"Error: {e}")
        raise typer.Exit(1)
