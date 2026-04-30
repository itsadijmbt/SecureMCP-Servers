"""Tests for the legacy auth helper compatibility layer."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
import typer
from conftest import _memory_store, _session

from dispatch_cli.auth import get_auth_headers, get_bearer_token, handle_auth_error
from dispatch_cli.auth_provider import MissingAuthenticationError, ResolvedCredential
from dispatch_cli.auth_session import (
    InvalidAuthSessionError,
)


class TestGetBearerToken:
    def test_returns_token_from_shared_credential_provider(self):
        provider = Mock()
        provider.resolve.return_value = ResolvedCredential(
            auth_mode="oauth",
            access_token="oauth-access-token",
        )

        with patch(
            "dispatch_cli.auth.default_credential_provider", return_value=provider
        ):
            assert get_bearer_token() == "oauth-access-token"

    def test_exits_with_login_guidance_when_no_auth_is_available(self, capsys):
        provider = Mock()
        provider.resolve.side_effect = MissingAuthenticationError(
            "Authentication required. Run `dispatch login`."
        )

        with patch(
            "dispatch_cli.auth.default_credential_provider", return_value=provider
        ):
            with pytest.raises(typer.Exit) as excinfo:
                get_bearer_token()

        assert excinfo.value.exit_code == 1
        captured = capsys.readouterr()
        assert "dispatch login" in captured.err

    def test_exits_with_secure_store_guidance_when_store_bootstrap_fails(self, capsys):
        with patch(
            "dispatch_cli.auth.default_credential_provider",
            side_effect=InvalidAuthSessionError(
                "Local OAuth session storage requires a system secure store."
            ),
        ):
            with pytest.raises(typer.Exit) as excinfo:
                get_bearer_token()

        assert excinfo.value.exit_code == 1
        captured = capsys.readouterr()
        assert "system secure store" in captured.err

    def test_exits_with_dispatch_api_key_format_guidance(self, capsys):
        provider = Mock()
        provider.resolve.side_effect = MissingAuthenticationError(
            "DISPATCH_API_KEY must be a Dispatch API key starting with `dak_`."
        )

        with patch(
            "dispatch_cli.auth.default_credential_provider", return_value=provider
        ):
            with pytest.raises(typer.Exit) as excinfo:
                get_bearer_token()

        assert excinfo.value.exit_code == 1
        captured = capsys.readouterr()
        assert "DISPATCH_API_KEY" in captured.err
        assert "dak_" in captured.err


class TestGetAuthHeaders:
    def test_builds_versioned_auth_headers_from_current_bearer_token(self):
        with patch(
            "dispatch_cli.auth.get_bearer_token", return_value="oauth-access-token"
        ):
            headers = get_auth_headers()

        assert headers["Authorization"] == "Bearer oauth-access-token"
        assert headers["x-dispatch-client"] == "cli"


class TestHandleAuthError:
    def test_clears_local_oauth_session_and_exits(self, capsys):
        store = _memory_store(_session())

        with (
            patch("dispatch_cli.auth.default_auth_session_store", return_value=store),
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(typer.Exit) as excinfo,
        ):
            handle_auth_error("Invalid or expired token")

        assert excinfo.value.exit_code == 1
        assert store.load() is None
        captured = capsys.readouterr()
        assert "dispatch login" in captured.err

    def test_preserves_local_oauth_session_when_env_api_key_is_active(self, capsys):
        store = _memory_store()
        session = _session()
        store.save(session)

        with (
            patch("dispatch_cli.auth.default_auth_session_store", return_value=store),
            patch.dict("os.environ", {"DISPATCH_API_KEY": "dak_test_123"}, clear=False),
            pytest.raises(typer.Exit) as excinfo,
        ):
            handle_auth_error("Invalid or expired token")

        assert excinfo.value.exit_code == 1
        assert store.load() == session
        captured = capsys.readouterr()
        assert "DISPATCH_API_KEY" in captured.err
