"""Dispatch CLI main entry point."""

from importlib.metadata import version as _version

import typer

from .auth_login import default_login_flow
from .auth_provider import MissingAuthenticationError, default_credential_provider
from .auth_session import (
    InvalidAuthSessionError,
    default_auth_session_store,
)
from .commands.agent import agent_app
from .commands.llm import llm_app
from .commands.mcp import mcp_app
from .commands.registry import registry_app
from .commands.router import router_app
from .commands.secrets import secrets_app
from .commands.skills import skills_app
from .utils import DISPATCH_API_BASE
from .version_check import check_and_notify_cli_update

app = typer.Typer(no_args_is_help=True)
app.add_typer(agent_app)
app.add_typer(llm_app)
app.add_typer(mcp_app)
app.add_typer(registry_app)
app.add_typer(router_app)
app.add_typer(secrets_app)
app.add_typer(skills_app)

__version__ = _version("dispatch-cli")


@app.callback()
def main_callback(
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output (show debug messages)",
    ),
):
    """Run before every command to check for CLI updates.

    This checks for updates once per day (cached) and notifies users
    if a newer version is available.
    """
    # Initialize global logger with verbosity setting
    from .logger import set_logger

    set_logger(verbose=verbose)

    # Check for CLI updates
    check_and_notify_cli_update(DISPATCH_API_BASE)


@app.command()
def version():
    """Show dispatch CLI version and optionally check for updates."""
    from .logger import get_logger
    from .version_check import get_sdk_version_requirements

    logger = get_logger()
    current = __version__
    logger.info(f"Dispatch CLI Version: {current}")

    # Force a version check
    version_data = get_sdk_version_requirements(DISPATCH_API_BASE)
    if version_data:
        from packaging.version import Version

        try:
            latest = version_data["cli_current"]
            current_ver = Version(current)
            latest_ver = Version(latest)

            if latest_ver > current_ver:
                logger.warning(f"A newer version is available: {latest}")
                logger.info("Run 'dispatch update-cli' to see the update command")
            elif latest_ver == current_ver:
                logger.success("You are on the latest version!")
            else:
                logger.debug(f"You are running a pre-release version ({current})")
        except (KeyError, ValueError):
            logger.warning("Could not check for updates")
    else:
        logger.warning("Could not check for updates (backend unreachable)")


@app.command()
def login(
    org: str | None = typer.Option(
        None, "--org", help="Organization ID to use for browser auth"
    ),
):
    """Authenticate the CLI in the browser."""
    from .logger import get_logger

    logger = get_logger()

    try:
        session_store = default_auth_session_store()
        login_flow = default_login_flow()
        with logger.status_context("Starting browser auth..."):
            session = login_flow.login(org_id=org)
        session_store.save(session)
    except Exception as exc:
        logger.error(f"Login failed: {exc}")
        raise typer.Exit(1) from exc

    logger.success("Logged in with browser auth")
    if session.user_email:
        logger.info(f"User: {session.user_email}")
    if session.org_display_name and session.org_id:
        logger.info(f"Organization: {session.org_display_name} ({session.org_id})")
    elif session.org_id:
        logger.info(f"Organization: {session.org_id}")


@app.command()
def logout():
    """Clear the locally stored OAuth session."""
    from .logger import get_logger

    logger = get_logger()
    try:
        session_store = default_auth_session_store()
    except InvalidAuthSessionError as exc:
        logger.error(str(exc))
        raise typer.Exit(1) from exc

    try:
        existing_session = session_store.load()
    except InvalidAuthSessionError:
        session_store.clear()
        logger.success("Cleared invalid local OAuth session")
        return

    if existing_session is None:
        logger.info("No local OAuth session found")
        return

    session_store.clear()
    logger.success("Logged out")


@app.command()
def whoami():
    """Show the current CLI authentication context."""
    from .logger import get_logger

    logger = get_logger()

    try:
        provider = default_credential_provider()
        credential = provider.resolve()
    except InvalidAuthSessionError as exc:
        logger.warning(str(exc))
        return
    except MissingAuthenticationError as exc:
        logger.warning(str(exc))
        return

    logger.info(f"Auth mode: {credential.auth_mode}")
    if credential.auth_mode == "api_key":
        logger.info("Identity: machine auth override via DISPATCH_API_KEY")
        return

    if credential.user_email:
        logger.info(f"User: {credential.user_email}")
    if credential.org_display_name and credential.org_id:
        logger.info(
            f"Organization: {credential.org_display_name} ({credential.org_id})"
        )
    elif credential.org_id:
        logger.info(f"Organization: {credential.org_id}")

    try:
        session = default_auth_session_store().load()
        if session:
            logger.info(f"Session expires: {session.expires_at}")
    except InvalidAuthSessionError as exc:
        logger.debug(f"Could not load session expiry details: {exc}")
    except Exception as exc:
        logger.debug(f"Could not load session expiry details: {exc}")


@app.command()
def update_cli():
    """Show the command to update the CLI to the latest version."""
    from .logger import get_logger

    logger = get_logger()
    current = __version__
    logger.info(f"Current CLI version: {current}\n")

    logger.code(
        "uv tool install git+ssh://git@github.com/datadog-labs/dispatch_agents_cli.git --upgrade",
        language="bash",
        title="To install the latest stable version:",
    )


if __name__ == "__main__":
    app()
