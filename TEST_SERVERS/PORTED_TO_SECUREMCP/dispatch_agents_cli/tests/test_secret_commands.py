"""Tests for local secret CLI behavior across supported platforms."""

from __future__ import annotations

from unittest.mock import patch

from typer.testing import CliRunner

from dispatch_cli.main import app


class TestLocalSecretCommands:
    def test_local_add_secret_uses_secure_store_on_linux(self, runner: CliRunner):
        with (
            patch("dispatch_cli.commands.secrets.sys.platform", "linux"),
            patch(
                "dispatch_cli.commands.secrets.add_local_secret", return_value=True
            ) as add_secret,
        ):
            result = runner.invoke(
                app,
                ["secret", "local", "add", "OPENAI_API_KEY", "--value", "sk-test"],
            )

        assert result.exit_code == 0
        add_secret.assert_called_once_with(
            "OPENAI_API_KEY",
            "sk-test",
            use_keychain=True,
        )
