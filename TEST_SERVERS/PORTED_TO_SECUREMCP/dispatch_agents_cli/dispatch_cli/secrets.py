"""Local secrets management for Dispatch development mode.

Secrets are stored in ~/.dispatch/secrets.yaml with references to either:
1. System secure-store items (preferred, secure)
2. Raw values (allowed but warns on access)

Example secrets.yaml:
    OPENAI_API_KEY:
      keychain: dispatch-OPENAI_API_KEY
    ANTHROPIC_API_KEY:
      value: sk-ant-...  # Will warn on access
    /shared/db-password:
      keychain: dispatch-shared-db-password
"""

import os
from pathlib import Path
from typing import Any

import yaml

from dispatch_cli.keychain import (
    KeychainClient,
    KeychainError,
    default_keychain_client,
)
from dispatch_cli.logger import get_logger

# Config paths
DISPATCH_DIR = Path.home() / ".dispatch"
SECRETS_FILE = DISPATCH_DIR / "secrets.yaml"

# Keychain service name prefix
KEYCHAIN_SERVICE = "dispatch"


def _resolve_keychain_client(
    keychain_client: KeychainClient | None = None,
) -> KeychainClient:
    return keychain_client or default_keychain_client()


def _get_from_keychain(
    account: str,
    *,
    keychain_client: KeychainClient | None = None,
) -> str | None:
    """Get a secret from the system secure store.

    Args:
        account: The account/item name in Keychain

    Returns:
        The secret value, or None if not found
    """
    try:
        return _resolve_keychain_client(keychain_client).get_generic_password(
            KEYCHAIN_SERVICE,
            account,
        )
    except KeychainError:
        return None


def _set_in_keychain(
    account: str,
    value: str,
    *,
    keychain_client: KeychainClient | None = None,
) -> bool:
    """Store a secret in the system secure store.

    Args:
        account: The account/item name in Keychain
        value: The secret value to store

    Returns:
        True if successful, False otherwise
    """
    try:
        _resolve_keychain_client(keychain_client).set_generic_password(
            KEYCHAIN_SERVICE,
            account,
            value,
        )
        return True
    except KeychainError:
        return False


def _delete_from_keychain(
    account: str,
    *,
    keychain_client: KeychainClient | None = None,
) -> bool:
    """Delete a secret from the system secure store.

    Args:
        account: The account/item name in Keychain

    Returns:
        True if successful (or item didn't exist), False on error
    """
    try:
        return _resolve_keychain_client(keychain_client).delete_generic_password(
            KEYCHAIN_SERVICE,
            account,
        )
    except KeychainError:
        return False


def _load_secrets_config() -> dict[str, Any]:
    """Load the secrets configuration from ~/.dispatch/secrets.yaml.

    Returns:
        Dict of secret_name -> config (keychain or value)
    """
    if not SECRETS_FILE.exists():
        return {}

    try:
        with open(SECRETS_FILE) as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_secrets_config(config: dict[str, Any]) -> None:
    """Save the secrets configuration to ~/.dispatch/secrets.yaml.

    Args:
        config: Dict of secret_name -> config
    """
    DISPATCH_DIR.mkdir(parents=True, exist_ok=True)

    with open(SECRETS_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=True)


def get_secret(
    name: str,
    warn_on_raw: bool = True,
    *,
    keychain_client: KeychainClient | None = None,
) -> str | None:
    """Get a secret by name from the local secrets store.

    Checks ~/.dispatch/secrets.yaml for the secret config, then:
    1. If keychain reference: fetches from the system secure store
    2. If raw value: returns value (with warning if warn_on_raw=True)
    3. Falls back to environment variable

    Args:
        name: Secret name (e.g., "OPENAI_API_KEY" or "/shared/db-password")
        warn_on_raw: Whether to warn when accessing raw (non-keychain) secrets

    Returns:
        The secret value, or None if not found
    """
    logger = get_logger()
    config = _load_secrets_config()

    secret_config = config.get(name)

    if secret_config:
        # Check for keychain reference
        if "keychain" in secret_config:
            keychain_account = secret_config["keychain"]
            value = _get_from_keychain(
                keychain_account,
                keychain_client=keychain_client,
            )
            if value:
                return value
            else:
                logger.debug(
                    f"Secret '{name}' configured for secure store but not found"
                )

        # Check for raw value
        if "value" in secret_config:
            if warn_on_raw:
                logger.warning(
                    f"⚠️  Secret '{name}' is stored as raw text in ~/.dispatch/secrets.yaml\n"
                    f"    For better security: dispatch secrets local add {name} --keychain"
                )
            return secret_config["value"]

    # Fallback to environment variable
    env_value = os.environ.get(name)
    if env_value:
        return env_value

    return None


