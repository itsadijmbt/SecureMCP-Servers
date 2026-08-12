"""
notion-proxy -> SecureMCPProxy, served natively.

Prereq:
    export NOTION_TOKEN="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_notion.py
    python proxy_notion.py http 8080

Claude Code:
    claude mcp add notion-macaw python /path/to/proxy_notion.py \
      -e NOTION_TOKEN=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

token = os.environ.get("NOTION_TOKEN")
if not token:
    raise ValueError("NOTION_TOKEN is not set (format: ntn_...)")

proxy = SecureMCPProxy(
    app_name="notion-proxy",
    command=["npx", "-y", "@notionhq/notion-mcp-server"],
    env={
        "PATH": os.environ["PATH"],
        "HOME": os.environ["HOME"],
        "NOTION_TOKEN": token,
    },
)
logging.info("notion-proxy: %d tools; serving native clients", len(proxy.list_tools()))

client = Client("notion-macaw-gateway")
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
