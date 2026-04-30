"""Tests for local secrets helpers with injected keychain behavior."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from conftest import MemoryKeychainClient

from dispatch_cli.keychain import KeychainClient
from dispatch_cli.secrets import add_secret, get_secret, list_secrets, remove_secret


def _keychain() -> KeychainClient:
    return MemoryKeychainClient()


def _patch_secrets_paths(tmp_path: Path):
    dispatch_dir = tmp_path / ".dispatch"
    return patch.multiple(
        "dispatch_cli.secrets",
        DISPATCH_DIR=dispatch_dir,
        SECRETS_FILE=dispatch_dir / "secrets.yaml",
    )


class TestSecrets:
    def test_add_secret_uses_default_keychain_factory_when_not_injected(
        self, tmp_path: Path
    ):
        keychain = MemoryKeychainClient()

        with (
            _patch_secrets_paths(tmp_path),
            patch(
                "dispatch_cli.secrets.default_keychain_client", return_value=keychain
            ),
        ):
            assert add_secret(
                "OPENAI_API_KEY",
                "sk-test",
                use_keychain=True,
            )

            assert get_secret("OPENAI_API_KEY", keychain_client=keychain) == "sk-test"

    def test_add_secret_stores_keychain_reference_and_secret_value(
        self, tmp_path: Path
    ):
        keychain = MemoryKeychainClient()

        with _patch_secrets_paths(tmp_path):
            assert add_secret(
                "OPENAI_API_KEY",
                "sk-test",
                use_keychain=True,
                keychain_client=keychain,
            )

            assert get_secret("OPENAI_API_KEY", keychain_client=keychain) == "sk-test"

    def test_remove_secret_clears_config_and_keychain_value(self, tmp_path: Path):
        keychain = MemoryKeychainClient()

        with _patch_secrets_paths(tmp_path):
            add_secret(
                "OPENAI_API_KEY",
                "sk-test",
                use_keychain=True,
                keychain_client=keychain,
            )

            assert remove_secret("OPENAI_API_KEY", keychain_client=keychain) is True
            assert get_secret("OPENAI_API_KEY", keychain_client=keychain) is None

    def test_list_secrets_reports_keychain_backed_entries(self, tmp_path: Path):
        keychain = MemoryKeychainClient()

        with _patch_secrets_paths(tmp_path):
            add_secret(
                "OPENAI_API_KEY",
                "sk-test",
                use_keychain=True,
                keychain_client=keychain,
            )

            secrets = list_secrets(keychain_client=keychain)

        assert secrets == [
            {
                "name": "OPENAI_API_KEY",
                "storage": "keychain",
                "configured": True,
                "keychain_account": "dispatch-OPENAI_API_KEY",
            }
        ]