def get_all_secrets(warn_on_raw: bool = True) -> dict[str, str]:
    """Get all configured secrets from the local secrets store.

    Args:
        warn_on_raw: Whether to warn when accessing raw secrets

    Returns:
        Dict of secret_name -> value for all configured secrets
    """
    config = _load_secrets_config()
    result = {}

    for name in config:
        value = get_secret(name, warn_on_raw=warn_on_raw)
        if value:
            result[name] = value

    return result


def add_secret(
    name: str,
    value: str,
    use_keychain: bool = True,
    *,
    keychain_client: KeychainClient | None = None,
) -> bool:
    """Add or update a secret in the local secrets store.

    Args:
        name: Secret name (e.g., "OPENAI_API_KEY" or "/shared/db-password")
        value: The secret value
        use_keychain: If True, store in the secure store; if False, store as raw value

    Returns:
        True if successful, False otherwise
    """
    logger = get_logger()
    config = _load_secrets_config()

    if use_keychain:
        # Generate keychain account name from secret name
        # Replace / with - for path-style secrets
        keychain_account = f"dispatch-{name.replace('/', '-').strip('-')}"

        if _set_in_keychain(
            keychain_account,
            value,
            keychain_client=keychain_client,
        ):
            config[name] = {"keychain": keychain_account}
            _save_secrets_config(config)
            logger.info(f"✓ Secret '{name}' stored in the system secure store")
            return True
        else:
            logger.error(f"Failed to store '{name}' in the system secure store")
            return False
    else:
        # Store as raw value (with warning)
        config[name] = {"value": value}
        _save_secrets_config(config)
        logger.warning(
            f"⚠️  Secret '{name}' stored as raw text in ~/.dispatch/secrets.yaml\n"
            f"    Consider using --keychain for better security"
        )
        return True


def remove_secret(
    name: str,
    *,
    keychain_client: KeychainClient | None = None,
) -> bool:
    """Remove a secret from the local secrets store.

    Removes from both secrets.yaml and the system secure store if applicable.

    Args:
        name: Secret name to remove

    Returns:
        True if removed, False if not found
    """
    logger = get_logger()
    config = _load_secrets_config()

    if name not in config:
        logger.warning(f"Secret '{name}' not found")
        return False

    secret_config = config[name]

    # Remove from Keychain if it was stored there
    if "keychain" in secret_config:
        _delete_from_keychain(
            secret_config["keychain"],
            keychain_client=keychain_client,
        )

    # Remove from config
    del config[name]
    _save_secrets_config(config)

    logger.info(f"✓ Secret '{name}' removed")
    return True


def list_secrets(
    *,
    keychain_client: KeychainClient | None = None,
) -> list[dict[str, Any]]:
    """List all configured secrets with their storage type.

    Returns:
        List of dicts with name, storage_type, and configured status
    """
    config = _load_secrets_config()
    result = []

    for name, secret_config in sorted(config.items()):
        if "keychain" in secret_config:
            # Check if actually in the secure store
            value = _get_from_keychain(
                secret_config["keychain"],
                keychain_client=keychain_client,
            )
            result.append(
                {
                    "name": name,
                    "storage": "keychain",
                    "configured": value is not None,
                    "keychain_account": secret_config["keychain"],
                }
            )
        elif "value" in secret_config:
            result.append(
                {
                    "name": name,
                    "storage": "raw",
                    "configured": True,
                }
            )

    return result


