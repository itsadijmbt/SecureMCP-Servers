"""OAuth login flow orchestration for Dispatch CLI commands."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
import threading
import webbrowser
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Protocol
from urllib.parse import parse_qs, urlencode, urlparse

import questionary
import requests
from pydantic import BaseModel, ValidationError, field_validator

from .auth_session import OAuthSession
from .logger import get_logger
from .utils import DISPATCH_API_BASE

DEFAULT_AUTH_CALLBACK_HOST = "127.0.0.1"
DEFAULT_AUTH_CALLBACK_PORT = 8765
# Auth0 requires exact callback URL matching (no dynamic-port support), so we register a
# small set of fixed ports and try them in order. 8766 is the fallback for hung sessions.
DEFAULT_AUTH_CALLBACK_FALLBACK_PORT = 8766


class AuthClientConfig(BaseModel):
    """Configuration for the CLI auth client."""

    domain: str
    client_id: str
    audience: str
    scope: str = "openid profile email offline_access"


class AuthOrganization(BaseModel):
    """Organization available to the current authenticated user."""

    id: str
    name: str
    display_name: str


class AuthUserContext(BaseModel):
    """User and organization context resolved after login."""

    user_email: str | None = None
    org_id: str | None = None
    org_display_name: str | None = None


class _AuthUserProfileResponse(BaseModel):
    email: str | None = None
    username: str | None = None
    org_id: str | None = None
    org_display_name: str | None = None


class _AuthRuntimeConfigResponse(BaseModel):
    auth_domain: str
    auth_api_audience: str
    auth_cli_client_id: str


class LoginFlow(Protocol):
    """Perform an interactive OAuth login flow."""

    def login(self, org_id: str | None = None) -> OAuthSession: ...


class _CallbackListener(Protocol):
    """Receive a single OAuth callback over a local transport."""

    redirect_uri: str

    def wait_for_result(self, timeout_seconds: int) -> _CallbackResult:
        """Wait for the OAuth callback payload."""

    def close(self) -> None:
        """Release listener resources."""


class _CallbackListenerFactory(Protocol):
    """Build a callback listener for the browser login flow."""

    def __call__(self, *, host: str, port: int) -> _CallbackListener: ...


@dataclass(slots=True)
class _CallbackResult:
    code: str | None = None
    state: str | None = None
    error: str | None = None
    error_description: str | None = None


class _LoopbackCallbackListener:
    """Capture a single auth callback on a loopback port."""

    def __init__(
        self,
        host: str = DEFAULT_AUTH_CALLBACK_HOST,
        port: int = DEFAULT_AUTH_CALLBACK_PORT,
    ):
        self._event = threading.Event()
        self._response_written = threading.Event()
        self._result = _CallbackResult()

        outer = self

        class CallbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                parsed = urlparse(self.path)
                if parsed.path != "/callback":
                    self.send_response(404)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(b"Not Found")
                    return

                params = parse_qs(parsed.query)
                outer._result = _CallbackResult(
                    code=_first_value(params, "code"),
                    state=_first_value(params, "state"),
                    error=_first_value(params, "error"),
                    error_description=_first_value(params, "error_description"),
                )
                outer._event.set()

                is_error = outer._result.error is not None
                self.send_response(400 if is_error else 200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(_callback_page(is_error).encode("utf-8"))
                outer._response_written.set()

            def log_message(self, format, *args):  # noqa: A003
                return

        class _ReuseAddrServer(HTTPServer):
            allow_reuse_address = True

        self._server = _ReuseAddrServer((host, port), CallbackHandler)
        self.redirect_uri = f"http://{host}:{self._server.server_port}/callback"
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def wait_for_result(self, timeout_seconds: int) -> _CallbackResult:
        """Wait for the callback to arrive."""
        if not self._event.wait(timeout_seconds):
            raise RuntimeError("Timed out waiting for auth callback.")
        return self._result

    def close(self) -> None:
        """Stop the loopback server."""
        self._response_written.wait(timeout=2)
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=1)


class BrowserLoginFlow:
    """Browser-based auth login flow for the CLI."""

    def __init__(
        self,
        config: AuthClientConfig,
        api_base: str = DISPATCH_API_BASE,
        browser_opener=webbrowser.open,
        http_session: requests.Session | None = None,
        callback_host: str = DEFAULT_AUTH_CALLBACK_HOST,
        callback_port: int = DEFAULT_AUTH_CALLBACK_PORT,
        callback_fallback_port: int = DEFAULT_AUTH_CALLBACK_FALLBACK_PORT,
        callback_listener_factory: _CallbackListenerFactory | None = None,
        status_reporter: Callable[[str], None] | None = None,
        timeout_seconds: int = 300,
    ):
        self.config = config
        self.api_base = _normalize_api_base(api_base)
        self.browser_opener = browser_opener
        self.http_session = http_session or requests.Session()
        self.callback_host = callback_host
        self.callback_port = callback_port
        self.callback_fallback_port = callback_fallback_port
        self.callback_listener_factory = (
            callback_listener_factory or create_loopback_callback_listener
        )
        self.status_reporter = status_reporter
        self.timeout_seconds = timeout_seconds

    def login(self, org_id: str | None = None) -> OAuthSession:
        """Run the login flow and return a persisted OAuth session."""
        session = self._authorize(org_id=org_id)
        user_context = self._fetch_user_context(session.access_token)
        if user_context is not None:
            return self._enrich_session(session, user_context)

        if org_id is not None:
            raise RuntimeError("Login completed without organization context.")

        organizations = self._fetch_organizations(session.access_token)
        if not organizations:
            raise RuntimeError("Your account does not belong to any organizations.")

        selected_org = (
            organizations[0].id
            if len(organizations) == 1
            else self._select_organization(organizations)
        )

        self._report_status(
            "Opening browser again to complete login with organization context..."
        )
        session = self._authorize(org_id=selected_org)
        user_context = self._fetch_user_context(session.access_token)
        if user_context is None:
            raise RuntimeError("Failed to resolve organization context after login.")
        return self._enrich_session(session, user_context)

    def _authorize(self, org_id: str | None = None) -> OAuthSession:
        """Run the PKCE browser flow and exchange the callback for tokens."""
        state = secrets.token_urlsafe(24)
        code_verifier = secrets.token_urlsafe(48)
        code_challenge = _pkce_challenge(code_verifier)

        try:
            callback_listener = self.callback_listener_factory(
                host=self.callback_host,
                port=self.callback_port,
            )
        except OSError:
            try:
                callback_listener = self.callback_listener_factory(
                    host=self.callback_host,
                    port=self.callback_fallback_port,
                )
            except OSError as exc:
                raise RuntimeError(
                    f"Could not start the auth callback listener on "
                    f"{self.callback_host}:{self.callback_port} or "
                    f"{self.callback_host}:{self.callback_fallback_port}. "
                    "Both ports appear to be in use. Close any in-progress "
                    "`dispatch login` sessions and retry."
                ) from exc
        try:
            auth_url = self._authorization_url(
                redirect_uri=callback_listener.redirect_uri,
                state=state,
                code_challenge=code_challenge,
                org_id=org_id,
            )
            if not self.browser_opener(auth_url):
                raise RuntimeError(
                    "Could not open the browser for login. "
                    "Use DISPATCH_API_KEY for non-interactive environments."
                )

            callback = callback_listener.wait_for_result(self.timeout_seconds)
        finally:
            callback_listener.close()

        code = _validate_callback_result(callback, expected_state=state)

        return self._exchange_code_for_tokens(
            code=code,
            code_verifier=code_verifier,
            redirect_uri=callback_listener.redirect_uri,
        )

    def _authorization_url(
        self,
        *,
        redirect_uri: str,
        state: str,
        code_challenge: str,
        org_id: str | None,
    ) -> str:
        params: dict[str, str] = {
            "response_type": "code",
            "client_id": self.config.client_id,
            "redirect_uri": redirect_uri,
            "scope": self.config.scope,
            "audience": self.config.audience,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        if org_id:
            params["organization"] = org_id
        return f"https://{self.config.domain}/authorize?{urlencode(params)}"

    def _exchange_code_for_tokens(
        self,
        *,
        code: str,
        code_verifier: str,
        redirect_uri: str,
    ) -> OAuthSession:
        response = self.http_session.post(
            f"https://{self.config.domain}/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": self.config.client_id,
                "code": code,
                "code_verifier": code_verifier,
                "redirect_uri": redirect_uri,
            },
            timeout=30,
        )
        return _oauth_session_from_token_payload(
            _json_or_error(response),
            require_refresh_token=True,
        )

    def _fetch_user_context(self, access_token: str) -> AuthUserContext | None:
        response = self.http_session.get(
            f"{self.api_base}/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30,
        )
        if response.status_code == 200:
            try:
                payload = _AuthUserProfileResponse.model_validate(
                    _json_or_error(response)
                )
            except ValidationError as exc:
                raise RuntimeError("Auth user context response was invalid.") from exc
            return AuthUserContext(
                user_email=payload.email or payload.username,
                org_id=payload.org_id,
                org_display_name=payload.org_display_name,
            )

        detail = _response_detail(response)
        if response.status_code == 400 and (
            "Organization selection required" in detail
            or "Organization context required" in detail
        ):
            return None
        raise RuntimeError(detail)

    def _fetch_organizations(self, access_token: str) -> list[AuthOrganization]:
        response = self.http_session.get(
            f"{self.api_base}/auth/my-organizations",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=30,
        )
        payload = _json_or_error(response)
        if not isinstance(payload, list):
            raise RuntimeError("Auth organization response was invalid.")
        try:
            return [AuthOrganization.model_validate(item) for item in payload]
        except ValidationError as exc:
            raise RuntimeError("Auth organization response was invalid.") from exc

    def _select_organization(self, organizations: list[AuthOrganization]) -> str:
        choices = [
            questionary.Choice(
                title=f"{organization.display_name} ({organization.id})",
                value=organization.id,
            )
            for organization in organizations
        ]
        selected = questionary.select(
            "Select the organization to use for this CLI session:",
            choices=choices,
        ).ask()
        if not selected:
            raise RuntimeError("Organization selection was cancelled.")
        return selected

    def _enrich_session(
        self,
        session: OAuthSession,
        user_context: AuthUserContext,
    ) -> OAuthSession:
        return OAuthSession(
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            expires_at=session.expires_at,
            user_email=user_context.user_email,
            org_id=user_context.org_id,
            org_display_name=user_context.org_display_name,
        )

    def _report_status(self, message: str) -> None:
        if self.status_reporter is not None:
            self.status_reporter(message)


def default_auth_client_config() -> AuthClientConfig:
    """Return the default Auth client config for CLI auth flows."""
    domain = os.getenv("DISPATCH_AUTH_DOMAIN")
    client_id = os.getenv("DISPATCH_AUTH_CLIENT_ID")
    audience = os.getenv("DISPATCH_AUTH_AUDIENCE")

    if domain or client_id or audience:
        if not domain or not client_id:
            raise RuntimeError(
                "Incomplete auth CLI override. Set both DISPATCH_AUTH_DOMAIN "
                "and DISPATCH_AUTH_CLIENT_ID."
            )
        return AuthClientConfig(
            domain=domain,
            client_id=client_id,
            audience=audience or DISPATCH_API_BASE,
        )

    api_base = _normalize_api_base(DISPATCH_API_BASE)
    try:
        response = requests.get(
            f"{api_base}/api/unstable/config",
            timeout=5,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            "Could not load auth CLI configuration from the Dispatch backend. "
            "Set DISPATCH_AUTH_DOMAIN and DISPATCH_AUTH_CLIENT_ID to override."
        ) from exc

    payload = _json_or_error(response)
    if not isinstance(payload, dict):
        raise RuntimeError("Auth CLI configuration response was invalid.")

    try:
        config = _AuthRuntimeConfigResponse.model_validate(payload)
    except ValidationError as exc:
        raise RuntimeError("Auth CLI configuration response was incomplete.") from exc
    return AuthClientConfig(
        domain=config.auth_domain,
        client_id=config.auth_cli_client_id,
        audience=config.auth_api_audience,
    )


def default_login_flow() -> LoginFlow:
    """Return the default login flow implementation."""
    return BrowserLoginFlow(
        default_auth_client_config(),
        status_reporter=_default_status_reporter(),
    )


def create_loopback_callback_listener(*, host: str, port: int) -> _CallbackListener:
    """Build the default local callback listener for browser login."""
    return _LoopbackCallbackListener(host=host, port=port)


def refresh_auth_session(
    session: OAuthSession,
    *,
    config: AuthClientConfig | None = None,
    http_session: requests.Session | None = None,
) -> OAuthSession:
    """Refresh an expired OAuth session using auth refresh tokens."""
    auth_config = config or default_auth_client_config()
    client = http_session or requests.Session()
    response = client.post(
        f"https://{auth_config.domain}/oauth/token",
        data={
            "grant_type": "refresh_token",
            "client_id": auth_config.client_id,
            "refresh_token": session.refresh_token,
        },
        timeout=30,
    )
    refreshed = _oauth_session_from_token_payload(_json_or_error(response))
    return OAuthSession(
        access_token=refreshed.access_token,
        refresh_token=refreshed.refresh_token or session.refresh_token,
        expires_at=refreshed.expires_at,
        user_email=session.user_email,
        org_id=session.org_id,
        org_display_name=session.org_display_name,
    )


def _callback_page(is_error: bool) -> str:
    title = "Dispatch login failed" if is_error else "Dispatch login complete"
    body = (
        "You can close this window and return to the CLI."
        if not is_error
        else "Return to the CLI to see the error details."
    )
    return (
        "<html><head><title>"
        f"{title}"
        "</title></head><body><h1>"
        f"{title}"
        "</h1><p>"
        f"{body}"
        "</p></body></html>"
    )


def _first_value(params: dict[str, list[str]], key: str) -> str | None:
    values = params.get(key)
    return values[0] if values else None


def _validate_callback_result(
    callback: _CallbackResult,
    *,
    expected_state: str,
) -> str:
    if callback.error is not None:
        message = callback.error_description or callback.error
        raise RuntimeError(f"Auth login failed: {message}")
    if callback.code is None or not hmac.compare_digest(
        callback.state or "", expected_state
    ):
        raise RuntimeError("Invalid auth callback received.")
    return callback.code


def _default_status_reporter() -> Callable[[str], None] | None:
    return get_logger().status


def _pkce_challenge(code_verifier: str) -> str:
    digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


def _normalize_api_base(api_base: str) -> str:
    normalized = api_base.rstrip("/")
    suffix = "/api/unstable"
    if normalized.endswith(suffix):
        return normalized[: -len(suffix)]
    return normalized


class _TokenPayload(BaseModel):
    access_token: str
    refresh_token: str | None = None
    expires_in: int = 3600

    @field_validator("access_token")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v:
            raise ValueError("must not be empty")
        return v


def _oauth_session_from_token_payload(
    payload: dict[str, Any],
    *,
    require_refresh_token: bool = False,
) -> OAuthSession:
    try:
        token = _TokenPayload.model_validate(payload)
    except ValidationError as exc:
        raise RuntimeError("Auth token response was invalid.") from exc
    if require_refresh_token and not token.refresh_token:
        raise RuntimeError("Auth token response did not include a refresh token.")
    expires_at = datetime.now(UTC) + timedelta(seconds=token.expires_in)
    return OAuthSession(
        access_token=token.access_token,
        refresh_token=token.refresh_token or "",
        expires_at=expires_at.isoformat(),
    )


def _json_or_error(response: requests.Response):
    if response.ok:
        return response.json()
    raise RuntimeError(_response_detail(response))


def _response_detail(response: requests.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return f"Request failed with status {response.status_code}."

    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
        error = payload.get("error_description") or payload.get("error")
        if isinstance(error, str):
            return error
    return f"Request failed with status {response.status_code}."
