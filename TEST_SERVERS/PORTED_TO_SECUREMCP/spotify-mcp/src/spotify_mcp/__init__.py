from . import server
# import asyncio   # PORT: not needed; server.main() is sync under SecureMCP.


def main():
    """Main entry point for the package."""
    # PORT: was `asyncio.run(server.main())`. Under SecureMCP, server.main()
    # calls mcp.run() which is sync (mcp.py:628-635 -- def run, internal
    # asyncio.run(_run_async)). Wrapping in another asyncio.run() would
    # raise "asyncio.run() cannot be called from a running event loop".
    # asyncio.run(server.main())
    server.main()


# Optionally expose other important items at package level
__all__ = ['main', 'server']
