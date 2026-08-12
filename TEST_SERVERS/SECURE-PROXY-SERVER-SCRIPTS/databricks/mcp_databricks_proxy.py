"""
databricks-proxy -> SecureMCPProxy, served natively.

Prereq:
    export DATABRICKS_MCP_URL="..."
    export DATABRICKS_TOKEN="..."
     export MACAW_HOME="path to whl"

Run:
    /home/itsadijmbt/testing-SecureAdapters-nativeMCP/venv/bin/python mcp_databricks_proxy.py
    /home/itsadijmbt/testing-SecureAdapters-nativeMCP/venv/bin/python mcp_databricks_proxy.py http 8080
"""

import os
import sys
import json
import asyncio
import logging

import httpx as _httpx

from macaw_adapters.mcp import SecureMCPProxy, Client

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types


logging.basicConfig(level=logging.INFO, stream=sys.stderr)


token = os.environ.get("DATABRICKS_TOKEN")
if not token:
    raise ValueError("DATABRICKS_TOKEN is not set (workspace PAT)")

DATABRICKS_MCP_URL = os.environ.get("DATABRICKS_MCP_URL")
if not DATABRICKS_MCP_URL:
    raise ValueError(
        "DATABRICKS_MCP_URL is not set -- e.g. https://<workspace>/api/2.0/mcp/sql")


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
    app_name="databricks-proxy",
    upstream_url=DATABRICKS_MCP_URL,
    upstream_auth={"type": "bearer", "token": token},
)
logging.info("databricks-proxy: %d tools; serving native clients", len(proxy.list_tools()))

client = Client("secure-claude-code")
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
