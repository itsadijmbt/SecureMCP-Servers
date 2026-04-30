"""Shared utility functions for dispatch CLI."""

import copy
import os
import re
from collections.abc import Callable
from typing import Any

import tomlkit
import typer
import yaml
from dispatch_agents.config import ResourceConfig, VolumeConfig
from tomlkit.items import Item

from dispatch_cli.logger import get_logger

# URL constants for different contexts
LOCAL_ROUTER_PORT = int(os.getenv("LOCAL_ROUTER_PORT", "8080"))
LOCAL_ROUTER_URL = "http://localhost"
DISPATCH_API_BASE = os.getenv("DISPATCH_DEPLOY_URL", "https://dispatchagents.ai")
DISPATCH_DEPLOY_URL = DISPATCH_API_BASE + "/api/unstable"

DISPATCH_DIR = ".dispatch"
DISPATCH_YAML = "dispatch.yaml"
DISPATCH_LISTENER_MODULE = "__dispatch_listener__"
DISPATCH_LISTENER_FILE = f"{DISPATCH_LISTENER_MODULE}.py"

# LLM provider API keys managed by the Dispatch LLM gateway.
# When present in dispatch.yaml secrets, these serve as fallback credentials
# if the namespace has no platform-level LLM provider configured.
LLM_PROVIDER_KEY_NAMES = {
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "COHERE_API_KEY",
    "MISTRAL_API_KEY",
}
AGENT_DIR = "."

DEFAULT_BASE_IMAGE = "python:3.13-slim"

# Supported base images with their Python versions for wheel downloads
SUPPORTED_BASE_IMAGES = {
    "python:3.11-slim": "3.11",
    "python:3.12-slim": "3.12",
    "python:3.12-slim-trixie": "3.12",
    "python:3.13-slim": "3.13",
}

DISPATCH_REQUIREMENTS = [
    "grpcio",
    "protobuf",
    "pydantic",
    "tomlkit",
    "pyyaml",
    "aiohttp",
    "asyncio",
]
# Legacy constant for backwards compatibility - prefer get_sdk_dependency() function
SDK_DEPENDENCY = os.getenv("SDK_DEPENDENCY", "dispatch-agents")


def get_sdk_dependency() -> str:
    """Get the SDK dependency string for agent projects.

    Defaults to the published PyPI package so `dispatch agent init` does not
    send users through a GitHub install flow. An explicit `SDK_DEPENDENCY`
    environment override still wins for local development and testing.

    Returns:
        SDK dependency string for use with 'uv add'
    """
    # Check for environment override first
    if os.getenv("SDK_DEPENDENCY"):
        return os.getenv("SDK_DEPENDENCY", SDK_DEPENDENCY)

    return SDK_DEPENDENCY


DEFAULT_SYSTEM_PACKAGES = ["curl", "unzip", "wget", "git", "ssh"]

INTERACTIVE_CONFIG_OPTIONS: dict[str, dict] = {
    "namespace": {
        "text": "Namespace for agent deployment (required - contact your org admin if it doesn't exist)",
        "default_from_context": True,  # Special flag to compute default from context
    },
    "entrypoint": {
        "text": "Entrypoint Python file (with agent handlers)",
        "default": "agent.py",
    },
    "base_image": {
        "text": "Base Docker image",
        "default": DEFAULT_BASE_IMAGE,
    },
    "system_packages": {
        "text": "Additional system packages (space-separated)",
        "default": "",
        "value_proc": lambda x: x.split() if isinstance(x, str) else x,
    },
}

