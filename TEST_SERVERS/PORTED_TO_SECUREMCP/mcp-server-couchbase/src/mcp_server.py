"""
Couchbase MCP Server (SecureMCP port).

PORT NOTE -- FastMCP -> SecureMCP

Original design used FastMCP with @asynccontextmanager app_lifespan
that yielded an AppContext into ctx.request_context.lifespan_context.
SecureMCP has no lifespan primitive, so:

  * app_lifespan was deleted; its body had no `await`. Read-only-mode
    flags were captured in initialize_app_context() at startup, called
    from main() before mcp.run().
  * The AppContext / cluster live in module globals in utils.context.
  * mcp.add_tool(fn, annotations=...) became mcp.tool(name=...,
    description=...)(fn). SecureMCP exposes only a decorator factory
    and accepts only (name, description, prompts).
  * --host, --port, --transport CLI flags are kept on the surface
    for back-compat but are cosmetic under SecureMCP. MACAW provides
    the mesh transport regardless.
"""

import logging
from collections.abc import Callable

import click
from macaw_adapters.mcp import SecureMCP

# Import tools
from tools import get_tools

# Import utilities
from utils import (
    ALLOWED_TRANSPORTS,
    DEFAULT_HOST,
    DEFAULT_LOG_LEVEL,
    DEFAULT_PORT,
    DEFAULT_READ_ONLY_MODE,
    DEFAULT_TRANSPORT,
    MCP_SERVER_NAME,
    parse_tool_names,
    wrap_with_confirmation,
)
from utils.config import set_settings
from utils.context import initialize_app_context

