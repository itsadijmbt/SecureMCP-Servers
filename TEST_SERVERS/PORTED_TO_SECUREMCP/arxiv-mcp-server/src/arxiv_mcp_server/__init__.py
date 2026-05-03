"""
Arxiv MCP Server initialization
"""

from . import server
# import asyncio    # PORT: not needed; server.main() is sync under SecureMCP


def main():
    """Main entry point for the package."""
    # PORT: was `asyncio.run(server.main())`. server.main() is sync now
    # (calls app.run() which is sync). Wrapping a sync return-None call
    # in asyncio.run would raise TypeError.
    # asyncio.run(server.main())
    server.main()


__all__ = ["main", "server"]