DEFAULT_CONFIG: dict[str, object | None] = {
    "namespace": None,
    "entrypoint": None,
    "base_image": None,
    "system_packages": None,
    "local_dependencies": None,
    "agent_name": None,
    "env": None,  # plain env vars (like {"LOG_LEVEL": "debug"})
    "vars": None,  # config variables accessible via dispatch_agents.config.vars (not injected as env vars)
    "secrets": None,  # list of objects with name/secret_id for secrets manager paths (like [{"name": "OPENAI_API_KEY", "secret_id": "/shared/openai-api-key"}])
    "volumes": None,  # list of volume objects (like [{"name": "data", "mountPath": "/data", "mode": "read_write_many"}])
    "mcp_servers": None,  # list of MCP server configs (e.g., [{"server": "com.datadoghq.mcp"}])
    "resources": None,  # resource limits (like {"cpu": 512, "memory": 1024})
    "network": None,  # network egress restrictions (like {"egress": {"allow_domains": [{"match_name": "api.openai.com"}]}})
}


def _to_builtin(value):
    if isinstance(value, Item):
        try:
            inner = value.unwrap()
        except AttributeError:
            inner = value.value
        if inner is value:
            return inner
        return _to_builtin(inner)
    if isinstance(value, dict):
        return {str(k): _to_builtin(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_builtin(v) for v in value]
    return value


def read_pyproject(path: str) -> tomlkit.TOMLDocument | None:
    """Load pyproject.toml if present."""
    logger = get_logger()
    pyproject_path = os.path.join(path, "pyproject.toml")
    if not os.path.exists(pyproject_path):
        logger.warning("pyproject.toml not found.")
        raise typer.Exit(1)

    try:
        with open(pyproject_path, "rb") as fh:
            return tomlkit.load(fh)
    except Exception as exc:  # pragma: no cover - surface error to caller
        logger.error(f"Could not parse pyproject.toml: {exc}")
        raise typer.Exit(1)


def read_project_config(
    path: str, pyproject: tomlkit.TOMLDocument | None = None
) -> dict:
    """Read configuration from pyproject.toml [tool.dispatch] section."""
    config: dict[str, object] = {}
    document = pyproject or read_pyproject(path)
    if not document:
        return config

    dispatch_config = document.get("tool", {}).get("dispatch", {}) or {}
    allowed_keys = set(DEFAULT_CONFIG.keys())
    unsupported = set(dispatch_config.keys()) - allowed_keys
    if unsupported:
        logger = get_logger()
        logger.warning(
            f"Unsupported keys in [tool.dispatch]: {', '.join(sorted(unsupported))}"
        )

    for key in allowed_keys:
        if key in dispatch_config:
            config[key] = _to_builtin(dispatch_config[key])

    return config


def _find_dispatch_yaml(path: str) -> str | None:
    """Return the path to the dispatch config file, or None if not found."""
    hidden = os.path.join(path, ".dispatch.yaml")
    if os.path.exists(hidden):
        raise RuntimeError(
            ".dispatch.yaml is no longer supported; rename it to dispatch.yaml"
        )
    candidate = os.path.join(path, DISPATCH_YAML)
    if os.path.exists(candidate):
        return candidate
    return None


def read_dispatch_yaml(path: str) -> dict:
    """Read configuration overrides from dispatch.yaml."""
    yaml_path = _find_dispatch_yaml(path)
    if yaml_path is None:
        return {}

    filename = os.path.basename(yaml_path)

    with open(yaml_path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    if not isinstance(data, dict):
        raise typer.BadParameter(
            f"{filename} must contain a mapping, found {type(data).__name__}"
        )

    # Validate against allowed keys - error on unknown keys
    allowed_keys = set(DEFAULT_CONFIG.keys())
    unknown_keys = set(data.keys()) - allowed_keys
    if unknown_keys:
        raise typer.BadParameter(
            f"Unknown keys in {filename}: {', '.join(sorted(unknown_keys))}. "
            f"Allowed keys are: {', '.join(sorted(allowed_keys))}"
        )

    return data


def save_dispatch_yaml(path: str, config: dict) -> None:
    """Persist configuration values to dispatch.yaml."""
    # Write to whichever file already exists; default to dispatch.yaml for new projects
    yaml_path = _find_dispatch_yaml(path) or os.path.join(path, DISPATCH_YAML)
    payload = _config_for_yaml(config)
    with open(yaml_path, "w", encoding="utf-8") as fh:
        yaml.safe_dump(
            payload,
            fh,
            allow_unicode=False,
            sort_keys=False,
            default_flow_style=False,
        )

    logger = get_logger()
    logger.debug(f"Saved configuration to {yaml_path}")


def _config_for_yaml(config: dict) -> dict:
    """Return a serializable subset of config for dispatch.yaml."""
    keys = DEFAULT_CONFIG.keys()
    always_include = {"namespace", "agent_name", "entrypoint", "base_image"}

    payload: dict[str, object] = {}
    for key in keys:
        value = config.get(key)
        if key in always_include:
            if value is not None:
                payload[key] = value
            continue

        if value is None:
            continue

        if key == "system_packages":
            # Always save system_packages to preserve user's explicit choice
            # Filter out defaults but keep empty list if user explicitly chose no extras
            extras = [
                pkg
                for pkg in _coerce_string_list(value)
                if pkg not in DEFAULT_SYSTEM_PACKAGES
            ]
            payload[key] = extras  # Save empty list or list with extras
            continue

        if isinstance(value, list | dict) and not value:
            continue

        payload[key] = value

    return payload


def prompt_for_missing_config(config: dict, assume_yes=False, path: str = ".") -> dict:
    """Prompt user for any missing interactive config options."""
    logger = get_logger()
    updated_config = copy.deepcopy(config)
    logger.info(
        "Configuration will be saved to dispatch.yaml; edit that file to adjust later."
    )

    for option_name, option_def in INTERACTIVE_CONFIG_OPTIONS.items():
        processor: Callable[[Any], Any] = option_def.get("value_proc", lambda x: x)  # type: ignore

        if updated_config.get(option_name) is not None:
            continue

        # Compute context-specific defaults
        default_value = option_def.get("default")
        if option_def.get("default_from_context"):
            if option_name == "namespace":
                # Use parent directory name as default namespace
                # Get the parent of the agent directory
                abs_path = os.path.abspath(path)
                parent_dir = os.path.basename(os.path.dirname(abs_path))
                default_value = parent_dir

        if assume_yes:
            value = default_value
        else:
            # Build prompt kwargs, excluding special keys
            prompt_kwargs = {
                k: v
                for k, v in option_def.items()
                if k not in ("value_proc", "default_from_context")
            }
            if default_value is not None:
                prompt_kwargs["default"] = default_value
            value = typer.prompt(**prompt_kwargs)  # type: ignore
        updated_config[option_name] = processor(value)

    return updated_config


def _coerce_string_list(value: object | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        value = value.split()
    if isinstance(value, list):
        items = value
    else:
        try:
            items = list(value)  # type: ignore
        except TypeError as exc:  # pragma: no cover - defensive
            raise typer.BadParameter(
                f"Expected list-like value, received {value!r}"
            ) from exc
    return [str(item) for item in items if str(item)]


def _merge_system_packages(value: object | None) -> list[str]:
    merged: list[str] = []
    for pkg in DEFAULT_SYSTEM_PACKAGES:
        if pkg not in merged:
            merged.append(pkg)
    for pkg in _coerce_string_list(value):
        if pkg not in merged:
            merged.append(pkg)
    return merged


def _coerce_dict(key, value: object | None) -> dict[str, str]:
    if value is None:
        return {}
    if isinstance(value, dict):
        return {str(k): str(v) for k, v in value.items()}
    raise typer.BadParameter(
        f"{key} must be a mapping of name → path, received {type(value).__name__}"
    )


def _validate_env(env: dict[str, Any] | None) -> dict[str, str] | None:
    """Validate that all env values are strings.

    YAML parses unquoted ``false`` as bool, ``123`` as int, etc.
    Env vars must be strings — tell users to wrap values in quotes.
    """
    if not env:
        return None
    if not isinstance(env, dict):
        raise typer.BadParameter(
            f"env must be a mapping of name → value, received {type(env).__name__}"
        )
    non_string = {
        k: (type(v).__name__, v) for k, v in env.items() if not isinstance(v, str)
    }
    if non_string:
        examples = ", ".join(
            f'{k} (got {t}, use: {k}: "{v}")'
            for k, (t, v) in sorted(non_string.items())
        )
        raise typer.BadParameter(f"All env values must be strings. {examples}")
    return env


def _apply_default_values(
    config: dict, pyproject: tomlkit.TOMLDocument | None, project_path: str
) -> dict:
    updated = copy.deepcopy(config)

    if not updated.get("base_image"):
        updated["base_image"] = DEFAULT_BASE_IMAGE

    updated["system_packages"] = _merge_system_packages(updated.get("system_packages"))
    updated["local_dependencies"] = _coerce_dict(
        "local_dependencies", updated.get("local_dependencies")
    )
    # Validate env values are strings (YAML parses false/true/123 as non-strings)
    updated["env"] = _validate_env(updated.get("env"))

    # Secrets as list - no coercion needed, YAML gives us the right structure
    if updated.get("secrets") is None:
        updated["secrets"] = []

    # Handle volumes configuration
    updated["volumes"] = _coerce_volumes(updated.get("volumes"))

    # Handle resources configuration
    updated["resources"] = _coerce_resources(updated.get("resources"))

    updated["dependency_strategy"] = str(
        updated.get("dependency_strategy") or "auto"
    ).lower()
    updated["dependency_file"] = updated.get("dependency_file")

    if not updated.get("agent_name"):
        updated["agent_name"] = derive_agent_name(project_path, updated, pyproject)

    return updated


def _coerce_resources(resources: dict[str, Any] | None) -> dict[str, Any] | None:
    """Validate and normalize resources configuration.

    Validates the resource configuration using the ResourceConfig Pydantic model
    and ensures CPU/memory form a valid combination.

    Args:
        resources: Resource configuration dict with limits sub-object

    Returns:
        Validated resource dict with K8s-style strings, or None if not specified
    """
    if not resources:
        return None

    if not isinstance(resources, dict):
        raise typer.BadParameter(
            f"resources must be an object with limits, got: {type(resources).__name__}"
        )

    # Validate using Pydantic model (combination validation happens automatically)
    try:
        resource_config = ResourceConfig(**resources)

        # Return only non-None values (keep K8s-style strings)
        if not resource_config.limits:
            return None

        limits_dict: dict[str, str] = {}
        if resource_config.limits.cpu is not None:
            limits_dict["cpu"] = resource_config.limits.cpu
        if resource_config.limits.memory is not None:
            limits_dict["memory"] = resource_config.limits.memory

        return {"limits": limits_dict} if limits_dict else None
    except ValueError as e:
        raise typer.BadParameter(f"resources validation error: {e}")


def _coerce_volumes(volumes: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """Validate and normalize volumes configuration.

    Validates each volume using the VolumeConfig Pydantic model.

    Args:
        volumes: List of volume configuration dicts

    Returns:
        Validated list of volume dicts
    """
    if not volumes:
        return []

    if not isinstance(volumes, list):
        raise typer.BadParameter(
            f"volumes must be a list of volume configurations, got: {type(volumes).__name__}"
        )

    # Validate each volume using Pydantic model
    validated_volumes: list[dict[str, Any]] = []
    for i, vol in enumerate(volumes):
        if not isinstance(vol, dict):
            raise typer.BadParameter(
                f"volumes[{i}] must be an object with name, mountPath, and mode"
            )

        # Validate required fields
        if "name" not in vol:
            raise typer.BadParameter(f"volumes[{i}] is missing required field 'name'")
        if "mountPath" not in vol:
            raise typer.BadParameter(
                f"volumes[{i}] is missing required field 'mountPath'"
            )
        if "mode" not in vol:
            raise typer.BadParameter(f"volumes[{i}] is missing required field 'mode'")

        # Validate using Pydantic model
        try:
            volume_config = VolumeConfig(**vol)
            validated_volumes.append(
                {
                    "name": volume_config.name,
                    "mountPath": volume_config.mount_path,
                    "mode": volume_config.mode.value,
                }
            )
        except Exception as e:
            raise typer.BadParameter(f"volumes[{i}] validation error: {e}")

    return validated_volumes


def load_dispatch_config(path: str, apply_defaults: bool = True) -> dict:
    """Load dispatch configuration, merging defaults, pyproject, and dispatch.yaml."""
    pyproject = read_pyproject(path)
    config = copy.deepcopy(DEFAULT_CONFIG)
    config.update(read_project_config(path, pyproject))
    config.update(read_dispatch_yaml(path))

    if apply_defaults:
        return _apply_default_values(config, pyproject, path)

    # Minimal normalization for callers that want raw values
    if config.get("system_packages") is not None:
        config["system_packages"] = _coerce_string_list(config["system_packages"])
    if config.get("local_dependencies") is None:
        config["local_dependencies"] = {}
    return config


def configure_dispatch_project(path: str, assume_yes=False) -> dict[str, Any]:
    """Interactive configuration flow used by `dispatch agent init`."""
    pyproject = read_pyproject(path)
    config = copy.deepcopy(DEFAULT_CONFIG)
    config.update(read_project_config(path, pyproject))
    config.update(read_dispatch_yaml(path))

    config = prompt_for_missing_config(config, assume_yes, path)
    config = _apply_default_values(config, pyproject, path)
    save_dispatch_yaml(path, config)
    return config


def has_python_reqs(path: str, warn=True) -> bool:
    """Validate that the path looks like a Python project we can work with."""

    pyproject_exists = os.path.exists(os.path.join(path, "pyproject.toml"))
    #  requirements_exists = os.path.exists(os.path.join(path, "requirements.txt"))

    if not pyproject_exists:  # or requirements_exists):
        if warn:
            logger = get_logger()
            logger.warning(
                "Could not find pyproject.toml or requirements.txt. Assuming no extra python dependencies."
            )
            logger.info("Tip: Use 'uv init --bare' to create pyproject.toml easily.")
        return False
    return True


def check_dotenv_has_all_secrets(path, config) -> None:
    """Warn if secret defined in dispatch.yaml is not set in .env"""
    logger = get_logger()
    secrets = config.get("secrets") or []
    if not secrets:
        return
    dotenv_path = os.path.join(path, ".env")
    existing_env_vars = set()

    if os.path.exists(dotenv_path):
        with open(dotenv_path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    var_name = line.split("=", 1)[0].strip()
                    existing_env_vars.add(var_name)

    for secret in secrets:
        secret_var = secret["name"]
        # LLM keys are injected by the proxy — don't require them in .env
        if secret_var in LLM_PROVIDER_KEY_NAMES:
            continue
        if secret_var not in existing_env_vars:
            logger.warning(
                f"Secret environment variable '{secret_var}' is defined in dispatch.yaml but not set in .env, please set it in order to use it for local testing."
            )


def _add_secrets_to_yaml(path: str, config: dict, secret_names: list[str]) -> None:
    """Append secret entries to the dispatch.yaml file."""
    yaml_path = _find_dispatch_yaml(path) or os.path.join(path, DISPATCH_YAML)
    with open(yaml_path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    agent_name = config.get("agent_name", data.get("agent_name", "shared"))
    secrets_list = data.get("secrets") or []
    existing_names = {s["name"] for s in secrets_list}

    for var in secret_names:
        if var not in existing_names:
            secrets_list.append(
                {"name": var, "secret_id": f"{agent_name}/{var.lower()}"}
            )

    data["secrets"] = secrets_list
    with open(yaml_path, "w", encoding="utf-8") as fh:
        yaml.dump(data, fh, default_flow_style=False, sort_keys=False)


def check_env_secrets_not_in_config(path: str, config: dict) -> list[str]:
    """Check if .env contains secrets that are not configured in dispatch.yaml.

    This helps catch cases where developers add secrets to .env for local testing
    but forget to add them to dispatch.yaml, meaning they won't be available
    in production.

    LLM provider keys are excluded — those are managed by the LLM gateway.

    Returns:
        List of secret variable names found in .env but not in dispatch.yaml.
        Empty list if all secrets are configured.
    """
    logger = get_logger()
    dotenv_path = os.path.join(path, ".env")

    if not os.path.exists(dotenv_path):
        return []

    # Get configured secrets from dispatch.yaml
    configured_secrets = {s["name"] for s in (config.get("secrets") or [])}

    # Parse .env file for variable names
    env_vars: set[str] = set()
    with open(dotenv_path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                var_name = line.split("=", 1)[0].strip()
                env_vars.add(var_name)

    # LLM keys are managed by the gateway — don't flag them as missing
    missing_secrets = sorted(env_vars - configured_secrets - LLM_PROVIDER_KEY_NAMES)
    skipped_llm_keys = sorted(env_vars & LLM_PROVIDER_KEY_NAMES - configured_secrets)

    if skipped_llm_keys:
        logger.info(
            f"Skipping LLM keys ({', '.join(skipped_llm_keys)}) — "
            "managed by the LLM gateway. Use `dispatch llm setup` to configure."
        )

    if missing_secrets:
        logger.warning(
            f"Found {len(missing_secrets)} secret(s) in .env "
            "not configured in dispatch.yaml:"
        )
        for var in missing_secrets:
            logger.info(f"  - {var}")
        logger.info("")
        logger.info("These secrets will NOT be available in production.")

        # Build the full yaml snippet for all missing secrets
        agent_name = config.get("agent_name", "shared")
        yaml_lines = "secrets:"
        for var in missing_secrets:
            yaml_lines += (
                f'\n  - name: "{var}"\n    secret_id: "{agent_name}/{var.lower()}"'
            )

        # Offer to add them automatically
        if typer.confirm("Add these secrets to dispatch.yaml?", default=True):
            _add_secrets_to_yaml(path, config, missing_secrets)
            logger.success("Added secrets to dispatch.yaml.")
            missing_secrets = []  # no longer missing
        else:
            logger.info("To add them manually, use this format:")
            logger.info("")
            logger.code(yaml_lines, "yaml")

    return missing_secrets


def validate_dispatch_project(path: str) -> bool:
    """Validate that dispatch project has been initialized."""
    logger = get_logger()
    if not os.path.isdir(path):
        logger.error(f"{path} is not a directory.")
        return False

    has_python_reqs(path, warn=True)

    dispatch_dir = os.path.join(path, DISPATCH_DIR)
    listener_path = os.path.join(dispatch_dir, DISPATCH_LISTENER_FILE)

    for check_path in [dispatch_dir, listener_path]:
        if not os.path.exists(check_path):
            logger.error(
                f"{check_path} not found. "
                "Run 'dispatch agent init' to regenerate project assets."
            )
            return False

    # Check for dispatch config file
    has_visible = os.path.exists(os.path.join(path, DISPATCH_YAML))
    has_hidden = os.path.exists(os.path.join(path, ".dispatch.yaml"))

    if has_hidden:
        logger.error(
            ".dispatch.yaml is no longer supported; rename it to dispatch.yaml"
        )
        return False

    if not has_visible:
        logger.error(
            f"{DISPATCH_YAML} not found. "
            "Run 'dispatch agent init' to regenerate project assets."
        )
        return False

    return True


def derive_agent_name(
    path: str,
    config: dict | None = None,
    pyproject: tomlkit.TOMLDocument | None = None,
) -> str:
    """Derive a stable agent name from config, pyproject, or directory name."""
    if config:
        candidate = config.get("agent_name")
        if candidate:
            return _slugify_name(candidate)

    document = pyproject or read_pyproject(path)
    if document:
        project_section = document.get("project", {})
        candidate = project_section.get("name")
        if candidate:
            return _slugify_name(candidate)

    return _slugify_name(os.path.basename(os.path.abspath(path)))


def _slugify_name(value: str) -> str:
    slug = re.sub(r"[^a-z0-9-]", "-", str(value).lower()).strip("-")
    return slug or "dispatch-agent"


def extract_local_deps_from_pyproject(project_path: str) -> dict[str, str | dict]:
    """Extract dependencies to bundle from pyproject.toml [tool.uv.sources].

    This function identifies dependencies that need to be bundled as wheels for remote builds.
    It extracts both local path dependencies and git dependencies from uv's source configuration.

    The mixed return type (str | dict) is intentional because different dependency types
    need different handling:
    - Path dependencies: Return the path string so we can call `uv build` on the directory
    - Git dependencies: Return the full source dict so we can clone the repo and build it

    Args:
        project_path: Path to the project directory containing pyproject.toml

    Returns:
        Dict mapping dependency name to source configuration:
        - For path deps: {"my-lib": "../../libs/my-lib"}
        - For git deps: {"other-lib": {"git": "https://...", "rev": "v1.0", "subdirectory": "pkg"}}

    Example pyproject.toml:
        [tool.uv.sources]
        my-local-lib = { path = "../../libs/my-local-lib" }
        private-repo = { git = "git@github.com/org/repo.git", subdirectory = "sdk", rev = "v1.2.3" }

    Example return value:
        {
            "my-local-lib": "../../libs/my-local-lib",
            "private-repo": {"git": "git@github.com/org/repo.git", "subdirectory": "sdk", "rev": "v1.2.3"}
        }

    Note:
        dispatch-agents and dispatch-cli dependencies are NOT included here - they're
        handled separately by the backend infrastructure to ensure version compatibility.
    """
    pyproject = read_pyproject(project_path)
    if not pyproject:
        return {}

    uv_sources = pyproject.get("tool", {}).get("uv", {}).get("sources", {})
    bundled_deps = {}

    for dep_name, source_config in uv_sources.items():
        if isinstance(source_config, dict):
            # Include path dependencies (local)
            if "path" in source_config:
                bundled_deps[dep_name] = source_config["path"]
            # Include git dependencies (need to be downloaded/built)
            elif "git" in source_config:
                bundled_deps[dep_name] = source_config

    return bundled_deps


def process_local_dependencies(config: dict, project_path: str) -> tuple[str, str, str]:
    """Process local path dependencies and return Docker COPY and RUN commands.

    Note: Only handles path dependencies. Git dependencies are handled differently
    in remote builds (downloaded as wheels).

    Returns:
        tuple: (copy_section, path_fix_section, install_section, filtered_requirements)
    """
    # Merge local_dependencies from config with those auto-detected from pyproject.toml
    config_deps = config.get("local_dependencies") or {}
    pyproject_deps = extract_local_deps_from_pyproject(project_path)

    # Config takes precedence over pyproject
    all_deps = {**pyproject_deps, **config_deps}

    # Filter to only path dependencies (strings), skip git dependencies (dicts)
    local_deps = {k: v for k, v in all_deps.items() if isinstance(v, str)}

    if not local_deps:
        return "", "", ""

    copy_commands: list[str] = []
    path_fix_commands: list[str] = []

    # Extract package names to filter out from shared requirements
    local_package_names = {name.replace("_", "-") for name in local_deps.keys()}
    local_package_names.update(local_deps.keys())

    filtered_requirements = []
    for req in DISPATCH_REQUIREMENTS:
        pkg_name = req.split("@")[0].split()[0].strip().strip('"').replace("_", "-")
        if pkg_name not in local_package_names:
            filtered_requirements.append(req)

    for dep_name, dep_path in local_deps.items():
        if not os.path.isabs(dep_path):
            abs_dep_path = os.path.join(project_path, dep_path)
        else:
            abs_dep_path = dep_path

        if not os.path.exists(abs_dep_path):
            logger = get_logger()
            logger.warning(f"Local dependency path does not exist: {abs_dep_path}")
            continue

        # Place local dependencies in a predictable location inside Docker
        # We'll put them in /deps/{dep_name} and update the pyproject.toml paths accordingly
        if os.path.isabs(dep_path):
            # For absolute paths, still use /deps location for consistency
            docker_path = f"/deps/{dep_name}"
        else:
            # For relative paths, place in /deps/{dep_name}
            docker_path = f"/deps/{dep_name}"

        copy_commands.append(f"COPY --from={dep_name} . {docker_path}")

        # Fix pyproject.toml and uv.lock to use the new Docker paths
        # This replaces the original path with our standardized /deps/{dep_name} location
        # Use sed to replace the path in both files
        # This handles formats like: dispatch-agents = { path = "../../sdk", editable = true }
        path_fix_commands.append(
            f'RUN sed -i \'s|path = "{dep_path}"|path = "{docker_path}"|g\' pyproject.toml'
        )

        # Fix uv.lock - update all possible path references
        # uv.lock can have paths in many different formats, so we need comprehensive replacement
        path_fix_commands.append(f"RUN sed -i 's|{dep_path}|{docker_path}|g' uv.lock")

    copy_section = "\n".join(copy_commands) if copy_commands else ""
    path_fix_section = "\n".join(path_fix_commands) if path_fix_commands else ""
    install_section = (
        ""  # No longer needed - uv sync will install from the copied paths
    )

    return copy_section, path_fix_section, install_section


def detect_dependency_strategy(
    path: str, _config: dict
) -> tuple[str, dict[str, object]]:
    """Auto-detect how to install project dependencies inside the container.

    Only supports pyproject.toml (with uv) or bundled wheels.
    requirements.txt is explicitly not supported.

    Args:
        path: Path to the agent project directory
        _config: Config dict (unused, kept for compatibility)
    """

    def _exists(relative: str) -> bool:
        return os.path.exists(os.path.join(path, relative))

    # Check for unsupported requirements.txt files first
    for candidate in [
        "requirements.txt",
        "requirements-prod.txt",
        "requirements-dev.txt",
    ]:
        if _exists(candidate):
            raise typer.BadParameter(
                f"Found {candidate}, but requirements.txt is no longer supported.\n"
                f"Please migrate to pyproject.toml using:\n"
                f"  uv init --name <your-agent-name>\n"
                f"  uv add $(cat {candidate})\n"
                f"Then remove {candidate}."
            )

    # Bundled strategy (for remote builds where wheels are pre-built)
    if _exists("dependencies"):
        return "bundled", {}

    # Standard pyproject.toml strategy
    if _exists("pyproject.toml"):
        return "pyproject", {}

    raise typer.BadParameter(
        "Could not find pyproject.toml. "
        "Please create one using: uv init --name <your-agent-name>"
    )


def render_dependency_install_step(strategy: str, _details: dict[str, object]) -> str:
    """Render Dockerfile snippet that installs project dependencies.

    Args:
        strategy: The dependency strategy ("pyproject" or "bundled")
        _details: Strategy details dict (unused, kept for compatibility)
    """
    if strategy == "requirements":
        raise ValueError("requirements.txt strategy is no longer supported.")

    if strategy == "pyproject":
        return (
            "RUN --mount=type=cache,target=/root/.cache/uv \\\n"
            "    --mount=type=ssh \\\n"
            "    mkdir -p /root/.ssh && \\\n"
            "    ssh-keyscan github.com >> /root/.ssh/known_hosts && \\\n"
            "    uv sync --frozen"
        )

    if strategy == "bundled":
        return (
            "COPY dependencies/ /app/dependencies/\n"
            "# Install dependencies from PyPI and bundled wheels\n"
            "RUN --mount=type=cache,target=/root/.cache/uv \\\n"
            "    uv pip install --system \\\n"
            "    --find-links /app/dependencies \\\n"
            "    ."
        )

    raise ValueError(f"Unsupported dependency strategy '{strategy}'")
