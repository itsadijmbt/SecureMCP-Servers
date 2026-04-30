"""Authentication compatibility helpers for authenticated CLI commands."""

from __future__ import annotations

import os
from typing import NoReturn

import typer

from dispatch_cli.logger import get_logger

from .auth_provider import MissingAuthenticationError, default_credential_provider
from .auth_session import InvalidAuthSessionError, default_auth_session_store
from .http_client import get_api_headers


def get_bearer_token() -> str:
    """Return the current bearer token for protected CLI commands."""
    try:
        return default_credential_provider().resolve().access_token
    except (MissingAuthenticationError, InvalidAuthSessionError) as exc:
        get_logger().error(str(exc))
        raise typer.Exit(1) from exc


def get_auth_headers() -> dict[str, str]:
    """Return API headers for protected CLI commands."""
    return get_api_headers(get_bearer_token())


def handle_auth_error(error_message: str = "") -> NoReturn:
    """Handle an authentication failure without prompting for new credentials."""
    logger = get_logger()
    if error_message:
        logger.error(f"Authentication failed: {error_message}")
    else:
        logger.error("Authentication failed.")

    if os.getenv("DISPATCH_API_KEY"):
        logger.info(
            "The current process is using `DISPATCH_API_KEY`. "
            "Update or unset it, then retry."
        )
    else:
        try:
            default_auth_session_store().clear()
            logger.info("Your local OAuth session was cleared.")
        except InvalidAuthSessionError:
            logger.info("Could not clear the local OAuth session.")
        logger.info("Run `dispatch login` to authenticate again.")

    raise typer.Exit(1)
