"""Focused regressions for CLI cleanup/correctness fixes."""

from __future__ import annotations

import os
from unittest.mock import Mock, patch

import pytest
import typer

from dispatch_cli.commands.agent import check_required_mcp_servers
from dispatch_cli.commands.secrets import get_namespace_from_config


class TestSecretsNamespaceResolution:
    def test_get_namespace_from_config_logs_missing_namespace_once(self):
        logger = Mock()

        with (
            patch.dict(os.environ, {}, clear=True),
            patch("dispatch_cli.commands.secrets.get_logger", return_value=logger),
            patch(
                "dispatch_cli.commands.secrets.load_dispatch_config", return_value={}
            ),
        ):
            with pytest.raises(typer.Exit):
                get_namespace_from_config(None, verify=False)

        logger.error.assert_called_once()


class TestAgentValidationCleanup:
    def test_check_required_mcp_servers_ignores_malformed_installation_entries(self):
        logger = Mock()
        response = Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "installations": [
                {"installation_name": "installed-server"},
                {"unexpected": "shape"},
            ]
        }

        with (
            patch("dispatch_cli.commands.agent.get_logger", return_value=logger),
            patch(
                "dispatch_cli.commands.agent.requests.request", return_value=response
            ),
        ):
            result = check_required_mcp_servers(
                {"mcp_servers": ["missing-server"]},
                {"Authorization": "Bearer token"},
                "demo",
            )

        assert result is False
        logger.info.assert_any_call("Installed MCP servers in this namespace:")