# Configure logging
logging.basicConfig(
    level=getattr(logging, DEFAULT_LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(MCP_SERVER_NAME)


def prepare_tools_for_registration(
    read_only_mode: bool,
    disabled_tools: str | None,
    confirmation_required_tools: str | None,
) -> tuple[list[Callable], set[str], set[str]]:
    """Prepare final tool list and confirmation configuration for registration."""
    tools = get_tools(read_only_mode=read_only_mode)

    loaded_tool_names = {tool.__name__ for tool in tools}
    disabled_tool_names = parse_tool_names(disabled_tools, loaded_tool_names)

    if disabled_tool_names:
        logger.info(
            f"Disabled {len(disabled_tool_names)} tool(s): {sorted(disabled_tool_names)}"
        )

    configured_confirmation_tool_names = parse_tool_names(
        confirmation_required_tools, loaded_tool_names
    )

    if configured_confirmation_tool_names:
        logger.info(
            f"Confirmation required for {len(configured_confirmation_tool_names)} tool(s): "
            f"{sorted(configured_confirmation_tool_names)}"
        )

    enabled_tools = [tool for tool in tools if tool.__name__ not in disabled_tool_names]

    active_tool_names = {tool.__name__ for tool in enabled_tools}
    active_confirmation_tool_names = (
        configured_confirmation_tool_names & active_tool_names
    )

    skipped_confirmation_tool_names = (
        configured_confirmation_tool_names - active_tool_names
    )
    if skipped_confirmation_tool_names:
        logger.info(
            "Skipped confirmation for unavailable tool(s): "
            f"{sorted(skipped_confirmation_tool_names)}"
        )

    final_tools = [
        (
            wrap_with_confirmation(tool)
            if tool.__name__ in active_confirmation_tool_names
            else tool
        )
        for tool in enabled_tools
    ]

    return final_tools, configured_confirmation_tool_names, disabled_tool_names


# PORT: app_lifespan() was here. Deleted. Its body had no `await`; it
# only built an AppContext and yielded it. Under SecureMCP we move
# that initialization to main() via initialize_app_context().


@click.command()
@click.option(
    "--connection-string",
    envvar="CB_CONNECTION_STRING",
    help="Couchbase connection string (required for operations)",
)
@click.option(
    "--username",
    envvar="CB_USERNAME",
    help="Couchbase database user (required for operations)",
)
@click.option(
    "--password",
    envvar="CB_PASSWORD",
    help="Couchbase database password (required for operations)",
)
@click.option(
    "--ca-cert-path",
    envvar="CB_CA_CERT_PATH",
    help="Path to the server trust store (CA certificate) file. The certificate at this path is used to verify the server certificate during the authentication process.",
)
@click.option(
    "--client-cert-path",
    envvar="CB_CLIENT_CERT_PATH",
    help="Path to the client certificate file used for mTLS authentication.",
)
@click.option(
    "--client-key-path",
    envvar="CB_CLIENT_KEY_PATH",
    help="Path to the client certificate key file used for mTLS authentication.",
)
@click.option(
    "--read-only-mode",
    envvar="CB_MCP_READ_ONLY_MODE",
    type=bool,
    default=DEFAULT_READ_ONLY_MODE,
    help="Enable read-only mode (default True). When True, all write operations are disabled and KV write tools are not loaded.",
)
@click.option(
    "--read-only-query-mode",
    envvar=[
        "CB_MCP_READ_ONLY_QUERY_MODE",
        "READ_ONLY_QUERY_MODE",  # Deprecated
    ],
    type=bool,
    deprecated=True,
    default=DEFAULT_READ_ONLY_MODE,
    help="[DEPRECATED: Use --read-only-mode] Enable read-only query mode.",
)
@click.option(
    "--transport",
    envvar=[
        "CB_MCP_TRANSPORT",
        "MCP_TRANSPORT",  # Deprecated
    ],
    type=click.Choice(ALLOWED_TRANSPORTS),
    default=DEFAULT_TRANSPORT,
    help="[Cosmetic under SecureMCP] Transport mode kept for CLI back-compat. MACAW provides the mesh transport.",
)
@click.option(
    "--host",
    envvar="CB_MCP_HOST",
    default=DEFAULT_HOST,
    help="[Cosmetic under SecureMCP] Kept for CLI back-compat.",
)
@click.option(
    "--port",
    envvar="CB_MCP_PORT",
    default=DEFAULT_PORT,
    help="[Cosmetic under SecureMCP] Kept for CLI back-compat.",
)
@click.option(
    "--disabled-tools",
    "disabled_tools",
    envvar="CB_MCP_DISABLED_TOOLS",
    help="Tools to disable (comma-separated names or path to file with one name per line).",
)
@click.option(
    "--confirmation-required-tools",
    "confirmation_required_tools",
    envvar="CB_MCP_CONFIRMATION_REQUIRED_TOOLS",
    help="Tools requiring user confirmation before execution. Comma-separated or file path.",
)
@click.version_option(package_name="couchbase-mcp-server")
@click.pass_context
def main(
    ctx,
    connection_string,
    username,
    password,
    ca_cert_path,
    client_cert_path,
    client_key_path,
    read_only_mode,
    read_only_query_mode,
    transport,
    host,
    port,
    disabled_tools,
    confirmation_required_tools,
):
    """Couchbase MCP Server (SecureMCP port)."""

    (
        final_tools,
        configured_confirmation_tool_names,
        disabled_tool_names,
    ) = prepare_tools_for_registration(
        read_only_mode=read_only_mode,
        disabled_tools=disabled_tools,
        confirmation_required_tools=confirmation_required_tools,
    )

    # Click context still feeds get_settings(); upstream code reads it.
    ctx.obj = {
        "connection_string": connection_string,
        "username": username,
        "password": password,
        "ca_cert_path": ca_cert_path,
        "client_cert_path": client_cert_path,
        "client_key_path": client_key_path,
        "read_only_mode": read_only_mode,
        "read_only_query_mode": read_only_query_mode,
        "transport": transport,
        "host": host,
        "port": port,
        "disabled_tools": disabled_tool_names,
        "confirmation_required_tools": configured_confirmation_tool_names,
    }

    # PORT: stash settings in a module global so tools running in
    # MACAW worker threads can read them without reaching for
    # click.get_current_context() (which only works in the click
    # command's own call frame).
    set_settings(ctx.obj)

    # PORT: initialize the AppContext module global once, here in main().
    # Replaces the lifespan-yielded AppContext that tools used to read
    # via ctx.request_context.lifespan_context.
    initialize_app_context(
        read_only_mode=read_only_mode,
        read_only_query_mode=read_only_query_mode,
    )

    # PORT: was FastMCP(MCP_SERVER_NAME, lifespan=app_lifespan, **config).
    # SecureMCP doesn't accept lifespan=, host=, port= -- those were
    # FastMCP-only. Just the name.
    mcp = SecureMCP(MCP_SERVER_NAME)

    logger.info(
        f"Registering {len(final_tools)} tool(s) with modes "
        f"(read_only_mode={read_only_mode}, read_only_query_mode={read_only_query_mode})"
    )

    # PORT: was mcp.add_tool(tool, annotations=annotations).
    # SecureMCP exposes only the decorator factory; use the
    # decorator-as-function form. annotations= is dropped because
    # SecureMCP only accepts (name, description, prompts).
    for tool in final_tools:
        mcp.tool(name=tool.__name__, description=tool.__doc__ or "")(tool)

    logger.info(f"Registered {len(final_tools)} tool(s)")

    # PORT: transport= argument is cosmetic; SecureMCP ignores it.
    mcp.run()


if __name__ == "__main__":
    main()
