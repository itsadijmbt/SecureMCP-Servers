"""HTTP client utilities with version headers for dispatch CLI."""

import os
from typing import Any

import requests

from .version import get_cli_version

# Client identifier for API requests
DISPATCH_CLIENT_NAME = "cli"


def get_api_headers(bearer_token: str | None = None) -> dict[str, str]:
    """Get HTTP headers including authentication and version information.

    Args:
        bearer_token: Optional bearer credential for authorization

    Returns:
        Dict of HTTP headers with version info and optionally authorization
    """
    headers = {
        "x-dispatch-client": DISPATCH_CLIENT_NAME,
        "x-dispatch-client-version": get_cli_version(),
        "x-dispatch-client-commit": os.getenv("GIT_COMMIT", "unknown")[:8],
    }

    if bearer_token:
        headers["Authorization"] = f"Bearer {bearer_token}"

    return headers


def request_json(
    method: str,
    url: str,
    *,
    auth_headers: dict[str, str] | None = None,
    timeout: int = 30,
    **kwargs: Any,
) -> dict:
    """Make an authenticated JSON request and return the parsed response body.

    Raises requests.exceptions.HTTPError on non-2xx responses.
    """
    from .auth import get_auth_headers

    response = requests.request(
        method,
        url,
        headers=auth_headers if auth_headers is not None else get_auth_headers(),
        timeout=timeout,
        **kwargs,
    )
    response.raise_for_status()
    return response.json()
