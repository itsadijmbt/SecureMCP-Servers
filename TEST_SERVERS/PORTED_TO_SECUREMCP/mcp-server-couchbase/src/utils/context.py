"""
Process-wide Couchbase cluster + app-context state.

PORT NOTE -- FastMCP -> SecureMCP

Original design:
    Tools reached the cluster via:
        ctx.request_context.lifespan_context.cluster
    The AppContext dataclass was YIELDED by FastMCP's @asynccontextmanager
    lifespan and threaded into every tool call through the Context object.

"""

import logging
from dataclasses import dataclass

from couchbase.cluster import Cluster

from utils.config import get_settings
from utils.connection import connect_to_couchbase_cluster
from utils.constants import MCP_SERVER_NAME

logger = logging.getLogger(f"{MCP_SERVER_NAME}.utils.context")


@dataclass
class AppContext:
    """Process-wide configuration flags.

    PORT: previously yielded by the FastMCP lifespan into every tool call.
    Now lives in the _APP_CONTEXT module global, populated by
    initialize_app_context() at server startup.
    """

    read_only_mode: bool = True
    read_only_query_mode: bool = True


# Module-level state. Populated at startup; read by tools throughout

_APP_CONTEXT: AppContext | None = None
_CLUSTER: Cluster | None = None


def initialize_app_context(read_only_mode: bool, read_only_query_mode: bool) -> None:
    """Populate the AppContext global. Call once from main() before mcp.run()."""
    global _APP_CONTEXT
    _APP_CONTEXT = AppContext(
        read_only_mode=read_only_mode,
        read_only_query_mode=read_only_query_mode,
    )


def get_app_context() -> AppContext:
    """Return the process-wide AppContext. Raises if main() never initialized it."""
    if _APP_CONTEXT is None:
        raise RuntimeError(
            "AppContext not initialized; "
            "call initialize_app_context() from main() before any tool runs."
        )
    return _APP_CONTEXT


def get_cluster_connection() -> Cluster:
    """Return the shared Couchbase cluster, building it on first call.

    PORT: previously took (ctx: Context) and reached
          ctx.request_context.lifespan_context.cluster.
    """
    global _CLUSTER
    if _CLUSTER is not None:
        return _CLUSTER

    try:
        settings = get_settings()
        _CLUSTER = connect_to_couchbase_cluster(
            settings["connection_string"],
            settings["username"],
            settings["password"],
            settings.get("ca_cert_path"),
            settings.get("client_cert_path"),
            settings.get("client_key_path"),
        )
        return _CLUSTER
    except Exception as e:
        logger.error(
            "Failed to connect to Couchbase: %s\n"
            "Verify connection string, and either:\n"
            "- Username/password are correct, or\n"
            "- Client certificate and key exist and match server mapping.\n"
            "If using self-signed or custom CA, set CB_CA_CERT_PATH to the CA file.",
            e,
        )
        raise
