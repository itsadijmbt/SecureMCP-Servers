"""Shared system secure-store adapters for CLI features."""

from __future__ import annotations

import subprocess
import sys
from typing import Protocol

KEYCHAIN_ITEM_NOT_FOUND = 44
SECRET_TOOL_ITEM_NOT_FOUND = 1


class KeychainError(RuntimeError):
    """Raised when a keychain command fails."""


class KeychainClient(Protocol):
    """Generic password operations supported by the CLI."""

    def get_generic_password(self, service: str, account: str) -> str | None:
        """Return the stored password if present."""

    def set_generic_password(self, service: str, account: str, password: str) -> None:
        """Persist or update the stored password."""

    def delete_generic_password(self, service: str, account: str) -> bool:
        """Delete the stored password.

        Returns False when the item does not exist.
        """


class SecurityKeychainClient:
    """Concrete keychain client backed by the macOS `security` tool."""

    def __init__(self, executable: str = "security"):
        self.executable = executable

    def get_generic_password(self, service: str, account: str) -> str | None:
        result = self._run(
            [
                "find-generic-password",
                "-s",
                service,
                "-a",
                account,
                "-w",
            ]
        )
        if result.returncode == 0:
            return result.stdout.rstrip("\n")
        if result.returncode == KEYCHAIN_ITEM_NOT_FOUND:
            return None
        raise KeychainError("Failed to load value from macOS Keychain.")

    def set_generic_password(self, service: str, account: str, password: str) -> None:
        result = self._run(
            [
                "add-generic-password",
                "-U",
                "-s",
                service,
                "-a",
                account,
                "-w",
                password,
            ]
        )
        if result.returncode != 0:
            raise KeychainError("Failed to save value to macOS Keychain.")

    def delete_generic_password(self, service: str, account: str) -> bool:
        result = self._run(
            [
                "delete-generic-password",
                "-s",
                service,
                "-a",
                account,
            ]
        )
        if result.returncode == 0:
            return True
        if result.returncode == KEYCHAIN_ITEM_NOT_FOUND:
            return False
        raise KeychainError("Failed to delete value from macOS Keychain.")

    def _run(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        if sys.platform != "darwin":
            raise KeychainError("macOS Keychain is only supported on macOS.")
        try:
            return subprocess.run(
                [self.executable, *args],
                capture_output=True,
                text=True,
            )
        except OSError as exc:
            raise KeychainError("macOS Keychain command failed to start.") from exc


class SecretToolKeychainClient:
    """Concrete keychain client backed by Linux `secret-tool`."""

    def __init__(self, executable: str = "secret-tool") -> None:
        self.executable = executable

    def get_generic_password(self, service: str, account: str) -> str | None:
        result = self._run(
            [
                "lookup",
                "service",
                service,
                "account",
                account,
            ]
        )
        if result.returncode == 0:
            return result.stdout.rstrip("\n")
        if (
            result.returncode == SECRET_TOOL_ITEM_NOT_FOUND
            and not result.stderr.strip()
        ):
            return None
        raise KeychainError("Failed to load value from Linux secret store.")

    def set_generic_password(self, service: str, account: str, password: str) -> None:
        result = self._run(
            [
                "store",
                "--label",
                f"Dispatch CLI ({account})",
                "service",
                service,
                "account",
                account,
            ],
            input_text=password,
        )
        if result.returncode != 0:
            raise KeychainError("Failed to save value to Linux secret store.")

    def delete_generic_password(self, service: str, account: str) -> bool:
        result = self._run(
            [
                "clear",
                "service",
                service,
                "account",
                account,
            ]
        )
        if result.returncode == 0:
            return True
        if (
            result.returncode == SECRET_TOOL_ITEM_NOT_FOUND
            and not result.stderr.strip()
        ):
            return False
        raise KeychainError("Failed to delete value from Linux secret store.")

    def _run(
        self,
        args: list[str],
        *,
        input_text: str | None = None,
    ) -> subprocess.CompletedProcess[str]:
        if not sys.platform.startswith("linux"):
            raise KeychainError("Linux secret store is only supported on Linux.")
        try:
            return subprocess.run(
                [self.executable, *args],
                capture_output=True,
                text=True,
                input=input_text,
            )
        except OSError as exc:
            raise KeychainError("Linux secret store command failed to start.") from exc


def default_keychain_client() -> KeychainClient:
    """Build the default secure-store client for the current platform."""
    if sys.platform == "darwin":
        return SecurityKeychainClient()
    if sys.platform.startswith("linux"):
        return SecretToolKeychainClient()
    raise KeychainError(
        "System secure-store support is only available on macOS and Linux."
    )
