"""Tests for OAuth login flow orchestration."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
import requests

from dispatch_cli.auth_login import (
    AuthClientConfig,
    AuthOrganization,
    AuthUserContext,
    BrowserLoginFlow,
    _CallbackResult,
    _LoopbackCallbackListener,
    _validate_callback_result,
    default_login_flow,
    refresh_auth_session,
)
from dispatch_cli.auth_session import OAuthSession


def _session(access_token: str = "oauth-access-token") -> OAuthSession:
    return OAuthSession(
        access_token=access_token,
        refresh_token="oauth-refresh-token",
        expires_at="2099-01-01T00:00:00+00:00",
    )


class TestDefaultLoginFlow:
    def test_uses_dispatch_env_overrides(self):
        with patch.dict(
            "os.environ",
            {
                "DISPATCH_AUTH_DOMAIN": "tenant.auth0.com",
                "DISPATCH_AUTH_CLIENT_ID": "client_123",
                "DISPATCH_AUTH_AUDIENCE": "https://dispatchagents.ai",
            },
            clear=True,
        ):
            flow = default_login_flow()

        assert isinstance(flow, BrowserLoginFlow)
        assert flow.config == AuthClientConfig(
            domain="tenant.auth0.com",
            client_id="client_123",
            audience="https://dispatchagents.ai",
        )

    def test_fetches_runtime_config_from_backend_when_env_missing(self):
        response = Mock()
        response.ok = True
        response.json.return_value = {
            "auth_domain": "tenant.auth0.com",
            "auth_cli_client_id": "client_123",
            "auth_api_audience": "https://dispatchagents.ai",
        }

        with (
            patch.dict("os.environ", {}, clear=True),
            patch(
                "dispatch_cli.auth_login.DISPATCH_API_BASE",
                "https://dispatchagents.ai",
            ),
            patch("dispatch_cli.auth_login.requests.get", return_value=response) as get,
        ):
            flow = default_login_flow()

        assert isinstance(flow, BrowserLoginFlow)
        assert flow.config == AuthClientConfig(
            domain="tenant.auth0.com",
            client_id="client_123",
            audience="https://dispatchagents.ai",
        )
        get.assert_called_once_with(
            "https://dispatchagents.ai/api/unstable/config",
            timeout=5,
        )

    def test_normalizes_api_base_when_env_points_at_unstable_root(self):
        response = Mock()
        response.ok = True
        response.json.return_value = {
            "auth_domain": "tenant.auth0.com",
            "auth_cli_client_id": "client_123",
            "auth_api_audience": "https://dispatchagents.work",
        }

        with (
            patch.dict("os.environ", {}, clear=True),
            patch(
                "dispatch_cli.auth_login.DISPATCH_API_BASE",
                "https://dispatchagents.work/api/unstable",
            ),
            patch("dispatch_cli.auth_login.requests.get", return_value=response) as get,
        ):
            flow = default_login_flow()

        assert isinstance(flow, BrowserLoginFlow)
        get.assert_called_once_with(
            "https://dispatchagents.work/api/unstable/config",
            timeout=5,
        )

    def test_raises_when_runtime_config_payload_is_incomplete(self):
        response = Mock()
        response.ok = True
        response.json.return_value = {
            "auth_domain": "tenant.auth0.com",
            "auth_api_audience": "https://dispatchagents.ai",
        }

        with (
            patch.dict("os.environ", {}, clear=True),
            patch("dispatch_cli.auth_login.requests.get", return_value=response),
        ):
            with pytest.raises(RuntimeError) as excinfo:
                default_login_flow()

        assert "incomplete" in str(excinfo.value)

    def test_raises_when_runtime_config_cannot_be_loaded(self):
        with (
            patch.dict("os.environ", {}, clear=True),
            patch(
                "dispatch_cli.auth_login.requests.get",
                side_effect=requests.ConnectionError("network down"),
            ),
        ):
            with pytest.raises(RuntimeError) as excinfo:
                default_login_flow()

        assert "Could not load auth CLI configuration" in str(excinfo.value)


class TestBrowserLoginFlow:
    def test_normalizes_api_base_before_fetching_user_context(self):
        response = Mock(status_code=200)
        response.json.return_value = {
            "email": "user@example.com",
            "org_id": "org_123",
            "org_display_name": "Example Org",
        }
        http_session = Mock()
        http_session.get.return_value = response
        flow = BrowserLoginFlow(
            AuthClientConfig(
                domain="tenant.auth0.com",
                client_id="client_123",
                audience="aud",
            ),
            api_base="https://dispatchagents.work/api/unstable",
            http_session=http_session,
        )

        context = flow._fetch_user_context("oauth-access-token")

        assert context == AuthUserContext(
            user_email="user@example.com",
            org_id="org_123",
            org_display_name="Example Org",
        )
        http_session.get.assert_called_once_with(
            "https://dispatchagents.work/auth/me",
            headers={"Authorization": "Bearer oauth-access-token"},
            timeout=30,
        )

    def test_returns_enriched_session_when_initial_login_has_org_context(self):
        flow = BrowserLoginFlow(
            AuthClientConfig(
                domain="tenant.auth0.com",
                client_id="client_123",
                audience="aud",
            )
        )
        first_session = _session()
        flow._authorize = Mock(return_value=first_session)
        flow._fetch_user_context = Mock(
            return_value=AuthUserContext(
                user_email="user@example.com",
                org_id="org_123",
                org_display_name="Example Org",
            )
        )

        session = flow.login(org_id=None)

        assert session.user_email == "user@example.com"
        assert session.org_id == "org_123"
        flow._authorize.assert_called_once_with(org_id=None)

    def test_auto_selects_single_organization_when_required(self):
        status_reporter = Mock()
        flow = BrowserLoginFlow(
            AuthClientConfig(
                domain="tenant.auth0.com",
                client_id="client_123",
                audience="aud",
            ),
            status_reporter=status_reporter,
        )
        discovery_session = _session("discovery-token")
        org_session = _session("org-token")
        flow._authorize = Mock(side_effect=[discovery_session, org_session])
        flow._fetch_user_context = Mock(
            side_effect=[
                None,
                AuthUserContext(
                    user_email="user@example.com",
                    org_id="org_123",
                    org_display_name="Example Org",
                ),
            ]
        )
        flow._fetch_organizations = Mock(
            return_value=[
                AuthOrganization(
                    id="org_123", name="example", display_name="Example Org"
                )
            ]
        )

        session = flow.login(org_id=None)

        assert session.org_id == "org_123"
        assert flow._authorize.call_args_list[1].kwargs == {"org_id": "org_123"}
        status_reporter.assert_called_once_with(
            "Opening browser again to complete login with organization context..."
        )

    def test_prompts_for_org_when_multiple_orgs_are_available(self):
        flow = BrowserLoginFlow(
            AuthClientConfig(
                domain="tenant.auth0.com",
                client_id="client_123",
                audience="aud",
            )
        )
        discovery_session = _session("discovery-token")
        org_session = _session("org-token")
        flow._authorize = Mock(side_effect=[discovery_session, org_session])
        flow._fetch_user_context = Mock(
            side_effect=[
                None,
                AuthUserContext(
                    user_email="user@example.com",
                    org_id="org_456",
                    org_display_name="Chosen Org",
                ),
            ]
        )
        flow._fetch_organizations = Mock(
            return_value=[
                AuthOrganization(id="org_123", name="first", display_name="First Org"),
                AuthOrganization(
                    id="org_456", name="chosen", display_name="Chosen Org"
                ),
            ]
        )
        flow._select_organization = Mock(return_value="org_456")

        session = flow.login(org_id=None)

        assert session.org_id == "org_456"
        flow._select_organization.assert_called_once()

    def test_raises_when_user_has_no_organizations(self):
        flow = BrowserLoginFlow(
            AuthClientConfig(
                domain="tenant.auth0.com",
                client_id="client_123",
                audience="aud",
            )
        )
        flow._authorize = Mock(return_value=_session("discovery-token"))
        flow._fetch_user_context = Mock(return_value=None)
        flow._fetch_organizations = Mock(return_value=[])

        with pytest.raises(RuntimeError) as excinfo:
            flow.login(org_id=None)

        assert "organizations" in str(excinfo.value)

    def test_exchange_requires_refresh_token_for_browser_login(self):
        response = Mock()
        response.ok = True
        response.json.return_value = {
            "access_token": "oauth-access-token",
            "expires_in": 3600,
        }
        http_session = Mock()
        http_session.post.return_value = response
        flow = BrowserLoginFlow(
            AuthClientConfig(
                domain="tenant.auth0.com",
                client_id="client_123",
                audience="aud",
            ),
            http_session=http_session,
        )

        with pytest.raises(RuntimeError) as excinfo:
            flow._exchange_code_for_tokens(
                code="auth-code",
                code_verifier="verifier",
                redirect_uri="http://127.0.0.1:1234/callback",
            )

        assert "refresh token" in str(excinfo.value)

    def test_authorize_uses_callback_listener_factory_and_closes_listener(self):
        response = Mock()
        response.ok = True
        response.json.return_value = {
            "access_token": "oauth-access-token",
            "refresh_token": "oauth-refresh-token",
            "expires_in": 3600,
        }
        http_session = Mock()
        http_session.post.return_value = response
        browser_opener = Mock(return_value=True)
        listener = Mock()
        listener.redirect_uri = "http://127.0.0.1:8765/callback"
        listener.wait_for_result.return_value.code = "auth-code"
        listener.wait_for_result.return_value.state = "test-state"
        listener.wait_for_result.return_value.error = None
        listener.wait_for_result.return_value.error_description = None
        listener_factory = Mock(return_value=listener)
        flow = BrowserLoginFlow(
            AuthClientConfig(
                domain="tenant.auth0.com",
                client_id="client_123",
                audience="aud",
            ),
            browser_opener=browser_opener,
            http_session=http_session,
            callback_listener_factory=listener_factory,
        )

        with patch(
            "dispatch_cli.auth_login.secrets.token_urlsafe",
            side_effect=["test-state", "code-verifier"],
        ):
            session = flow._authorize(org_id="org_123")

        assert session.access_token == "oauth-access-token"
        listener_factory.assert_called_once_with(host="127.0.0.1", port=8765)
        browser_opener.assert_called_once()
        listener.close.assert_called_once()
        http_session.post.assert_called_once()
        post_data = http_session.post.call_args.kwargs["data"]
        assert post_data["code_verifier"] == "code-verifier"
        assert post_data["grant_type"] == "authorization_code"
        assert post_data["code"] == "auth-code"

    def test_authorize_closes_listener_when_browser_open_fails(self):
        listener = Mock()
        listener.redirect_uri = "http://127.0.0.1:8765/callback"
        listener_factory = Mock(return_value=listener)
        flow = BrowserLoginFlow(
            AuthClientConfig(
                domain="tenant.auth0.com",
                client_id="client_123",
                audience="aud",
            ),
            browser_opener=Mock(return_value=False),
            callback_listener_factory=listener_factory,
        )

        with (
            patch(
                "dispatch_cli.auth_login.secrets.token_urlsafe",
                side_effect=["test-state", "code-verifier"],
            ),
            pytest.raises(RuntimeError) as excinfo,
        ):
            flow._authorize(org_id=None)

        assert "Could not open the browser" in str(excinfo.value)
        assert "DISPATCH_API_KEY" in str(excinfo.value)
        listener.close.assert_called_once()

    def test_authorize_rejects_state_mismatch_before_token_exchange(self):
        http_session = Mock()
        browser_opener = Mock(return_value=True)
        listener = Mock()
        listener.redirect_uri = "http://127.0.0.1:8765/callback"
        listener.wait_for_result.return_value.code = "auth-code"
        listener.wait_for_result.return_value.state = "wrong-state"
        listener.wait_for_result.return_value.error = None
        listener.wait_for_result.return_value.error_description = None
        flow = BrowserLoginFlow(
            AuthClientConfig(
                domain="tenant.auth0.com",
                client_id="client_123",
                audience="aud",
            ),
            browser_opener=browser_opener,
            http_session=http_session,
            callback_listener_factory=Mock(return_value=listener),
        )

        with (
            patch(
                "dispatch_cli.auth_login.secrets.token_urlsafe",
                side_effect=["expected-state", "code-verifier"],
            ),
            pytest.raises(RuntimeError) as excinfo,
        ):
            flow._authorize(org_id=None)

        assert "Invalid auth callback received." in str(excinfo.value)
        http_session.post.assert_not_called()
        listener.close.assert_called_once()

    def test_authorize_falls_back_to_fallback_port_when_primary_port_in_use(self):
        listener = Mock()
        listener.redirect_uri = "http://127.0.0.1:8766/callback"
        listener.wait_for_result.return_value.code = "auth-code"
        listener.wait_for_result.return_value.state = "test-state"
        listener.wait_for_result.return_value.error = None
        listener.wait_for_result.return_value.error_description = None
        listener_factory = Mock(
            side_effect=[OSError(48, "Address already in use"), listener]
        )
        http_session = Mock()
        http_session.post.return_value = Mock()
        http_session.post.return_value.json.return_value = {
            "access_token": "oauth-access-token",
            "refresh_token": "refresh-token",
            "expires_in": 3600,
        }
        flow = BrowserLoginFlow(
            AuthClientConfig(
                domain="tenant.auth0.com",
                client_id="client_123",
                audience="aud",
            ),
            browser_opener=Mock(return_value=True),
            http_session=http_session,
            callback_listener_factory=listener_factory,
        )

        with patch(
            "dispatch_cli.auth_login.secrets.token_urlsafe",
            side_effect=["test-state", "code-verifier"],
        ):
            session = flow._authorize(org_id=None)

        assert session.access_token == "oauth-access-token"
        assert listener_factory.call_count == 2
        listener_factory.assert_any_call(host="127.0.0.1", port=8765)
        listener_factory.assert_any_call(host="127.0.0.1", port=8766)

    def test_authorize_raises_when_both_ports_are_in_use(self):
        flow = BrowserLoginFlow(
            AuthClientConfig(
                domain="tenant.auth0.com",
                client_id="client_123",
                audience="aud",
            ),
            callback_listener_factory=Mock(
                side_effect=OSError(48, "Address already in use")
            ),
        )

        with pytest.raises(RuntimeError) as excinfo:
            flow._authorize(org_id=None)

        message = str(excinfo.value)
        assert "127.0.0.1:8765" in message
        assert "127.0.0.1:8766" in message
        assert "dispatch login" in message


class TestLoopbackCallbackListener:
    def test_loopback_listener_server_allows_address_reuse(self):
        """SO_REUSEADDR must be set to avoid TIME_WAIT port exhaustion on rapid retries."""
        listener = _LoopbackCallbackListener(port=0)
        try:
            # allow_reuse_address should be truthy (True or 1)
            assert listener._server.allow_reuse_address
        finally:
            listener.close()

    def test_receives_callback_result_over_http(self):
        listener = _LoopbackCallbackListener(port=0)

        try:
            response = requests.get(
                f"{listener.redirect_uri}?code=auth-code&state=test-state",
                timeout=2,
            )
            result = listener.wait_for_result(timeout_seconds=1)
        finally:
            listener.close()

        assert response.status_code == 200
        assert result.code == "auth-code"
        assert result.state == "test-state"

    def test_ignores_non_callback_requests_until_auth_callback_arrives(self):
        listener = _LoopbackCallbackListener(port=0)
        non_callback_url = listener.redirect_uri.removesuffix("/callback") + "/health"

        try:
            non_callback = requests.get(non_callback_url, timeout=2)
            callback = requests.get(
                f"{listener.redirect_uri}?code=auth-code&state=test-state",
                timeout=2,
            )
            result = listener.wait_for_result(timeout_seconds=1)
        finally:
            listener.close()

        assert non_callback.status_code == 404
        assert callback.status_code == 200
        assert result.code == "auth-code"
        assert result.state == "test-state"


class TestRefreshAuthSession:
    def test_uses_refresh_token_grant_and_preserves_context(self):
        response = Mock()
        response.ok = True
        response.json.return_value = {
            "access_token": "oauth-access-token-refreshed",
            "refresh_token": "oauth-refresh-token-rotated",
            "expires_in": 7200,
        }
        http_session = Mock()
        http_session.post.return_value = response
        session = OAuthSession(
            access_token="oauth-access-token",
            refresh_token="oauth-refresh-token",
            expires_at="2000-01-01T00:00:00+00:00",
            user_email="user@example.com",
            org_id="org_123",
            org_display_name="Example Org",
        )

        refreshed = refresh_auth_session(
            session,
            config=AuthClientConfig(
                domain="tenant.auth0.com",
                client_id="client_123",
                audience="aud",
            ),
            http_session=http_session,
        )

        assert refreshed.access_token == "oauth-access-token-refreshed"
        assert refreshed.refresh_token == "oauth-refresh-token-rotated"
        assert refreshed.user_email == "user@example.com"
        assert refreshed.org_id == "org_123"
        http_session.post.assert_called_once_with(
            "https://tenant.auth0.com/oauth/token",
            data={
                "grant_type": "refresh_token",
                "client_id": "client_123",
                "refresh_token": "oauth-refresh-token",
            },
            timeout=30,
        )

    def test_preserves_existing_refresh_token_when_auth0_does_not_rotate_it(self):
        response = Mock()
        response.ok = True
        response.json.return_value = {
            "access_token": "oauth-access-token-refreshed",
            "expires_in": 3600,
        }
        http_session = Mock()
        http_session.post.return_value = response
        session = OAuthSession(
            access_token="oauth-access-token",
            refresh_token="oauth-refresh-token",
            expires_at="2000-01-01T00:00:00+00:00",
        )

        refreshed = refresh_auth_session(
            session,
            config=AuthClientConfig(
                domain="tenant.auth0.com",
                client_id="client_123",
                audience="aud",
            ),
            http_session=http_session,
        )

        assert refreshed.refresh_token == "oauth-refresh-token"

    def test_rejects_invalid_token_payload(self):
        response = Mock()
        response.ok = True
        response.json.return_value = {
            "access_token": "",
            "expires_in": "soon",
        }
        http_session = Mock()
        http_session.post.return_value = response
        session = OAuthSession(
            access_token="oauth-access-token",
            refresh_token="oauth-refresh-token",
            expires_at="2000-01-01T00:00:00+00:00",
        )

        with pytest.raises(RuntimeError, match="Auth token response was invalid"):
            refresh_auth_session(
                session,
                config=AuthClientConfig(
                    domain="tenant.auth0.com",
                    client_id="client_123",
                    audience="aud",
                ),
                http_session=http_session,
            )


class TestValidateCallbackResult:
    def test_rejects_none_state(self):
        """state=None must not bypass state validation via the 'or ""' fallback."""
        callback = _CallbackResult(
            code="auth-code",
            state=None,
            error=None,
            error_description=None,
        )
        with pytest.raises(RuntimeError, match="Invalid auth callback received"):
            _validate_callback_result(callback, expected_state="expected-state")

    def test_rejects_empty_string_state(self):
        """state='' must not match a non-empty expected_state."""
        callback = _CallbackResult(
            code="auth-code",
            state="",
            error=None,
            error_description=None,
        )
        with pytest.raises(RuntimeError, match="Invalid auth callback received"):
            _validate_callback_result(callback, expected_state="expected-state")

    def test_accepts_matching_state_and_returns_code(self):
        """A matching state must pass validation and return the authorization code."""
        callback = _CallbackResult(
            code="auth-code",
            state="expected-state",
            error=None,
            error_description=None,
        )
        result = _validate_callback_result(callback, expected_state="expected-state")
        assert result == "auth-code"

    def test_rejects_missing_code_even_with_valid_state(self):
        """Reject callback if code is None regardless of state."""
        callback = _CallbackResult(
            code=None,
            state="expected-state",
            error=None,
            error_description=None,
        )
        with pytest.raises(RuntimeError, match="Invalid auth callback received"):
            _validate_callback_result(callback, expected_state="expected-state")
