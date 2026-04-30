"""Tests for MCP auth behavior with shared CLI credentials."""

from __future__ import annotations

import tomllib
from pathlib import Path
from unittest.mock import Mock, patch

import httpx
import pytest
from typer.testing import CliRunner

from dispatch_cli.auth_provider import (
    MissingAuthenticationError,
    ResolvedCredential,
    StaticCredentialProvider,
)
from dispatch_cli.main import app
from dispatch_cli.mcp.agent.server import create_agent_server
from dispatch_cli.mcp.client import (
    AgentBackendClient,
    DispatchAPIClient,
    OperatorBackendClient,
)
from dispatch_cli.mcp.config import MCPConfig
from dispatch_cli.mcp.operator.server import create_operator_server, run_operator_server
from dispatch_cli.mcp.operator.tools import ListNamespacesRequest


class TestMCPCommands:
    def test_serve_agent_uses_shared_credential_provider(self, runner: CliRunner):
        provider = StaticCredentialProvider(
            ResolvedCredential(auth_mode="oauth", access_token="oauth-token")
        )
        backend_client = Mock()
        backend_client.list_namespaces.return_value = {"namespaces": []}

        with (
            patch("dispatch_cli.main.check_and_notify_cli_update"),
            patch(
                "dispatch_cli.commands.mcp.default_credential_provider",
                return_value=provider,
            ),
            patch(
                "dispatch_cli.commands.mcp.default_operator_backend_client",
                return_value=backend_client,
            ),
            patch("dispatch_cli.commands.mcp.run_agent_server") as run_agent_server,
        ):
            result = runner.invoke(
                app,
                ["mcp", "serve", "agent", "--namespace", "demo", "--agent", "greeter"],
            )

        assert result.exit_code == 0
        backend_client.list_namespaces.assert_called_once_with()
        backend_client.close.assert_called_once_with()
        config = run_agent_server.call_args.args[0]
        assert config.credential_provider is provider

    def test_serve_operator_defers_auth_until_tool_invocation(self, runner: CliRunner):
        provider = Mock()
        provider.resolve.side_effect = MissingAuthenticationError(
            "Authentication required. Run `dispatch login`."
        )

        with (
            patch("dispatch_cli.main.check_and_notify_cli_update"),
            patch(
                "dispatch_cli.commands.mcp.default_credential_provider",
                return_value=provider,
            ),
            patch(
                "dispatch_cli.commands.mcp.run_operator_server"
            ) as run_operator_server,
        ):
            result = runner.invoke(
                app,
                ["mcp", "serve", "operator", "--namespace", "demo"],
            )

        assert result.exit_code == 0
        provider.resolve.assert_not_called()
        config = run_operator_server.call_args.args[0]
        assert config.credential_provider is provider

    @pytest.mark.asyncio
    async def test_operator_tools_prompt_login_when_auth_missing(self):
        provider = Mock()
        provider.resolve.side_effect = MissingAuthenticationError(
            "Authentication required. Run `dispatch login`."
        )
        config = MCPConfig(
            credential_provider=provider,
            namespace="demo",
            server_type="operator",
        )

        server = create_operator_server(config)

        list_namespaces = server._tool_manager._tools["list_namespaces"].fn

        with pytest.raises(MissingAuthenticationError, match="dispatch login"):
            await list_namespaces(ListNamespacesRequest())

    def test_register_operator_fails_closed_when_invalid_api_key(
        self, runner: CliRunner
    ):
        provider = StaticCredentialProvider(
            ResolvedCredential(auth_mode="api_key", access_token="invalid-token")
        )
        backend_client = Mock()
        request = httpx.Request("GET", "https://dispatchagents.work/namespaces/list")
        response = httpx.Response(401, request=request)
        auth_error = httpx.HTTPStatusError(
            "401 Unauthorized", request=request, response=response
        )
        backend_client.list_namespaces.side_effect = auth_error

        with runner.isolated_filesystem():
            with (
                patch.dict(
                    "os.environ", {"DISPATCH_API_KEY": "dak_invalid"}, clear=False
                ),
                patch("dispatch_cli.main.check_and_notify_cli_update"),
                patch(
                    "dispatch_cli.commands.mcp.default_credential_provider",
                    return_value=provider,
                ),
                patch(
                    "dispatch_cli.commands.mcp.default_operator_backend_client",
                    return_value=backend_client,
                ),
            ):
                result = runner.invoke(
                    app,
                    ["mcp", "serve", "operator", "--register", "codex"],
                )

            assert result.exit_code == 1
            assert "Authentication verified" not in result.output
            assert "DISPATCH_API_KEY" in result.output
            assert "Error: 1" not in result.output
            assert not Path(".codex/config.toml").exists()
            backend_client.close.assert_called_once_with()

    @pytest.mark.parametrize(
        ("credential", "environment", "expected_env"),
        [
            pytest.param(
                ResolvedCredential(auth_mode="oauth", access_token="oauth-token"),
                {"DISPATCH_DEPLOY_URL": "https://dispatchagents.work"},
                {"DISPATCH_DEPLOY_URL": "https://dispatchagents.work"},
                id="oauth_with_deploy_url",
            ),
            pytest.param(
                ResolvedCredential(auth_mode="api_key", access_token="dak_valid"),
                {"DISPATCH_API_KEY": "dak_valid"},
                None,
                id="api_key_without_deploy_url",
            ),
        ],
    )
    def test_register_operator_success_cases(
        self,
        runner: CliRunner,
        credential: ResolvedCredential,
        environment: dict[str, str],
        expected_env: dict[str, str] | None,
    ):
        provider = StaticCredentialProvider(credential)
        backend_client = Mock()
        backend_client.list_namespaces.return_value = {"namespaces": []}

        with runner.isolated_filesystem():
            with (
                patch.dict("os.environ", environment, clear=True),
                patch("dispatch_cli.main.check_and_notify_cli_update"),
                patch(
                    "dispatch_cli.commands.mcp.default_credential_provider",
                    return_value=provider,
                ),
                patch(
                    "dispatch_cli.commands.mcp.default_operator_backend_client",
                    return_value=backend_client,
                ),
            ):
                result = runner.invoke(
                    app,
                    ["mcp", "serve", "operator", "--register", "codex"],
                )

            assert result.exit_code == 0
            assert "Authentication verified" in result.output
            config_path = Path(".codex/config.toml")
            assert config_path.exists()
            config = tomllib.loads(config_path.read_text())
            server = config["mcp_servers"]["dispatch_operator"]
            if expected_env is None:
                assert "env" not in server
            else:
                assert server["env"] == expected_env
            backend_client.close.assert_called_once_with()


