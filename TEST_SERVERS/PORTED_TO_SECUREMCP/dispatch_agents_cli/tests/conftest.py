"""Pytest configuration and fixtures for CLI tests."""

import threading
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime, timedelta
from typing import cast
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from dispatch_cli.auth_session import (
    AuthSessionStore,
    InvalidAuthSessionError,
    OAuthSession,
)
from dispatch_cli.keychain import KeychainClient
from dispatch_cli.logger import set_logger


@pytest.fixture(autouse=True)
def init_logger():
    """Initialize the logger before each test.

    The CLI logger is a global singleton that must be initialized
    before any utility functions can use it. This fixture ensures
    it's set up for every test automatically.
    """
    set_logger(verbose=False)
    yield


@pytest.fixture(autouse=True)
def disable_version_check():
    """Avoid network/version side effects in CLI command tests."""
    with patch("dispatch_cli.main.check_and_notify_cli_update"):
        yield


@pytest.fixture
def runner() -> CliRunner:
    """Provide a shared CLI runner for command tests."""
    return CliRunner()


def _future_timestamp(minutes: int = 30) -> str:
    return (datetime.now(UTC) + timedelta(minutes=minutes)).isoformat()


def _past_timestamp(minutes: int = 30) -> str:
    return (datetime.now(UTC) - timedelta(minutes=minutes)).isoformat()


def _session(**overrides: str | None) -> OAuthSession:
    payload: dict[str, str | None] = {
        "access_token": "oauth-access-token",
        "refresh_token": "oauth-refresh-token",
        "expires_at": _future_timestamp(),
        "user_email": "user@example.com",
        "org_id": "org_123",
        "org_display_name": "Example Org",
    }
    payload.update(overrides)
    return OAuthSession(
        access_token=cast(str, payload["access_token"]),
        refresh_token=cast(str, payload["refresh_token"]),
        expires_at=cast(str, payload["expires_at"]),
        user_email=payload["user_email"],
        org_id=payload["org_id"],
        org_display_name=payload["org_display_name"],
    )


class MemoryKeychainClient:
    """In-memory KeychainClient for use in tests."""

    def __init__(self):
        self._values: dict[tuple[str, str], str] = {}

    def get_generic_password(self, service: str, account: str) -> str | None:
        return self._values.get((service, account))

    def set_generic_password(self, service: str, account: str, password: str) -> None:
        self._values[(service, account)] = password

    def delete_generic_password(self, service: str, account: str) -> bool:
        return self._values.pop((service, account), None) is not None


def _memory_keychain() -> KeychainClient:
    return MemoryKeychainClient()


class MemoryAuthSessionStore:
    """In-memory AuthSessionStore for use in tests."""

    def __init__(
        self,
        session: OAuthSession | None = None,
        *,
        fail_load: bool = False,
    ):
        self._session = session
        self._fail_load = fail_load
        self._lock = threading.RLock()

    @contextmanager
    def locked(self) -> Iterator[None]:
        with self._lock:
            yield

    def load(self) -> OAuthSession | None:
        with self.locked():
            return self.load_locked()

    def load_locked(self) -> OAuthSession | None:
        if self._fail_load:
            raise InvalidAuthSessionError(
                "Stored OAuth session is invalid. Run `dispatch login`."
            )
        return self._session

    def save(self, session: OAuthSession) -> None:
        with self.locked():
            self.save_locked(session)

    def save_locked(self, session: OAuthSession) -> None:
        self._session = session
        self._fail_load = False

    def clear(self) -> None:
        with self.locked():
            self.clear_locked()

    def clear_locked(self) -> None:
        self._session = None
        self._fail_load = False


def _memory_store(
    session: OAuthSession | None = None,
    *,
    fail_load: bool = False,
) -> AuthSessionStore:
    return MemoryAuthSessionStore(session, fail_load=fail_load)
