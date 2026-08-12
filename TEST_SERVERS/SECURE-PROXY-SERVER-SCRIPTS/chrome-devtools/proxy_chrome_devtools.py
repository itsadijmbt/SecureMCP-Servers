"""
chrome-devtools-proxy -> SecureMCPProxy, served natively.

Prereq:
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_chrome_devtools.py
    python proxy_chrome_devtools.py http 8080

Claude Code:
    claude mcp add chrome-devtools-macaw python /path/to/proxy_chrome_devtools.py \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

proxy = SecureMCPProxy(
    app_name="chrome-devtools-proxy",
    command=[
        "npx", "-y", "chrome-devtools-mcp@latest",
        "--headless",
        "--isolated",
    ],
    env={
        "PATH": os.environ["PATH"],
        "HOME": os.environ["HOME"],
    },
)
logging.info("chrome-devtools-proxy: %d tools; serving native clients", len(proxy.list_tools()))

client = Client("chrome-devtools-macaw-gateway")
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
