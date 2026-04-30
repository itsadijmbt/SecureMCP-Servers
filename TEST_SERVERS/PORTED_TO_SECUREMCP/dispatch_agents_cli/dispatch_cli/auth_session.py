"""Local OAuth session persistence for the Dispatch CLI."""

from __future__ import annotations

import json
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol

from .keychain import KeychainClient, KeychainError, default_keychain_client

AUTH_SESSION_KEYCHAIN_SERVICE = "dispatch-cli-oauth"
AUTH_SESSION_KEYCHAIN_ACCOUNT = "default"


@dataclass(slots=True)
class OAuthSession:
    """Persisted OAuth session for human CLI usage."""

    access_token: str
    refresh_token: str
    expires_at: str
    user_email: str | None = None
    org_id: str | None = None
    org_display_name: str | None = None
    _expires_at_utc: datetime = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        self._expires_at_utc = _parse_session_expiry(self.expires_at)

    def is_expired(self, now: datetime | None = None) -> bool:
        """Return whether the access token is expired."""
        current_time = now or datetime.now(UTC)
        return self._expires_at_utc <= current_time


class InvalidAuthSessionError(RuntimeError):
    """Raised when the stored OAuth session cannot be read or persisted."""


def _parse_session_expiry(expires_at: str) -> datetime:
    """Parse persisted expiry data once when the session is constructed."""
    try:
        parsed = datetime.fromisoformat(expires_at)
    except ValueError as exc:
        raise ValueError(f"Invalid expires_at format: {expires_at!r}") from exc

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=UTC)
    return parsed


class AuthSessionStore(Protocol):
    """Storage interface for persisted OAuth sessions."""

    @contextmanager
    def locked(self) -> Iterator[None]:
        """Serialize access to the session store."""

    def load(self) -> OAuthSession | None:
        """Load the stored session if present."""

    def load_locked(self) -> OAuthSession | None:
        """Load the stored session while already holding the session lock."""

    def save(self, session: OAuthSession) -> None:
        """Persist the current session."""

    def save_locked(self, session: OAuthSession) -> None:
        """Persist the current session while already holding the session lock."""

    def clear(self) -> None:
        """Delete any stored session."""

    def clear_locked(self) -> None:
        """Delete any stored session while already holding the session lock."""


class KeychainAuthSessionStore:
    """System secure-store-backed OAuth session store."""

    def __init__(
        self,
        keychain: KeychainClient,
        service: str = AUTH_SESSION_KEYCHAIN_SERVICE,
        account: str = AUTH_SESSION_KEYCHAIN_ACCOUNT,
    ) -> None:
        self.keychain: KeychainClient = keychain
        self.service: str = service
        self.account: str = account
        self._thread_lock = threading.RLock()

    @contextmanager
    def locked(self) -> Iterator[None]:
        """Serialize access to the keychain-backed session store."""
        with self._thread_lock:
            yield

    def load(self) -> OAuthSession | None:
        """Load the stored session if present."""
        with self.locked():
            return self.load_locked()

    def load_locked(self) -> OAuthSession | None:
        """Load the stored session while already holding the session lock."""
        try:
            payload_text = self.keychain.get_generic_password(
                self.service,
                self.account,
            )
        except KeychainError as exc:
            raise InvalidAuthSessionError(
                "Stored OAuth session is invalid. Run `dispatch login`."
            ) from exc

        if payload_text is None:
            return None

        try:
            payload = json.loads(payload_text)
            return OAuthSession(**payload)
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            raise InvalidAuthSessionError(
                "Stored OAuth session is invalid. Run `dispatch login`."
            ) from exc

    def save(self, session: OAuthSession) -> None:
        """Persist the current session to keychain."""
        with self.locked():
            self.save_locked(session)

    def save_locked(self, session: OAuthSession) -> None:
        """Persist the current session while already holding the session lock."""
        payload = json.dumps(
            {
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
                "expires_at": session.expires_at,
                "user_email": session.user_email,
                "org_id": session.org_id,
                "org_display_name": session.org_display_name,
            },
            separators=(",", ":"),
        )
        try:
            self.keychain.set_generic_password(
                self.service,
                self.account,
                payload,
            )
        except KeychainError as exc:
            raise InvalidAuthSessionError(
                "Failed to persist the local OAuth session."
            ) from exc

    def clear(self) -> None:
        """Delete any stored session."""
        with self.locked():
            self.clear_locked()

    def clear_locked(self) -> None:
        """Delete any stored session while already holding the session lock."""
        try:
            self.keychain.delete_generic_password(self.service, self.account)
        except KeychainError as exc:
            raise InvalidAuthSessionError(
                "Failed to clear the local OAuth session."
            ) from exc


def default_auth_session_store() -> AuthSessionStore:
    """Build the default OAuth session store for the current platform."""
    try:
        return KeychainAuthSessionStore(keychain=default_keychain_client())
    except KeychainError as exc:
        raise InvalidAuthSessionError(
            "Local OAuth session storage requires a system secure store. "
            "On Linux, install libsecret-tools (e.g. `apt install libsecret-tools`) "
            "and ensure a keyring daemon (GNOME Keyring or KWallet) is running."
        ) from exc
