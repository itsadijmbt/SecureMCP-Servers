"""Tests for CLI auth session storage and credential resolution."""

from __future__ import annotations

import os
import threading
from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest
from conftest import (
    MemoryKeychainClient,
    _future_timestamp,
    _memory_keychain,
    _memory_store,
    _past_timestamp,
    _session,
)

from dispatch_cli.auth_login import refresh_auth_session
from dispatch_cli.auth_provider import (
    CredentialProvider,
    MissingAuthenticationError,
    default_credential_provider,
)
from dispatch_cli.auth_session import (
    AUTH_SESSION_KEYCHAIN_ACCOUNT,
    AUTH_SESSION_KEYCHAIN_SERVICE,
    InvalidAuthSessionError,
    KeychainAuthSessionStore,
    OAuthSession,
    default_auth_session_store,
)
from dispatch_cli.keychain import (
    KeychainError,
    SecretToolKeychainClient,
    SecurityKeychainClient,
)


class TestAuthSessionStore:
    def test_oauth_session_rejects_invalid_expiry_at_construction(self):
        with pytest.raises(ValueError, match="Invalid expires_at format"):
            OAuthSession(
                access_token="oauth-access-token",
                refresh_token="oauth-refresh-token",
                expires_at="not-a-timestamp",
            )

    def test_oauth_session_treats_naive_expiry_as_utc(self):
        session = OAuthSession(
            access_token="oauth-access-token",
            refresh_token="oauth-refresh-token",
            expires_at="2099-01-01T00:00:00",
        )

        assert (
            session.is_expired(now=datetime(2098, 12, 31, 23, 59, tzinfo=UTC)) is False
        )
        assert session.is_expired(now=datetime(2099, 1, 1, 0, 0, tzinfo=UTC)) is True

    def test_oauth_session_is_expired_at_exact_expiry_moment(self):
        # Catches off-by-one: `< now` would let a token live one moment too long.
        session = OAuthSession(
            access_token="oauth-access-token",
            refresh_token="oauth-refresh-token",
            expires_at="2099-06-15T12:00:00Z",
        )
        expiry = datetime(2099, 6, 15, 12, 0, 0, tzinfo=UTC)
        assert session.is_expired(now=expiry) is True
        assert (
            session.is_expired(
                now=datetime(2099, 6, 15, 11, 59, 59, 999999, tzinfo=UTC)
            )
            is False
        )

    def test_default_auth_session_store_uses_macos_client(self):
        with patch("dispatch_cli.keychain.sys.platform", "darwin"):
            store = default_auth_session_store()

        assert isinstance(store, KeychainAuthSessionStore)
        assert isinstance(store.keychain, SecurityKeychainClient)

    def test_default_auth_session_store_uses_linux_client(self):
        with patch("dispatch_cli.keychain.sys.platform", "linux"):
            store = default_auth_session_store()

        assert isinstance(store, KeychainAuthSessionStore)
        assert isinstance(store.keychain, SecretToolKeychainClient)

    def test_default_auth_session_store_injects_factory_result(self):
        keychain = _memory_keychain()

        with patch(
            "dispatch_cli.auth_session.default_keychain_client",
            return_value=keychain,
        ):
            store = default_auth_session_store()

        assert store.keychain is keychain

    def test_default_auth_session_store_errors_on_unsupported_platform(self):
        with patch(
            "dispatch_cli.auth_session.default_keychain_client",
            side_effect=KeychainError("unsupported"),
        ):
            with pytest.raises(
                InvalidAuthSessionError,
                match="Local OAuth session storage requires a system secure store.",
            ):
                default_auth_session_store()

    def test_keychain_store_save_load_and_clear_round_trip(self):
        store = KeychainAuthSessionStore(keychain=_memory_keychain())
        session = _session()

        assert store.load() is None

        store.save(session)

        loaded = store.load()
        assert loaded == session

        store.clear()
        assert store.load() is None

    def test_keychain_store_uses_default_service_and_account(self):
        keychain = MemoryKeychainClient()
        store = KeychainAuthSessionStore(keychain=keychain)

        store.save(_session())

        assert (
            keychain.get_generic_password(
                AUTH_SESSION_KEYCHAIN_SERVICE,
                AUTH_SESSION_KEYCHAIN_ACCOUNT,
            )
            is not None
        )


