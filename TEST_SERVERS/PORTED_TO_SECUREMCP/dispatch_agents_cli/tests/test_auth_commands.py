"""Tests for auth-related CLI commands."""

from __future__ import annotations

from unittest.mock import Mock, patch

from conftest import _memory_store, _session

from dispatch_cli.auth_provider import (
    CredentialProvider,
    MissingAuthenticationError,
    ResolvedCredential,
    StaticCredentialProvider,
)
from dispatch_cli.auth_session import (
    InvalidAuthSessionError,
)
from dispatch_cli.main import app


class TestLoginCommand:
    def test_login_runs_oauth_flow_and_persists_session(self, runner):
        login_flow = Mock()
        login_flow.login.return_value = _session()
        store = _memory_store()

        with (
            patch(
                "dispatch_cli.main.default_auth_session_store",
                return_value=store,
            ),
            patch(
                "dispatch_cli.main.default_login_flow", return_value=login_flow
            ) as flow_factory,
        ):
            result = runner.invoke(app, ["login", "--org", "org_123"])

        assert result.exit_code == 0
        flow_factory.assert_called_once_with()
        login_flow.login.assert_called_once_with(org_id="org_123")

        stored = store.load()
        assert stored is not None
        assert stored.user_email == "user@example.com"
        assert "Logged in with browser auth" in result.output

    def test_login_surfaces_oauth_flow_failure(self, runner):
        login_flow = Mock()
        login_flow.login.side_effect = RuntimeError("browser open failed")
        store = _memory_store()

        with (
            patch(
                "dispatch_cli.main.default_auth_session_store",
                return_value=store,
            ),
            patch("dispatch_cli.main.default_login_flow", return_value=login_flow),
        ):
            result = runner.invoke(app, ["login"])

        assert result.exit_code == 1
        assert "Login failed" in result.output
        assert "browser open failed" in result.output

    def test_login_handles_runtime_config_failure_without_traceback(self, runner):
        store = _memory_store()

        with (
            patch(
                "dispatch_cli.main.default_auth_session_store",
                return_value=store,
            ),
            patch(
                "dispatch_cli.main.default_login_flow",
                side_effect=RuntimeError("Missing auth CLI configuration"),
            ),
        ):
            result = runner.invoke(app, ["login"])

        assert result.exit_code == 1
        assert "Login failed: Missing auth CLI configuration" in result.output

    def test_login_reports_secure_store_bootstrap_failure(self, runner):
        with (
            patch(
                "dispatch_cli.main.default_auth_session_store",
                side_effect=InvalidAuthSessionError(
                    "Local OAuth session storage requires a system secure store."
                ),
            ),
            patch("dispatch_cli.main.default_login_flow") as flow_factory,
        ):
            result = runner.invoke(app, ["login"])

        assert result.exit_code == 1
        assert "Login failed" in result.output
        assert "system secure store" in result.output
        flow_factory.assert_not_called()


class TestLogoutCommand:
    def test_logout_clears_stored_session(self, runner):
        store = _memory_store(_session())

        with patch(
            "dispatch_cli.main.default_auth_session_store",
            return_value=store,
        ):
            result = runner.invoke(app, ["logout"])

        assert result.exit_code == 0
        assert store.load() is None
        assert "Logged out" in result.output

    def test_logout_handles_missing_session(self, runner):
        store = _memory_store()

        with patch(
            "dispatch_cli.main.default_auth_session_store",
            return_value=store,
        ):
            result = runner.invoke(app, ["logout"])

        assert result.exit_code == 0
        assert "No local OAuth session found" in result.output

    def test_logout_reports_secure_store_bootstrap_failure(self, runner):
        with patch(
            "dispatch_cli.main.default_auth_session_store",
            side_effect=InvalidAuthSessionError(
                "Local OAuth session storage requires a system secure store."
            ),
        ):
            result = runner.invoke(app, ["logout"])

        assert result.exit_code == 1
        assert "system secure store" in result.output

    def test_logout_clears_invalid_session(self, runner):
        store = _memory_store(fail_load=True)

        with patch(
            "dispatch_cli.main.default_auth_session_store",
            return_value=store,
        ):
            result = runner.invoke(app, ["logout"])

        assert result.exit_code == 0
        assert "Cleared invalid local OAuth session" in result.output
        assert store.load() is None


