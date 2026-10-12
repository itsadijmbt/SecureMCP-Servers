"""
pan-mcp-relay-proxy -> SecureMCPProxy, served natively.

Prereq:
    export PRISMA_AIRS_AI_PROFILE="..."
    export PRISMA_AIRS_API_KEY="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_pan_mcp_relay.py

Claude Code:
    claude mcp add pan-mcp-relay-macaw python /path/to/proxy_pan_mcp_relay.py \
      -e PRISMA_AIRS_AI_PROFILE=... \
      -e PRISMA_AIRS_API_KEY=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12

    The relay is started by this script on 127.0.0.1 and reached over HTTP. MCP_RELAY_PORT sets its port (default 8000).
"""

import os
import sys
import time
import atexit
import signal
import socket
import logging
import subprocess
from pathlib import Path
from macaw_adapters.mcp import SecureMCPProxy


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

api_key = os.environ.get("PRISMA_AIRS_API_KEY")
ai_profile = os.environ.get("PRISMA_AIRS_AI_PROFILE")
if not api_key or not ai_profile:
    raise ValueError("Set PRISMA_AIRS_API_KEY and PRISMA_AIRS_AI_PROFILE")

port = os.environ.get("MCP_RELAY_PORT", "8000")
config_file = str(Path(__file__).parent / "mcp-relay.yaml")
with socket.socket() as probe:
    if probe.connect_ex(("127.0.0.1", int(port))) == 0:
        raise RuntimeError(f"127.0.0.1:{port} is already in use. Set MCP_RELAY_PORT to a free port.")

# The relay runs over its HTTP transport: its stdio transport does not answer tools/list
# (PaloAltoNetworks/pan-mcp-relay issue 6). mcp is pinned to the release line the relay's code matches.
relay = subprocess.Popen(
    [
        "uvx", "--with", "mcp==1.21.2", "pan-mcp-relay@latest",
        "--config-file", config_file,
        "--transport", "http",
        "--port", port,
    ],
    env={
        "PATH": os.environ["PATH"],
        "HOME": os.environ["HOME"],
        "PRISMA_AIRS_API_KEY": api_key,
        "PRISMA_AIRS_AI_PROFILE": ai_profile,
    },
    stdin=subprocess.DEVNULL,
    stdout=sys.stderr,
)
atexit.register(relay.terminate)
signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))

for _ in range(240):
    if relay.poll() is not None:
        raise RuntimeError("pan-mcp-relay stopped while starting; see the lines above")
    try:
        socket.create_connection(("127.0.0.1", int(port)), 0.5).close()
        break
    except OSError:
        time.sleep(0.5)
else:
    raise RuntimeError(f"pan-mcp-relay did not open 127.0.0.1:{port}")

proxy = SecureMCPProxy(
    app_name="pan-mcp-relay-proxy",
    upstream_url=f"http://127.0.0.1:{port}/mcp",
)
logging.info("pan-mcp-relay-proxy: %d tools; serving native clients", len(proxy.list_tools()))

proxy.run()
