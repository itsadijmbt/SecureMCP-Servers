"""Main entry point for K8s MCP Server.

Running this module will start the K8s MCP Server.
"""

import logging
import signal
import sys
import warnings

# Configure logging before importing server
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger("k8s-mcp-server")


def handle_interrupt(signum, frame):
    """Handle keyboard interrupt (Ctrl+C) gracefully."""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)


# PORT: was "Using FastMCP's built-in CLI handling".
# Under SecureMCP, transport selection is inert (mcp.run() ignores
# the transport= kwarg and creates its own asyncio.run() internally;
# the mesh carries the traffic, not stdio/SSE/HTTP). All
# transport-validation, SSE deprecation, and host-binding logic is
# commented below since the underlying machinery doesn't exist
# under SecureMCP. Signal handlers are kept (they are framework-
# independent OS-level handlers).
def main():
    """Run the K8s MCP Server."""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, handle_interrupt)
    signal.signal(signal.SIGTERM, handle_interrupt)
    try:
        # Import here to avoid circular imports
        # PORT: dropped MCP_TRANSPORT/VALID_TRANSPORTS/is_docker_environment imports;
        # transport-selection block below is commented and they are no longer used here.
        # from k8s_mcp_server.config import MCP_TRANSPORT, VALID_TRANSPORTS, is_docker_environment
        from k8s_mcp_server.server import mcp

        # ==============================================================
        # PORT: transport selection is inert under SecureMCP. Original
        # block preserved as comments for future reference.
        # ==============================================================
        # # Validate transport protocol
        # if MCP_TRANSPORT not in VALID_TRANSPORTS:
        #     logger.error(f"Invalid transport protocol: {MCP_TRANSPORT}. Must be one of: {', '.join(sorted(VALID_TRANSPORTS))}. Using stdio instead.")
        #     transport = "stdio"
        # else:
        #     transport = MCP_TRANSPORT
        #
        # # SSE deprecation warning — recommend streamable-http
        # if transport == "sse":
        #     msg = "SSE transport is deprecated per MCP spec 2025-11-25. Use 'streamable-http' instead (K8S_MCP_TRANSPORT=streamable-http)."
        #     warnings.warn(msg, DeprecationWarning, stacklevel=2)
        #     logger.warning(msg)
        #
        # # For HTTP transports, bind to 0.0.0.0 inside Docker (required for port mapping)
        # # mcp.settings does not exist on SecureMCP; this block is unreachable.
        # if transport in ("sse", "streamable-http"):
        #     host = "0.0.0.0" if is_docker_environment() else "127.0.0.1"
        #     mcp.settings.host = host
        #     logger.info(f"HTTP server binding to {host}:{mcp.settings.port}")
        #
        # # Start the server
        # logger.info(f"Starting K8s MCP Server with {transport} transport")
        # mcp.run(transport=transport)

        # PORT: SecureMCP boots and idles on a single internal asyncio.run.
        # Traffic arrives via the MACAW mesh, not via stdio/SSE/HTTP.
        logger.info("Starting K8s MCP Server (SecureMCP / MACAW mesh)")
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down gracefully...")
        sys.exit(0)


if __name__ == "__main__":
    main()
