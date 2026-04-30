"""Secret management commands."""

import os
import sys
from typing import Annotated

import questionary
import requests
import typer
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Table

from dispatch_cli.auth import get_auth_headers, handle_auth_error
from dispatch_cli.http_client import request_json
from dispatch_cli.logger import get_logger
from dispatch_cli.secrets import (
    add_secret as add_local_secret,
)
from dispatch_cli.secrets import (
    list_secrets as list_local_secrets,
)
from dispatch_cli.secrets import (
    remove_secret as remove_local_secret,
)
from dispatch_cli.utils import (
    DISPATCH_API_BASE,
    load_dispatch_config,
    validate_dispatch_project,
)

from .agent import build_namespaced_url

_NAMESPACE_REQUIRED_MESSAGE = (
    "Namespace is required. "
    "Configure it in dispatch.yaml, set DISPATCH_NAMESPACE environment variable, or provide via --namespace option."
)


def get_namespace_from_config(
    namespace: str | None, path: str = ".", verify: bool = False
) -> tuple[str, str]:
    """Resolve namespace from env, CLI arg, or config file. Returns (namespace, source)."""
    env_namespace = os.environ.get("DISPATCH_NAMESPACE")
    if env_namespace:
        resolved_namespace = env_namespace
        source = "env"
    elif namespace:
        resolved_namespace = namespace
        source = "cli"
    else:
        logger = get_logger()
        try:
            config = load_dispatch_config(path)
            config_namespace = config.get("namespace")
            if config_namespace:
                resolved_namespace = config_namespace
                source = "yaml"
            else:
                logger.error(_NAMESPACE_REQUIRED_MESSAGE)
                raise typer.Exit(1)
        except typer.Exit:
            raise
        except Exception:
            logger.error(_NAMESPACE_REQUIRED_MESSAGE)
            raise typer.Exit(1)

    if verify and resolved_namespace != "default":
        auth_headers = get_auth_headers()
        try:
            result = request_json(
                "GET",
                f"{DISPATCH_API_BASE}/api/unstable/namespaces/list",
                auth_headers=auth_headers,
            )
            available_namespaces = result.get("namespaces", [])

            if resolved_namespace not in available_namespaces:
                logger = get_logger()
                logger.error(f"Namespace '{resolved_namespace}' does not exist.")
                if available_namespaces:
                    logger.info("[bold]Available namespaces:[/bold]")
                    for ns in sorted(available_namespaces):
                        logger.info(f"  • {ns}")
                else:
                    logger.warning(
                        "No namespaces available. Contact your org admin to create one."
                    )
                raise typer.Exit(1)
        except requests.exceptions.RequestException as e:
            logger = get_logger()
            logger.warning(f"Could not verify namespace exists: {e}")
            # Continue anyway - don't block operations if API is unavailable

    return resolved_namespace, source


_NAMESPACE_SOURCE_DISPLAY = {
    "env": "environment variable DISPATCH_NAMESPACE",
    "yaml": "dispatch.yaml",
    "cli": "command line argument",
}

secrets_app = typer.Typer(
    name="secret",
    help="Manage secrets",
    rich_markup_mode="markdown",
)