class TestCredentialProvider:
    def test_default_credential_provider_uses_default_session_store(self):
        store = _memory_store()

        with patch(
            "dispatch_cli.auth_provider.default_auth_session_store",
            return_value=store,
        ):
            provider = default_credential_provider()

        assert provider.store is store

    def test_default_credential_provider_wires_default_refresh_session(self):
        store = _memory_store()

        with patch(
            "dispatch_cli.auth_provider.default_auth_session_store",
            return_value=store,
        ):
            provider = default_credential_provider()

        assert provider.refresh_session is refresh_auth_session

    def test_uses_explicit_api_key_env_over_stored_oauth(self):
        store = _memory_store(_session())
        provider = CredentialProvider(store=store)

        with patch.dict(
            "os.environ", {"DISPATCH_API_KEY": "dak_test_123"}, clear=False
        ):
            credential = provider.resolve()

        assert credential.auth_mode == "api_key"
        assert credential.access_token == "dak_test_123"
        assert credential.user_email is None
        assert credential.org_id is None

    def test_rejects_non_api_key_dispatch_api_key_override(self):
        store = _memory_store(_session())
        provider = CredentialProvider(store=store)

        with patch.dict(
            "os.environ", {"DISPATCH_API_KEY": "oauth-access-token"}, clear=False
        ):
            with pytest.raises(MissingAuthenticationError) as excinfo:
                provider.resolve()

        assert "DISPATCH_API_KEY must be a Dispatch API key" in str(excinfo.value)
        assert store.load() is not None

    def test_uses_stored_oauth_session_when_env_absent(self):
        store = _memory_store(_session())
        provider = CredentialProvider(store=store)

        with patch.dict("os.environ", {}, clear=True):
            credential = provider.resolve()

        assert credential.auth_mode == "oauth"
        assert credential.access_token == "oauth-access-token"
        assert credential.user_email == "user@example.com"
        assert credential.org_id == "org_123"
        assert credential.authorization_header == "Bearer oauth-access-token"

    def test_refreshes_expired_oauth_session_and_persists_result(self):
        expired = _session(expires_at=_past_timestamp())
        refreshed = _session(
            access_token="oauth-access-token-refreshed",
            refresh_token="oauth-refresh-token-refreshed",
            expires_at=_future_timestamp(60),
        )
        store = _memory_store(expired)
        refresh_session = Mock(return_value=refreshed)
        provider = CredentialProvider(store=store, refresh_session=refresh_session)

        with patch.dict("os.environ", {}, clear=True):
            credential = provider.resolve()

        refresh_session.assert_called_once_with(expired)
        assert credential.auth_mode == "oauth"
        assert credential.access_token == "oauth-access-token-refreshed"
        assert store.load() == refreshed

    def test_clears_session_and_errors_when_refresh_fails(self):
        store = _memory_store(_session(expires_at=_past_timestamp()))
        provider = CredentialProvider(
            store=store,
            refresh_session=Mock(side_effect=RuntimeError("refresh failed")),
        )

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(MissingAuthenticationError) as excinfo:
                provider.resolve()

        assert "dispatch login" in str(excinfo.value)
        assert store.load() is None

    def test_clears_invalid_session_and_errors_when_session_is_unreadable(self):
        store = _memory_store(fail_load=True)
        provider = CredentialProvider(store=store)

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(MissingAuthenticationError) as excinfo:
                provider.resolve()

        assert "Stored OAuth session is invalid" in str(excinfo.value)
        assert store.load() is None

    def test_logs_when_invalid_session_cannot_be_cleared(self):
        class FailingClearStore:
            def locked(self):
                return _memory_store().locked()

            def load_locked(self):
                raise InvalidAuthSessionError(
                    "Stored OAuth session is invalid. Run `dispatch login`."
                )

            def clear_locked(self):
                raise InvalidAuthSessionError("keychain unavailable")

        logger = Mock()
        provider = CredentialProvider(store=FailingClearStore())

        with (
            patch.dict("os.environ", {}, clear=True),
            patch("dispatch_cli.auth_provider.get_logger", return_value=logger),
            pytest.raises(MissingAuthenticationError) as excinfo,
        ):
            provider.resolve()

        assert "Stored OAuth session is invalid" in str(excinfo.value)
        logger.debug.assert_called_once()

    def test_errors_when_no_authentication_is_available(self):
        provider = CredentialProvider(store=_memory_store())

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(MissingAuthenticationError) as excinfo:
                provider.resolve()

        assert "dispatch login" in str(excinfo.value)

    def test_clears_expired_session_and_errors_when_no_refresh_callback(self):
        # Catches condition-flip: flipping the `refresh_session is None` check
        # would skip clearing the session or skip raising the error.
        store = _memory_store(_session(expires_at=_past_timestamp()))
        provider = CredentialProvider(store=store, refresh_session=None)

        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(MissingAuthenticationError) as excinfo:
                provider.resolve()

        assert "dispatch login" in str(excinfo.value)
        assert store.load() is None

    def test_default_provider_refreshes_expired_oauth_session(self):
        expired = _session(expires_at=_past_timestamp())
        refreshed = _session(
            access_token="oauth-access-token-refreshed",
            refresh_token="oauth-refresh-token-refreshed",
            expires_at=_future_timestamp(60),
        )
        store = _memory_store(expired)

        with (
            patch(
                "dispatch_cli.auth_provider.default_auth_session_store",
                return_value=store,
            ),
            patch(
                "dispatch_cli.auth_provider.refresh_auth_session",
                return_value=refreshed,
            ) as refresh_session,
            patch.dict("os.environ", {}, clear=True),
        ):
            credential = default_credential_provider().resolve()

        refresh_session.assert_called_once_with(expired)
        assert credential.access_token == "oauth-access-token-refreshed"
        assert store.load() == refreshed

    def test_concurrent_resolve_refreshes_session_once(self):
        expired = _session(expires_at=_past_timestamp())
        refreshed = _session(
            access_token="oauth-access-token-refreshed",
            refresh_token="oauth-refresh-token-refreshed",
            expires_at=_future_timestamp(60),
        )
        store = _memory_store(expired)

        refresh_calls = 0
        refresh_calls_lock = threading.Lock()
        refresh_started = threading.Event()
        release_refresh = threading.Event()

        def refresh_session(session: OAuthSession) -> OAuthSession:
            nonlocal refresh_calls
            with refresh_calls_lock:
                refresh_calls += 1
            refresh_started.set()
            release_refresh.wait(timeout=1)
            return refreshed

        provider = CredentialProvider(store=store, refresh_session=refresh_session)
        results: list[str] = []

        def resolve_token() -> None:
            results.append(provider.resolve().access_token)

        getenv = os.getenv
        with patch(
            "dispatch_cli.auth_provider.os.getenv",
            side_effect=lambda key, default=None: (
                None if key == "DISPATCH_API_KEY" else getenv(key, default)
            ),
        ):
            first = threading.Thread(target=resolve_token)
            second = threading.Thread(target=resolve_token)

            first.start()
            assert refresh_started.wait(timeout=5)
            second.start()
            release_refresh.set()
            first.join()
            second.join()

        assert refresh_calls == 1
        assert results == [
            "oauth-access-token-refreshed",
            "oauth-access-token-refreshed",
        ]
