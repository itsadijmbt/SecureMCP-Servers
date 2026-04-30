"""Tests for the concrete macOS keychain adapter."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from dispatch_cli.keychain import (
    KeychainError,
    SecretToolKeychainClient,
    SecurityKeychainClient,
    default_keychain_client,
)


class TestSecurityKeychainClient:
    def test_get_generic_password_returns_secret_value(self):
        result = Mock(returncode=0, stdout="secret-value\n", stderr="")

        with (
            patch("dispatch_cli.keychain.sys.platform", "darwin"),
            patch("dispatch_cli.keychain.subprocess.run", return_value=result) as run,
        ):
            client = SecurityKeychainClient()
            value = client.get_generic_password("dispatch", "demo")

        assert value == "secret-value"
        run.assert_called_once_with(
            [
                "security",
                "find-generic-password",
                "-s",
                "dispatch",
                "-a",
                "demo",
                "-w",
            ],
            capture_output=True,
            text=True,
        )

    def test_get_generic_password_returns_none_when_item_is_missing(self):
        result = Mock(returncode=44, stdout="", stderr="")

        with (
            patch("dispatch_cli.keychain.sys.platform", "darwin"),
            patch("dispatch_cli.keychain.subprocess.run", return_value=result),
        ):
            client = SecurityKeychainClient()

            assert client.get_generic_password("dispatch", "missing") is None

    def test_set_generic_password_raises_on_failure(self):
        result = Mock(returncode=1, stdout="", stderr="failed")

        with (
            patch("dispatch_cli.keychain.sys.platform", "darwin"),
            patch("dispatch_cli.keychain.subprocess.run", return_value=result),
        ):
            client = SecurityKeychainClient()

            with pytest.raises(KeychainError):
                client.set_generic_password("dispatch", "demo", "secret-value")

    def test_delete_generic_password_returns_false_when_item_is_missing(self):
        result = Mock(returncode=44, stdout="", stderr="")

        with (
            patch("dispatch_cli.keychain.sys.platform", "darwin"),
            patch("dispatch_cli.keychain.subprocess.run", return_value=result),
        ):
            client = SecurityKeychainClient()

            assert client.delete_generic_password("dispatch", "missing") is False

    def test_delete_generic_password_returns_true_when_item_exists(self):
        result = Mock(returncode=0, stdout="", stderr="")

        with (
            patch("dispatch_cli.keychain.sys.platform", "darwin"),
            patch("dispatch_cli.keychain.subprocess.run", return_value=result),
        ):
            client = SecurityKeychainClient()

            assert client.delete_generic_password("dispatch", "demo") is True

    def test_run_raises_on_non_macos(self):
        client = SecurityKeychainClient()

        with patch("dispatch_cli.keychain.sys.platform", "linux"):
            with pytest.raises(
                KeychainError, match="macOS Keychain is only supported on macOS."
            ):
                client.get_generic_password("dispatch", "demo")


class TestSecretToolKeychainClient:
    def test_get_generic_password_returns_secret_value(self):
        result = Mock(returncode=0, stdout="secret-value\n", stderr="")

        with (
            patch("dispatch_cli.keychain.sys.platform", "linux"),
            patch("dispatch_cli.keychain.subprocess.run", return_value=result) as run,
        ):
            client = SecretToolKeychainClient()
            value = client.get_generic_password("dispatch", "demo")

        assert value == "secret-value"
        run.assert_called_once_with(
            [
                "secret-tool",
                "lookup",
                "service",
                "dispatch",
                "account",
                "demo",
            ],
            capture_output=True,
            text=True,
            input=None,
        )

    def test_get_generic_password_returns_none_when_item_is_missing(self):
        result = Mock(returncode=1, stdout="", stderr="")

        with (
            patch("dispatch_cli.keychain.sys.platform", "linux"),
            patch("dispatch_cli.keychain.subprocess.run", return_value=result),
        ):
            client = SecretToolKeychainClient()

            assert client.get_generic_password("dispatch", "missing") is None

    def test_get_generic_password_raises_when_lookup_fails_with_error_output(self):
        result = Mock(returncode=1, stdout="", stderr="keyring unavailable")

        with (
            patch("dispatch_cli.keychain.sys.platform", "linux"),
            patch("dispatch_cli.keychain.subprocess.run", return_value=result),
        ):
            client = SecretToolKeychainClient()

            with pytest.raises(
                KeychainError, match="Failed to load value from Linux secret store."
            ):
                client.get_generic_password("dispatch", "demo")

    def test_set_generic_password_stores_secret_value_via_stdin(self):
        result = Mock(returncode=0, stdout="", stderr="")

        with (
            patch("dispatch_cli.keychain.sys.platform", "linux"),
            patch("dispatch_cli.keychain.subprocess.run", return_value=result) as run,
        ):
            client = SecretToolKeychainClient()
            client.set_generic_password("dispatch", "demo", "secret-value")

        run.assert_called_once_with(
            [
                "secret-tool",
                "store",
                "--label",
                "Dispatch CLI (demo)",
                "service",
                "dispatch",
                "account",
                "demo",
            ],
            capture_output=True,
            text=True,
            input="secret-value",
        )

    def test_set_generic_password_raises_on_failure(self):
        result = Mock(returncode=1, stdout="", stderr="failed")

        with (
            patch("dispatch_cli.keychain.sys.platform", "linux"),
            patch("dispatch_cli.keychain.subprocess.run", return_value=result),
        ):
            client = SecretToolKeychainClient()

            with pytest.raises(KeychainError):
                client.set_generic_password("dispatch", "demo", "secret-value")

    def test_delete_generic_password_returns_false_when_item_is_missing(self):
        result = Mock(returncode=1, stdout="", stderr="")

        with (
            patch("dispatch_cli.keychain.sys.platform", "linux"),
            patch("dispatch_cli.keychain.subprocess.run", return_value=result),
        ):
            client = SecretToolKeychainClient()

            assert client.delete_generic_password("dispatch", "missing") is False

    def test_delete_generic_password_raises_when_clear_fails_with_error_output(self):
        result = Mock(returncode=1, stdout="", stderr="keyring unavailable")

        with (
            patch("dispatch_cli.keychain.sys.platform", "linux"),
            patch("dispatch_cli.keychain.subprocess.run", return_value=result),
        ):
            client = SecretToolKeychainClient()

            with pytest.raises(
                KeychainError, match="Failed to delete value from Linux secret store."
            ):
                client.delete_generic_password("dispatch", "demo")

    def test_delete_generic_password_returns_true_when_item_exists(self):
        result = Mock(returncode=0, stdout="", stderr="")

        with (
            patch("dispatch_cli.keychain.sys.platform", "linux"),
            patch("dispatch_cli.keychain.subprocess.run", return_value=result) as run,
        ):
            client = SecretToolKeychainClient()

            assert client.delete_generic_password("dispatch", "demo") is True

        run.assert_called_once_with(
            [
                "secret-tool",
                "clear",
                "service",
                "dispatch",
                "account",
                "demo",
            ],
            capture_output=True,
            text=True,
            input=None,
        )

    def test_run_raises_on_non_linux(self):
        client = SecretToolKeychainClient()

        with patch("dispatch_cli.keychain.sys.platform", "darwin"):
            with pytest.raises(
                KeychainError, match="Linux secret store is only supported on Linux."
            ):
                client.get_generic_password("dispatch", "demo")

    def test_run_raises_when_linux_command_cannot_start(self):
        client = SecretToolKeychainClient()

        with (
            patch("dispatch_cli.keychain.sys.platform", "linux"),
            patch(
                "dispatch_cli.keychain.subprocess.run",
                side_effect=OSError("missing binary"),
            ),
        ):
            with pytest.raises(
                KeychainError,
                match="Linux secret store command failed to start.",
            ):
                client.get_generic_password("dispatch", "demo")


class TestDefaultKeychainClient:
    def test_uses_security_client_on_macos(self):
        with patch("dispatch_cli.keychain.sys.platform", "darwin"):
            client = default_keychain_client()

        assert isinstance(client, SecurityKeychainClient)

    def test_uses_secret_tool_client_on_linux(self):
        with patch("dispatch_cli.keychain.sys.platform", "linux"):
            client = default_keychain_client()

        assert isinstance(client, SecretToolKeychainClient)

    def test_raises_on_unsupported_platform(self):
        with patch("dispatch_cli.keychain.sys.platform", "win32"):
            with pytest.raises(
                KeychainError,
                match="System secure-store support is only available on macOS and Linux.",
            ):
                default_keychain_client()