@secrets_app.command("manage")
def manage_secrets(
    path: Annotated[str, typer.Option()] = ".",
    upload: Annotated[
        bool, typer.Option("--upload", help="Upload secrets to remote server")
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", help="Force overwrite existing secrets without asking"),
    ] = False,
):
    """Manage agent secrets from .env file."""
    abs_path = os.path.abspath(path)
    if not validate_dispatch_project(abs_path):
        raise typer.Exit(1)

    config = load_dispatch_config(abs_path)
    namespace, namespace_source = get_namespace_from_config(None, abs_path, verify=True)

    # Show namespace information to user
    logger = get_logger()
    logger.info(
        f"Using namespace: [bold]{namespace}[/bold] [dim](from {_NAMESPACE_SOURCE_DISPLAY[namespace_source]})[/dim]"
    )

    secrets_config = config.get("secrets", [])

    if not secrets_config:
        logger.warning("No secrets configured in dispatch.yaml")
        logger.info("Add secrets configuration to dispatch.yaml like:")
        logger.code(
            """secrets:
    - name: OPENAI_API_KEY
      secret_id: shared/openai-api-key""",
            "yaml",
            title="Example secrets config",
        )
        return

    env_file_path = os.path.join(abs_path, ".env")

    # Create .env file if it doesn't exist
    if not os.path.exists(env_file_path):
        logger.warning(f"No .env file found at {env_file_path}")
        create_env = typer.confirm("Create .env file with secret placeholders?")
        if create_env:
            with open(env_file_path, "w") as f:
                f.write("# Environment variables for secrets\n")
                f.write(
                    "# Replace placeholder values with real secrets before uploading\n\n"
                )
                for secret in secrets_config:
                    name = secret["name"]
                    f.write(f"{name}=your_{name.lower()}_here\n")
            logger.success(f"Created {env_file_path} with placeholders")
            logger.warning(
                "Please edit the file and replace placeholders with real values"
            )
        return

    # Read .env file
    env_vars = {}
    try:
        with open(env_file_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        logger.error(f"Failed to read .env file: {e}")
        raise typer.Exit(1)

    # Check remote status if uploading
    remote_status = {}
    if upload:
        logger.debug("Checking remote secrets status...")
        auth_headers = get_auth_headers()

        # Get list of secret_ids to check
        secret_ids = [secret["secret_id"] for secret in secrets_config]

        try:
            check_result = request_json(
                "POST",
                build_namespaced_url("/secrets/check", namespace),
                auth_headers=auth_headers,
                json={"secret_paths": secret_ids},
            )
            for secret_status in check_result["secrets"]:
                remote_status[secret_status["secret_path"]] = secret_status["exists"]
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                handle_auth_error("Invalid or expired API key")
            else:
                logger.warning(f"Could not check remote secrets: {e}")
        except Exception as e:
            logger.warning(f"Could not check remote secrets: {e}")

    logger.info("Found secrets configuration:")
    for secret in secrets_config:
        name = secret["name"]
        secret_id = secret["secret_id"]
        has_value = (
            name in env_vars
            and env_vars[name]
            and not env_vars[name].startswith("your_")
        )
        local_status = "[green]✓[/green]" if has_value else "[red]✗[/red]"

        remote_exists = remote_status.get(secret_id, False)
        remote_status_text = (
            "[cyan](exists remotely)[/cyan]"
            if remote_exists
            else "[dim](not saved remote)[/dim]"
        )

        logger.info(f"  {local_status} {name} → {secret_id} {remote_status_text}")

    if not upload:
        logger.info("\nAvailable commands:")
        logger.info("  --upload                Upload secrets to remote server")
        logger.info(
            "  --upload --force        Upload and overwrite all secrets without asking"
        )
        return

    # Prepare secrets to upload (filter and confirm)
    logger.debug("Preparing secrets for upload...")
    auth_headers = get_auth_headers()

    secrets_to_upload = []
    for secret in secrets_config:
        name = secret["name"]
        secret_id = secret["secret_id"]

        if (
            name not in env_vars
            or not env_vars[name]
            or env_vars[name].startswith("your_")
        ):
            logger.warning(f"Skipping {name} - no value in .env file")
            continue

        # Check if secret exists remotely and ask for confirmation (unless forced)
        remote_exists = remote_status.get(secret_id, False)
        if force:
            secrets_to_upload.append((name, secret_id, env_vars[name], remote_exists))
        elif remote_exists:
            logger.warning(f"OVERWRITE {name} → {secret_id} (already exists remotely)")
            if typer.confirm("Continue?"):
                secrets_to_upload.append(
                    (name, secret_id, env_vars[name], remote_exists)
                )
            else:
                logger.warning(f"Skipped {name}")
        else:
            if typer.confirm(f"Upload {name} → {secret_id}?"):
                secrets_to_upload.append(
                    (name, secret_id, env_vars[name], remote_exists)
                )
            else:
                logger.warning(f"Skipped {name}")

    if not secrets_to_upload:
        logger.warning("No secrets to upload")
        logger.info(
            f"[link={DISPATCH_API_BASE}/secrets]View/update secrets in the Dispatch Agents secrets UI[/link]"
        )
        return

    # Upload with progress bar
    logger.info(f"Uploading {len(secrets_to_upload)} secret(s)...")

    def upload_secret_value(name: str, secret_id: str, value: str) -> bool:
        """Upload a single secret and return whether it succeeded."""
        try:
            request_json(
                "POST",
                build_namespaced_url("/secrets/upload", namespace),
                auth_headers=auth_headers,
                json={"secret_path": secret_id, "secret_value": value},
            )
            return True
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                handle_auth_error("Invalid or expired API key")
            return False
        except Exception:
            return False

    # Use Rich progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task("Uploading secrets...", total=len(secrets_to_upload))

        success_count = 0
        for name, secret_id, value, remote_exists in secrets_to_upload:
            progress.update(task, description=f"Uploading {name}...")

            success = upload_secret_value(name, secret_id, value)
            if success:
                action = "Overwritten" if remote_exists else "Uploaded"
                logger.success(f"{name} {action.lower()} successfully")
                success_count += 1
            else:
                logger.error(f"Failed to upload {name}")

            progress.advance(task)

    logger.success(
        f"Successfully uploaded {success_count}/{len(secrets_to_upload)} secrets"
    )
    logger.info(
        f"[link={DISPATCH_API_BASE}/secrets]View/update secrets in the Dispatch Agents secrets UI[/link]"
    )


@secrets_app.command("upload")
def upload_secret(
    secret_path: Annotated[
        str, typer.Argument(help="Secret path (e.g., 'shared/openai-api-key')")
    ],
    secret_value: Annotated[str, typer.Argument(help="Secret value")],
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace for the secret (defaults to dispatch.yaml config)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
):
    """Upload a secret to remote storage."""
    logger = get_logger()
    namespace, namespace_source = get_namespace_from_config(namespace, verify=True)

    # Show namespace information to user
    logger.info(
        f"Using namespace: [bold]{namespace}[/bold] [dim](from {_NAMESPACE_SOURCE_DISPLAY[namespace_source]})[/dim]"
    )
    logger.debug(f"Uploading secret: {secret_path}")

    # Get the current bearer credential for authentication
    auth_headers = get_auth_headers()

    try:
        with logger.status_context("Uploading secret..."):
            result = request_json(
                "POST",
                build_namespaced_url("/secrets/upload", namespace),
                auth_headers=auth_headers,
                json={
                    "namespace": namespace,
                    "secret_path": secret_path,
                    "secret_value": secret_value,
                },
            )
        if result.get("success"):
            logger.success(result.get("message", "Secret uploaded successfully"))
        else:
            logger.error(f"Failed to upload secret: {result}")
            raise typer.Exit(1)

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            handle_auth_error("Invalid or expired credential")
        else:
            logger.error(f"HTTP Error: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Failed to upload secret: {e}")
        raise typer.Exit(1)


@secrets_app.command("list")
def list_secrets(
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace to list secrets from (defaults to dispatch.yaml config)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
):
    """List all secrets for your namespace."""
    logger = get_logger()
    namespace, namespace_source = get_namespace_from_config(namespace, verify=True)

    # Show namespace information to user
    logger.info(
        f"Using namespace: [bold]{namespace}[/bold] [dim](from {_NAMESPACE_SOURCE_DISPLAY[namespace_source]})[/dim]"
    )

    # Get the current bearer credential for authentication
    auth_headers = get_auth_headers()

    try:
        with logger.status_context("Fetching secrets..."):
            result = request_json(
                "GET",
                build_namespaced_url("/secrets/list", namespace),
                auth_headers=auth_headers,
                params={"namespace": namespace},
            )
        secrets = result.get("secrets", [])

        if not secrets:
            logger.info("No secrets found for your organization")
        else:
            logger.info("Secrets for your organization:")
            for secret in secrets:
                secret_path = secret.get("secret_path", "unknown")
                logger.info(f"  • {secret_path}")
            logger.info(f"\nTotal: {len(secrets)} secret(s)")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            handle_auth_error("Invalid or expired credential")
        else:
            logger.error(f"HTTP Error: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Failed to list secrets: {e}")
        raise typer.Exit(1)


@secrets_app.command("check")
def check_secrets(
    secret_paths: Annotated[list[str], typer.Argument(help="Secret paths to check")],
    namespace: Annotated[
        str | None,
        typer.Option(
            help="Namespace to check secrets in (defaults to dispatch.yaml config)",
            envvar="DISPATCH_NAMESPACE",
        ),
    ] = None,
):
    """Check if secrets exist without revealing their values."""
    logger = get_logger()
    namespace, namespace_source = get_namespace_from_config(namespace, verify=True)

    # Show namespace information to user
    logger.info(
        f"Using namespace: [bold]{namespace}[/bold] [dim](from {_NAMESPACE_SOURCE_DISPLAY[namespace_source]})[/dim]"
    )

    if not secret_paths:
        logger.warning("No secret paths provided")
        return

    logger.debug(f"Checking {len(secret_paths)} secret(s)...")

    auth_headers = get_auth_headers()

    try:
        with logger.status_context("Checking secrets..."):
            result = request_json(
                "POST",
                build_namespaced_url("/secrets/check", namespace),
                auth_headers=auth_headers,
                json={"secret_paths": secret_paths},
            )
        secrets_status = result.get("secrets", [])

        found_count = 0
        for secret_status in secrets_status:
            secret_path = secret_status.get("secret_path", "unknown")
            exists = secret_status.get("exists", False)
            error = secret_status.get("error")

            if error:
                logger.error(f"{secret_path}: {error}")
            elif exists:
                logger.success(f"{secret_path}: Found")
                found_count += 1
            else:
                logger.error(f"{secret_path}: Not found")

        logger.info(f"\nResult: {found_count}/{len(secret_paths)} secrets found")

        if found_count < len(secret_paths):
            logger.warning("To upload missing secrets use:")
            logger.code("dispatch secret upload <secret_path> <secret_value>", "bash")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            handle_auth_error("Invalid or expired credential")
        else:
            logger.error(f"HTTP Error: {e}")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Failed to check secrets: {e}")
        raise typer.Exit(1)


# =============================================================================
# Local Secrets Management (for local development mode)
# =============================================================================

local_app = typer.Typer(
    name="local",
    help="Manage local secrets for development mode (stored in ~/.dispatch/secrets.yaml)",
    rich_markup_mode="markdown",
)
secrets_app.add_typer(local_app)


@local_app.command("add")
def local_add_secret(
    name: Annotated[
        str,
        typer.Argument(
            help="Secret name (e.g., 'OPENAI_API_KEY' or '/shared/db-password')"
        ),
    ],
    value: Annotated[
        str | None,
        typer.Option(
            "--value",
            "-v",
            help="Secret value (if not provided, will prompt securely)",
        ),
    ] = None,
    no_keychain: Annotated[
        bool,
        typer.Option(
            "--no-keychain",
            help="Store as raw text instead of in the system secure store (not recommended)",
        ),
    ] = False,
):
    """Add or update a local secret for development mode.

    By default, secrets are stored in the system secure store with a reference
    in ~/.dispatch/secrets.yaml. Use --no-keychain to store as raw text (warns on access).

    Examples:
        dispatch secret local add OPENAI_API_KEY
        dispatch secret local add ANTHROPIC_API_KEY --value sk-ant-...
        dispatch secret local add /shared/db-password --no-keychain
    """
    logger = get_logger()

    # Prompt for value if not provided
    if value is None:
        if sys.stdin.isatty():
            value = questionary.password(f"Enter value for {name}:").ask()
        else:
            logger.error(
                "No value provided. Use --value or run interactively to be prompted."
            )
            raise typer.Exit(1)

    if not value:
        logger.error("Secret value cannot be empty")
        raise typer.Exit(1)

    # Use the native secure store on supported platforms.
    use_keychain = not no_keychain
    if (
        use_keychain
        and sys.platform != "darwin"
        and not sys.platform.startswith("linux")
    ):
        logger.warning(
            "The system secure store is only supported on macOS and Linux. Storing as raw value instead."
        )
        use_keychain = False

    success = add_local_secret(name, value, use_keychain=use_keychain)
    if not success:
        raise typer.Exit(1)


@local_app.command("list")
def local_list_secrets():
    """List all locally configured secrets for development mode.

    Shows secrets stored in ~/.dispatch/secrets.yaml, their storage type
    (keychain or raw), and whether they are properly configured.
    """
    logger = get_logger()
    secrets = list_local_secrets()

    if not secrets:
        logger.info("No local secrets configured.")
        logger.info("\nTo add a secret:")
        logger.code("dispatch secret local add OPENAI_API_KEY", "bash")
        return

    # Create a rich table for nice output
    table = Table(title="Local Secrets (~/.dispatch/secrets.yaml)")
    table.add_column("Name", style="cyan")
    table.add_column("Storage", style="magenta")
    table.add_column("Status", style="green")

    for secret in secrets:
        name = secret["name"]
        storage = secret["storage"]
        configured = secret["configured"]

        storage_display = "🔐 Secure store" if storage == "keychain" else "📝 Raw text"
        status = "✓ Configured" if configured else "✗ Missing"
        status_style = "green" if configured else "red"

        table.add_row(
            name, storage_display, f"[{status_style}]{status}[/{status_style}]"
        )

    logger.console.print(table)
    logger.info(f"\nTotal: {len(secrets)} secret(s)")

    # Check for raw secrets and warn
    raw_secrets = [s for s in secrets if s["storage"] == "raw"]
    if raw_secrets:
        logger.warning(
            f"\n⚠️  {len(raw_secrets)} secret(s) stored as raw text. "
            "Consider migrating to the secure store for better security:"
        )
        for secret in raw_secrets:
            logger.info(f"    dispatch secret local add {secret['name']}")


@local_app.command("remove")
def local_remove_secret(
    name: Annotated[
        str,
        typer.Argument(help="Secret name to remove"),
    ],
):
    """Remove a local secret from development mode storage.

    Removes the secret from ~/.dispatch/secrets.yaml and from the system secure store
    if it was stored there.
    """
    success = remove_local_secret(name)
    if not success:
        raise typer.Exit(1)
