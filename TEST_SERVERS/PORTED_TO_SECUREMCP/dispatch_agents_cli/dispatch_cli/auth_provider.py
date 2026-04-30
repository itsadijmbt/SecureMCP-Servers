"""Credential resolution for Dispatch CLI auth consumers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal, Protocol

from .auth_login import refresh_auth_session
from .auth_session import (
    AuthSessionStore,
    InvalidAuthSessionError,
    OAuthSession,
    default_auth_session_store,
)
from .logger import get_logger


class MissingAuthenticationError(RuntimeError):
    """Raised when the CLI has no usable authentication state."""


class CredentialResolver(Protocol):
    """Resolve the current process credential."""

    def resolve(self) -> ResolvedCredential: ...


class RefreshSession(Protocol):
    """Refresh an expired OAuth session."""

    def __call__(self, session: OAuthSession) -> OAuthSession: ...


AuthMode = Literal["api_key", "oauth"]
API_KEY_PREFIX = "dak_"


# Keep the resolved credential as a small slotted record so auth state stays
# explicit and callers cannot tack on ad hoc attributes.
@dataclass(slots=True)
class ResolvedCredential:
    """Credential resolved for the current CLI process."""

    auth_mode: AuthMode
    access_token: str
    user_email: str | None = None
    org_id: str | None = None
    org_display_name: str | None = None

    @property
    def authorization_header(self) -> str:
        """Return the bearer authorization header value."""
        return f"Bearer {self.access_token}"


class StaticCredentialProvider:
    """Return a fixed credential for the current process."""

    def __init__(self, credential: ResolvedCredential):
        self.credential = credential

    def resolve(self) -> ResolvedCredential:
        return self.credential


class CredentialProvider:
    """Resolve the current process credential from env or local session."""

    def __init__(
        self,
        store: AuthSessionStore,
        refresh_session: RefreshSession | None = None,
    ):
        self.store = store
        self.refresh_session = refresh_session

    def resolve(self) -> ResolvedCredential:
        """Resolve the credential for the current process."""
        api_key = os.getenv("DISPATCH_API_KEY")
        if api_key:
            if not api_key.startswith(API_KEY_PREFIX):
                raise MissingAuthenticationError(
                    "DISPATCH_API_KEY must be a Dispatch API key starting with "
                    "`dak_`. Unset it or replace it with a real API key."
                )
            return ResolvedCredential(auth_mode="api_key", access_token=api_key)

        with self.store.locked():
            try:
                session = self.store.load_locked()
            except InvalidAuthSessionError as exc:
                # Clear inside the lock to avoid a race with concurrent callers.
                try:
                    self.store.clear_locked()
                except InvalidAuthSessionError as clear_exc:
                    get_logger().debug(
                        f"Could not clear invalid stored OAuth session: {clear_exc}"
                    )
                raise MissingAuthenticationError(
                    "Stored OAuth session is invalid. Run `dispatch login`."
                ) from exc

            if session is None:
                raise MissingAuthenticationError(
                    "Authentication required. Run `dispatch login`."
                )

            if session.is_expired():
                session = self._refresh_locked(session)

            return ResolvedCredential(
                auth_mode="oauth",
                access_token=session.access_token,
                user_email=session.user_email,
                org_id=session.org_id,
                org_display_name=session.org_display_name,
            )

    def _refresh_locked(self, session: OAuthSession) -> OAuthSession:
        """Refresh an expired session or clear unusable local state."""
        if self.refresh_session is None:
            self.store.clear_locked()
            raise MissingAuthenticationError(
                "Authentication expired. Run `dispatch login`."
            )

        try:
            refreshed = self.refresh_session(session)
        except Exception as exc:
            self.store.clear_locked()
            raise MissingAuthenticationError(
                "Authentication expired. Run `dispatch login`."
            ) from exc

        self.store.save_locked(refreshed)
        return refreshed


def default_credential_provider() -> CredentialProvider:
    """Build the default credential provider for CLI processes."""
    return CredentialProvider(
        store=default_auth_session_store(),
        refresh_session=refresh_auth_session,
    )
