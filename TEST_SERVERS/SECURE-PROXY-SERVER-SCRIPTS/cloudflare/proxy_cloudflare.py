"""
cloudflare-proxy -> SecureMCPProxy, served natively.

Prereq:
    export CLOUDFLARE_API_TOKEN="..."
    export MACAW_HOME="/path/to/macaw-client-<version>-Linux-x86_64-py3.12"

Run:
    python proxy_cloudflare.py
    python proxy_cloudflare.py http 8080

Claude Code:
    claude mcp add cloudflare-macaw python /path/to/proxy_cloudflare.py \
      -e CLOUDFLARE_API_TOKEN=... \
      -e MACAW_HOME=/path/to/macaw-client-<version>-Linux-x86_64-py3.12
"""

import os
import sys
import logging

import httpx as _httpx
from macaw_adapters.mcp import SecureMCPProxy, Client


logging.basicConfig(level=logging.INFO, stream=sys.stderr)

token = os.environ.get("CLOUDFLARE_API_TOKEN")
if not token:
    raise ValueError("CLOUDFLARE_API_TOKEN is not set")

CF_MCP_URL = "https://bindings.mcp.cloudflare.com/mcp"


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
    app_name="cloudflare-proxy",
    upstream_url=CF_MCP_URL,
    upstream_auth={"type": "bearer", "token": token},
)
logging.info("cloudflare-proxy: %d tools; serving native clients", len(proxy.list_tools()))

client = Client("cloudflare-macaw-gateway")
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