class TestDispatchAPIClient:
    def test_client_resolves_headers_dynamically_for_each_request(self):
        provider = Mock()
        provider.resolve.side_effect = [
            ResolvedCredential(auth_mode="oauth", access_token="oauth-token-1"),
            ResolvedCredential(auth_mode="oauth", access_token="oauth-token-2"),
        ]
        config = MCPConfig(credential_provider=provider, namespace="demo")
        client = DispatchAPIClient(config)

        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {"ok": True}
        client.client.request = Mock(return_value=response)

        client.list_namespaces()
        client.list_namespaces()

        first_headers = client.client.request.call_args_list[0].kwargs["headers"]
        second_headers = client.client.request.call_args_list[1].kwargs["headers"]
        assert first_headers["Authorization"] == "Bearer oauth-token-1"
        assert second_headers["Authorization"] == "Bearer oauth-token-2"


class FakeAgentBackendClient:
    def __init__(self):
        self.calls: list[tuple[str, str, str | None]] = []

    def get_agent_info(self, agent_id: str, namespace: str | None = None) -> dict:
        self.calls.append(("get_agent_info", agent_id, namespace))
        return {
            "functions": [
                {
                    "name": "greet",
                    "description": "Greet a user",
                    "input_schema": {"type": "object"},
                    "output_schema": {"type": "object"},
                }
            ]
        }

    async def invoke_function_async(
        self,
        agent_name: str,
        function_name: str,
        payload: dict,
        namespace: str | None = None,
        timeout_seconds: int | None = None,
    ) -> dict:
        raise AssertionError("invoke_function_async should not be used in this test")

    async def get_invocation_status_async(
        self, invocation_id: str, namespace: str | None = None
    ) -> dict:
        raise AssertionError(
            "get_invocation_status_async should not be used in this test"
        )


class TestAgentServerInterfaces:
    def test_create_agent_server_accepts_agent_backend_client_interface(self):
        provider = StaticCredentialProvider(
            ResolvedCredential(auth_mode="oauth", access_token="oauth-token")
        )
        config = MCPConfig(
            credential_provider=provider,
            namespace="demo",
            agent_name="greeter",
        )
        client: AgentBackendClient = FakeAgentBackendClient()

        server = create_agent_server(config, client=client)

        assert server is not None
        assert client.calls == [("get_agent_info", "greeter", "demo")]


class FakeOperatorBackendClient:
    def close(self) -> None:
        pass


class TestOperatorServerInterfaces:
    def test_create_operator_server_uses_default_operator_backend_factory(self):
        provider = StaticCredentialProvider(
            ResolvedCredential(auth_mode="oauth", access_token="oauth-token")
        )
        config = MCPConfig(
            credential_provider=provider,
            namespace="demo",
            server_type="operator",
        )
        client: OperatorBackendClient = FakeOperatorBackendClient()
        mcp = Mock()

        with (
            patch(
                "dispatch_cli.mcp.operator.server.default_operator_backend_client",
                return_value=client,
            ) as default_client,
            patch(
                "dispatch_cli.mcp.operator.server.create_operator_mcp",
                return_value=mcp,
            ) as create_mcp,
        ):
            server = create_operator_server(config)

        assert server is mcp
        default_client.assert_called_once_with(config)
        create_mcp.assert_called_once_with(client, config)

    def test_create_operator_server_accepts_operator_backend_client_interface(self):
        provider = StaticCredentialProvider(
            ResolvedCredential(auth_mode="oauth", access_token="oauth-token")
        )
        config = MCPConfig(
            credential_provider=provider,
            namespace="demo",
            server_type="operator",
        )
        client: OperatorBackendClient = FakeOperatorBackendClient()
        mcp = Mock()

        with patch(
            "dispatch_cli.mcp.operator.server.create_operator_mcp",
            return_value=mcp,
        ) as create_mcp:
            server = create_operator_server(config, client=client)

        assert server is mcp
        create_mcp.assert_called_once_with(client, config)

    def test_run_operator_server_uses_injected_operator_backend_client(self):
        provider = StaticCredentialProvider(
            ResolvedCredential(auth_mode="oauth", access_token="oauth-token")
        )
        config = MCPConfig(
            credential_provider=provider,
            namespace="demo",
            server_type="operator",
        )
        client: OperatorBackendClient = FakeOperatorBackendClient()
        mcp = Mock()

        with patch(
            "dispatch_cli.mcp.operator.server.create_operator_mcp",
            return_value=mcp,
        ) as create_mcp:
            run_operator_server(config, client=client)

        create_mcp.assert_called_once_with(client, config)
        mcp.run.assert_called_once_with()
