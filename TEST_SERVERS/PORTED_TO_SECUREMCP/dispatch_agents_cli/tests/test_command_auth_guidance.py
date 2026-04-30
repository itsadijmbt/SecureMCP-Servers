"""Tests for command-level auth guidance on HTTP 401 responses."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
import requests

from dispatch_cli.auth_provider import MissingAuthenticationError
from dispatch_cli.main import app


def _http_401_error(url: str) -> requests.exceptions.HTTPError:
    response = requests.Response()
    response.status_code = 401
    response.url = url
    request = requests.Request("GET", url).prepare()
    response.request = request
    return requests.exceptions.HTTPError("401 Client Error", response=response)


AUTH_GUIDANCE_CASES = [
    pytest.param(
        "dispatch_cli.commands.llm.get_auth_headers",
        "dispatch_cli.commands.llm.requests.get",
        ["llm", "list", "--namespace", "default"],
        "https://dispatchagents.work/namespace/default",
        id="llm_list",
    ),
    pytest.param(
        "dispatch_cli.commands.skills.get_auth_headers",
        "dispatch_cli.commands.skills.requests.get",
        ["skills", "show", "demo", "--namespace", "default"],
        "https://dispatchagents.work/api/unstable/namespace/default/skills/demo",
        id="skills_show",
    ),
    pytest.param(
        "dispatch_cli.commands.secrets.get_auth_headers",
        "dispatch_cli.commands.secrets.requests.get",
        ["secret", "list", "--namespace", "default"],
        "https://dispatchagents.work/namespace/default/secrets/list",
        id="secret_list",
    ),
]


class TestCommandAuthGuidance:
    def test_llm_list_reports_missing_auth_with_login_guidance(self, runner):
        provider = Mock()
        provider.resolve.side_effect = MissingAuthenticationError(
            "Authentication required. Run `dispatch login`."
        )

        with patch(
            "dispatch_cli.auth.default_credential_provider", return_value=provider
        ):
            result = runner.invoke(app, ["llm", "list", "--namespace", "default"])

        assert result.exit_code == 1
        assert "dispatch login" in result.output

    @pytest.mark.parametrize(
        ("headers_target", "request_target", "argv", "url"),
        AUTH_GUIDANCE_CASES,
    )
    def test_invalid_env_api_key_tells_user_to_update_or_unset_it(
        self,
        runner,
        headers_target: str,
        request_target: str,
        argv: list[str],
        url: str,
    ):
        store = Mock()

        with (
            patch.dict("os.environ", {"DISPATCH_API_KEY": "dak_invalid"}, clear=False),
            patch(headers_target, return_value={"Authorization": "Bearer dak_invalid"}),
            patch(request_target, side_effect=_http_401_error(url)),
            patch("dispatch_cli.auth.default_auth_session_store", return_value=store),
        ):
            result = runner.invoke(app, argv)

        assert result.exit_code == 1
        assert "DISPATCH_API_KEY" in result.output
        assert "Update or unset it" in result.output
        assert "dispatch login" not in result.output
        store.clear.assert_not_called()

    @pytest.mark.parametrize(
        ("headers_target", "request_target", "argv", "url"),
        AUTH_GUIDANCE_CASES,
    )
    def test_oauth_401_clears_session_and_prompts_relogin(
        self,
        runner,
        headers_target: str,
        request_target: str,
        argv: list[str],
        url: str,
    ):
        store = Mock()

        with (
            patch.dict("os.environ", {}, clear=True),
            patch(headers_target, return_value={"Authorization": "Bearer oauth-token"}),
            patch(request_target, side_effect=_http_401_error(url)),
            patch("dispatch_cli.auth.default_auth_session_store", return_value=store),
        ):
            result = runner.invoke(app, argv)

        assert result.exit_code == 1
        assert "dispatch login" in result.output
        assert "local OAuth session was cleared" in result.output
        store.clear.assert_called_once_with()