class TestWhoAmICommand:
    def test_whoami_shows_oauth_identity(self, runner):
        provider = StaticCredentialProvider(
            ResolvedCredential(
                auth_mode="oauth",
                access_token="oauth-access-token",
                user_email="user@example.com",
                org_id="org_123",
                org_display_name="Example Org",
            )
        )

        with patch(
            "dispatch_cli.main.default_credential_provider", return_value=provider
        ):
            result = runner.invoke(app, ["whoami"])

        assert result.exit_code == 0
        assert "Auth mode: oauth" in result.output
        assert "User: user@example.com" in result.output
        assert "Organization: Example Org (org_123)" in result.output

    def test_whoami_shows_api_key_mode(self, runner):
        provider = StaticCredentialProvider(
            ResolvedCredential(auth_mode="api_key", access_token="dak_test_123")
        )

        with patch(
            "dispatch_cli.main.default_credential_provider", return_value=provider
        ):
            result = runner.invoke(app, ["whoami"])

        assert result.exit_code == 0
        assert "Auth mode: api_key" in result.output
        assert "machine auth override" in result.output

    def test_whoami_reports_unauthenticated_state(self, runner):
        provider = Mock()
        provider.resolve.side_effect = MissingAuthenticationError(
            "Authentication required. Run `dispatch login`."
        )

        with patch(
            "dispatch_cli.main.default_credential_provider", return_value=provider
        ):
            result = runner.invoke(app, ["whoami"])

        assert result.exit_code == 0
        assert "Authentication required" in result.output
        assert "dispatch login" in result.output

    def test_whoami_reports_secure_store_bootstrap_failure(self, runner):
        with (
            patch.dict("os.environ", {}, clear=True),
            patch(
                "dispatch_cli.main.default_credential_provider",
                side_effect=InvalidAuthSessionError(
                    "Local OAuth session storage requires a system secure store."
                ),
            ),
        ):
            result = runner.invoke(app, ["whoami"])

        assert result.exit_code == 0
        assert "system secure store" in result.output

    def test_whoami_handles_invalid_local_session(self, runner):
        store = _memory_store(fail_load=True)
        provider = CredentialProvider(store=store)

        with (
            patch.dict("os.environ", {}, clear=True),
            patch(
                "dispatch_cli.main.default_credential_provider",
                return_value=provider,
            ),
        ):
            result = runner.invoke(app, ["whoami"])

        assert result.exit_code == 0
        assert "Stored OAuth session is invalid" in result.output
        assert "dispatch login" in result.output
        assert store.load() is None

    def test_whoami_logs_debug_when_session_expiry_lookup_fails(self, runner):
        provider = StaticCredentialProvider(
            ResolvedCredential(
                auth_mode="oauth",
                access_token="oauth-access-token",
                user_email="user@example.com",
            )
        )
        logger = Mock()
        store = Mock()
        store.load.side_effect = InvalidAuthSessionError("broken keychain entry")

        with (
            patch(
                "dispatch_cli.main.default_credential_provider", return_value=provider
            ),
            patch("dispatch_cli.main.default_auth_session_store", return_value=store),
            patch("dispatch_cli.logger.get_logger", return_value=logger),
        ):
            result = runner.invoke(app, ["whoami"])

        assert result.exit_code == 0
        logger.info.assert_any_call("Auth mode: oauth")
        logger.debug.assert_called_once_with(
            "Could not load session expiry details: broken keychain entry"
        )


class TestProtectedCommandAuth:
    def test_protected_command_directs_user_to_login_when_unauthenticated(self, runner):
        provider = Mock()
        provider.resolve.side_effect = MissingAuthenticationError(
            "Authentication required. Run `dispatch login`."
        )

        with patch(
            "dispatch_cli.auth.default_credential_provider", return_value=provider
        ):
            result = runner.invoke(
                app, ["skills", "search", "demo", "--namespace", "default"]
            )

        assert result.exit_code == 1
        assert "dispatch login" in result.output
