"""Configuration for MCP server."""

from dataclasses import dataclass

from dispatch_cli.auth_provider import CredentialResolver
from dispatch_cli.utils import DISPATCH_API_BASE, DISPATCH_DEPLOY_URL


@dataclass
class MCPConfig:
    """Configuration for MCP server."""

    credential_provider: CredentialResolver
    namespace: str | None = None
    agent_name: str | None = None
    api_base: str = DISPATCH_API_BASE
    deploy_url: str = DISPATCH_DEPLOY_URL
    use_tasks: bool = True  # Enable experimental task support
    server_type: str = "operator"  # "agent" or "operator"
