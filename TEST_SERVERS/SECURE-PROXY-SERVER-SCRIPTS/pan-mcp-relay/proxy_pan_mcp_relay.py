"""
pan-mcp-relay-proxy -> SecureMCPProxy, served natively.

Prereq:
    export PRISMA_AIRS_AI_PROFILE="..."
    export PRISMA_AIRS_API_KEY="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_pan_mcp_relay.py
    python proxy_pan_mcp_relay.py http 8080

Claude Code:
    claude mcp add pan-mcp-relay-macaw python /path/to/proxy_pan_mcp_relay.py \
      -e PRISMA_AIRS_AI_PROFILE=... \
      -e PRISMA_AIRS_API_KEY=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging
from pathlib import Path
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

api_key = os.environ.get("PRISMA_AIRS_API_KEY")
ai_profile = os.environ.get("PRISMA_AIRS_AI_PROFILE")
if not api_key or not ai_profile:
    raise ValueError("Set PRISMA_AIRS_API_KEY and PRISMA_AIRS_AI_PROFILE")

config_file = str(Path(__file__).parent / "mcp-relay.yaml")

proxy = SecureMCPProxy(
    app_name="pan-mcp-relay-proxy",
    command=["uvx", "pan-mcp-relay@latest", "--config-file", config_file],
    env={
        "PATH": os.environ["PATH"],
        "HOME": os.environ["HOME"],
        "PRISMA_AIRS_API_KEY": api_key,
        "PRISMA_AIRS_AI_PROFILE": ai_profile,
    },
)
logging.info("pan-mcp-relay-proxy: %d tools; serving native clients", len(proxy.list_tools()))

client = Client("pan-mcp-relay-macaw-gateway")
bound = proxy.bind_to_user(client.macaw_client)

import macaw_adapters.mcp._endpoint as _endpoint

_StubClient = _endpoint.Client


def _bound_stub_client(name):
    stub = _StubClient(name)
    stub.macaw_client = bound.user_client
    return stub


_endpoint.Client = _bound_stub_client

transport = sys.argv[1] if len(sys.argv) > 1 else "stdio"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
proxy.run(transport=transport, port=port)