def load_secrets_to_env(warn_on_raw: bool = True) -> dict[str, str]:
    """Load all secrets and set them as environment variables.

    This is called by the router on startup to make secrets available.

    Args:
        warn_on_raw: Whether to warn when accessing raw secrets

    Returns:
        Dict of secrets that were loaded
    """
    secrets = get_all_secrets(warn_on_raw=warn_on_raw)

    for name, value in secrets.items():
        # Only set if not already in environment
        if name not in os.environ:
            os.environ[name] = value

    return secrets


def get_secret_sources(
    required_secrets: list[str] | None = None,
    agent_env_path: str | None = None,
) -> list[dict[str, Any]]:
    """Get the source of each secret for display purposes.

    Checks multiple sources in order of precedence:
    1. Environment variables (highest precedence)
    2. Agent's local .env file (if agent_env_path provided)
    3. Centralized secrets.yaml (Keychain or raw)

    Args:
        required_secrets: List of secret names to check. If None, returns all configured secrets.
        agent_env_path: Path to agent's .env file (optional)

    Returns:
        List of dicts with keys: name, source, storage_type, configured
        - source: "env", "agent_env", "keychain", "raw", or None (not found)
        - storage_type: More detailed info like keychain account name
    """
    config = _load_secrets_config()
    results = []

    # Parse agent's .env file if provided
    agent_env_vars: dict[str, str] = {}
    if agent_env_path and os.path.exists(agent_env_path):
        with open(agent_env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    agent_env_vars[key.strip()] = value.strip()

    # Determine which secrets to check
    secrets_to_check = required_secrets or list(config.keys())

    # Also include any secrets from agent's .env
    for key in agent_env_vars:
        if key not in secrets_to_check:
            secrets_to_check.append(key)

    for name in secrets_to_check:
        result: dict[str, Any] = {
            "name": name,
            "source": None,
            "storage_type": None,
            "configured": False,
        }

        # Check precedence order

        # 1. Environment variable (highest precedence)
        if name in os.environ:
            result["source"] = "env"
            result["storage_type"] = "environment variable"
            result["configured"] = True
            results.append(result)
            continue

        # 2. Agent's local .env file
        if name in agent_env_vars:
            result["source"] = "agent_env"
            result["storage_type"] = "agent .env file"
            result["configured"] = True
            results.append(result)
            continue

        # 3. Centralized secrets.yaml
        secret_config = config.get(name)
        if secret_config:
            if "keychain" in secret_config:
                keychain_account = secret_config["keychain"]
                keychain_value = _get_from_keychain(keychain_account)
                if keychain_value:
                    result["source"] = "keychain"
                    result["storage_type"] = f"system secure store ({keychain_account})"
                    result["configured"] = True
                else:
                    result["source"] = "keychain"
                    result["storage_type"] = (
                        f"secure-store entry missing ({keychain_account})"
                    )
                    result["configured"] = False
            elif "value" in secret_config:
                result["source"] = "raw"
                result["storage_type"] = "raw text in secrets.yaml (⚠️ insecure)"
                result["configured"] = True

        results.append(result)

    return results


def print_secret_sources(
    required_secrets: list[str] | None = None,
    agent_env_path: str | None = None,
) -> None:
    """Print the source of each secret in a formatted table.

    Args:
        required_secrets: List of secret names to check
        agent_env_path: Path to agent's .env file (optional)
    """
    logger = get_logger()
    sources = get_secret_sources(required_secrets, agent_env_path)

    if not sources:
        logger.info("No secrets configured.")
        return

    logger.info("Secrets:")
    for secret in sources:
        name = secret["name"]
        storage_type = secret["storage_type"]
        configured = secret["configured"]

        if configured:
            status = "✓"
            style = "green"
        else:
            status = "✗"
            style = "red"

        if storage_type:
            logger.info(f"  [{style}]{status}[/{style}] {name} ← {storage_type}")
        else:
            logger.info(f"  [{style}]{status}[/{style}] {name} ← [dim]not found[/dim]")
