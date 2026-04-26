import logging
from pathlib import Path

# PORT: `import click` was here, used by the old get_settings()
# implementation to reach click.get_current_context(). Removed --
# tool calls under SecureMCP run in worker threads where click has
# no current context, so the click-based read raised
# `RuntimeError: There is no active click context.`
# import click

from .constants import MCP_SERVER_NAME

logger = logging.getLogger(f"{MCP_SERVER_NAME}.utils.config")


# PORT: settings are now stashed in a module global at startup by
# main() via set_settings(), and read by tools in any thread via
# get_settings(). Replaces the FastMCP-era pattern of reading
# click.get_current_context().obj at tool-call time.
_SETTINGS: dict = {}


def set_settings(settings: dict) -> None:
    """Store settings in the process-wide module global.

    Called once from main() right after the click command parses CLI
    args / env vars, BEFORE mcp.run(). After this call, get_settings()
    is safe to call from any thread (worker threads dispatched by
    MACAW do not have access to click's context).
    """
    global _SETTINGS
    _SETTINGS = dict(settings or {})


def get_settings() -> dict:
    """Return the process-wide settings dict.

    PORT NOTE: this used to be
        ctx = click.get_current_context()
        return ctx.obj or {}
    which raised "There is no active click context" when called
    from a worker thread. Now reads the module global populated
    by set_settings() at startup. Same return shape, no click.
    """
    return _SETTINGS


def _parse_file(file_path: Path, valid_tool_names: set[str]) -> set[str]:
    """Parse tool names from a file (one tool per line)."""
    tools: set[str] = set()
    invalid_count = 0
    try:
        with open(file_path) as f:
            for raw_line in f:
                name = raw_line.strip()
                if not name or name.startswith("#"):
                    continue
                if name in valid_tool_names:
                    tools.add(name)
                else:
                    invalid_count += 1
        if invalid_count > 0:
            logger.warning(
                f"Ignored {invalid_count} invalid tool name(s) from file: {file_path}"
            )
        logger.debug(f"Loaded {len(tools)} tool name(s) from file: {file_path}")
    except OSError as e:
        logger.warning(f"Failed to read tool names file {file_path}: {e}")
    return tools


def _parse_comma_separated(value: str, valid_tool_names: set[str]) -> set[str]:
    """Parse comma-separated tool names."""
    tools: set[str] = set()
    invalid_count = 0
    for part in value.split(","):
        name = part.strip()
        if name:
            if name in valid_tool_names:
                tools.add(name)
            else:
                invalid_count += 1
    if invalid_count > 0:
        logger.warning(
            f"Ignored {invalid_count} invalid tool name(s) from comma-separated input"
        )
    logger.debug(f"Parsed tool names from comma-separated string: {tools}")
    return tools


def parse_tool_names(
    tool_names_input: str | None,
    valid_tool_names: set[str],
) -> set[str]:
    """
    Parse tool names from CLI argument or environment variable.

    Supported formats:
    1. Comma-separated string: "tool_1,tool_2"
    2. File path containing one tool name per line: "disabled_tools.txt"

    Args:
        tool_names_input: Comma-separated tools or file path
        valid_tool_names: Set of valid tool names to validate against

    Returns:
        Set of valid tool names
    """
    if not tool_names_input:
        return set()

    value = tool_names_input.strip()

    # Check if it's a file path
    potential_path = Path(value)
    if potential_path.exists() and potential_path.is_file():
        return _parse_file(potential_path, valid_tool_names)

    # Otherwise, treat as comma-separated
    return _parse_comma_separated(value, valid_tool_names)
