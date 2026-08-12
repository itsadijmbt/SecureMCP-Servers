"""
neon-proxy -> SecureMCPProxy, served natively.

Prereq:
    export NEON_API_KEY="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_neon.py
    python proxy_neon.py http 8080

Claude Code:
    claude mcp add neon-macaw python /path/to/proxy_neon.py \
      -e NEON_API_KEY=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging

import httpx as _httpx

from macaw_adapters.mcp import SecureMCPProxy, Client

logging.basicConfig(level=logging.INFO, stream=sys.stderr)

NEON_API_KEY = os.environ.get("NEON_API_KEY")
if not NEON_API_KEY:
    raise ValueError("NEON_API_KEY is not set (create at https://console.neon.tech/app/settings/api-keys)")

NEON_MCP_URL = "https://mcp.neon.tech/mcp"


def _timed_create_http_client(self):
    ua = self.upstream_auth
    headers = {}
    if getattr(ua, "type", None) == "bearer" and getattr(ua, "token", None):
        headers["Authorization"] = f"Bearer {ua.token}"
    elif getattr(ua, "type", None) == "api_key" and getattr(ua, "api_key", None):
        headers[getattr(ua, "header_name", None) or "X-API-Key"] = ua.api_key
    return _httpx.AsyncClient(
        headers=headers or None,
        timeout=_httpx.Timeout(connect=30, read=300, write=30, pool=30),
    )
SecureMCPProxy._create_http_client = _timed_create_http_client

proxy = SecureMCPProxy(
    app_name="neon-proxy",
    upstream_url=NEON_MCP_URL,
    upstream_auth={"type": "bearer", "token": NEON_API_KEY},
)
logging.info("neon-proxy: %d tools; serving native clients", len(proxy.list_tools()))

client = Client("neon-macaw-gateway")
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
