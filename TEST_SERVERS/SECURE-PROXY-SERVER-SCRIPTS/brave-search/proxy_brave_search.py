"""
brave-search-proxy -> SecureMCPProxy, served natively.

Prereq:
    export BRAVE_API_KEY="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_brave_search.py
    python proxy_brave_search.py http 8080

Claude Code:
    claude mcp add brave-search-macaw python /path/to/proxy_brave_search.py \
      -e BRAVE_API_KEY=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

api_key = os.environ.get("BRAVE_API_KEY")
if not api_key:
    raise ValueError(
        "BRAVE_API_KEY is not set. "
        "Get a key at https://api-dashboard.search.brave.com/app/keys"
    )

proxy = SecureMCPProxy(
    app_name="brave-search-proxy",
    command=["npx", "-y", "@brave/brave-search-mcp-server", "--transport", "stdio"],
    env={
        "PATH": os.environ["PATH"],
        "HOME": os.environ["HOME"],
        "BRAVE_API_KEY": api_key,
    },
)
logging.info("brave-search-proxy: %d tools; serving native clients", len(proxy.list_tools()))

client = Client("brave-search-macaw-gateway")
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
