"""Integration tests for MCP operator tools - NO MOCKS, real end-to-end.

NOTE: These tests directly invoke start_local_agent_dev with no mocks, measuring
real performance. However, they require a working router subprocess which may not
work in all test environments (e.g., if uvicorn can't bind to port 8080).

To manually validate performance improvements:
1. Stop the router: dispatch router stop
2. Use Claude Code MCP tool or Python:
   ```python
   import time
   from dispatch_cli.mcp.operator.tools import StartLocalAgentDevRequest, create_operator_mcp
   from dispatch_cli.mcp.config import MCPConfig
   from dispatch_cli.mcp.client import DispatchAPIClient

   config = MCPConfig(
       credential_provider=StaticCredentialProvider(
           ResolvedCredential(auth_mode="api_key", access_token="test")
       ),
       deploy_url="http://localhost:8000",
       namespace="examples",
   )
   client = DispatchAPIClient(config)
   mcp = create_operator_mcp(client, config)
   fn = mcp._tool_manager._tools["start_local_agent_dev"].fn

   class Ctx:
       async def info(self, m): print(f"INFO: {m}")
       async def debug(self, m): pass
       async def error(self, m): print(f"ERROR: {m}")
       async def warning(self, m): print(f"WARN: {m}")

   ctx = Ctx()
   req = StartLocalAgentDevRequest(agent_directory="./examples/hello_world")

   import asyncio
   start = time.time()
   result = asyncio.run(fn(req, ctx))
   print(f"Elapsed: {time.time() - start:.3f}s")
   ```

Expected: < 2s with optimizations (was ~7s before)
"""

import asyncio
import subprocess
import time
from pathlib import Path

import pytest

from dispatch_cli.auth_provider import ResolvedCredential, StaticCredentialProvider
from dispatch_cli.mcp.client import DispatchAPIClient
from dispatch_cli.mcp.config import MCPConfig
from dispatch_cli.mcp.operator.tools import (
    StartLocalAgentDevRequest,
    StopRouterRequest,
    create_operator_mcp,
)


class MCPContext:
    """Simple context for capturing logs during test."""

    def __init__(self):
        self.logs = []

    async def info(self, msg):
        self.logs.append(("INFO", msg))
        print(f"INFO: {msg}")

    async def debug(self, msg):
        self.logs.append(("DEBUG", msg))

    async def error(self, msg):
        self.logs.append(("ERROR", msg))
        print(f"ERROR: {msg}")

    async def warning(self, msg):
        self.logs.append(("WARN", msg))
        print(f"WARN: {msg}")


@pytest.mark.integration
class TestStartLocalAgentDevIntegration:
    """End-to-end integration tests - NO MOCKS."""

    @pytest.mark.asyncio
    async def test_start_local_agent_dev_with_router_startup_real(self):
        """Test start_local_agent_dev with real router startup (NO MOCKS).

        This reproduces the original slow startup scenario and validates the fix.
        """
        # Use the hello_world example agent
        repo_root = Path(__file__).parent.parent.parent
        agent_dir = repo_root / "examples" / "hello_world"

        if not agent_dir.exists():
            pytest.skip(f"Agent directory not found: {agent_dir}")

        # Create real MCP client (not mocked)
        config = MCPConfig(
            credential_provider=StaticCredentialProvider(
                ResolvedCredential(auth_mode="api_key", access_token="test")
            ),
            deploy_url="http://localhost:8000",
            namespace="examples",
        )
        client = DispatchAPIClient(config)
        mcp = create_operator_mcp(client, config)

        ctx = MCPContext()

        # Get the actual functions directly from the tool registry
        start_local_agent_dev_fn = mcp._tool_manager._tools["start_local_agent_dev"].fn
        stop_local_router_fn = mcp._tool_manager._tools["stop_local_router"].fn

        try:
            # Step 1: Stop router to reproduce original slow startup issue
            print("\n" + "=" * 80)
            print("STEP 1: Stopping router to reproduce original issue...")
            print("=" * 80)

            stop_request = StopRouterRequest()
            await stop_local_router_fn(stop_request, ctx)

            # Wait for cleanup
            await asyncio.sleep(1)

            # Verify router is stopped
            router_check = subprocess.run(
                ["lsof", "-i", ":8080"],
                capture_output=True,
            )
            router_stopped = router_check.returncode != 0
            print(f"Router stopped: {router_stopped}")

            # Step 2: Time the start_local_agent_dev function DIRECTLY (router will auto-start)
            print("\n" + "=" * 80)
            print(
                "STEP 2: Calling start_local_agent_dev directly (router will auto-start)..."
            )
            print("=" * 80)

            start_request = StartLocalAgentDevRequest(agent_directory=str(agent_dir))

            start_time = time.time()
            # DIRECT CALL - NO MOCKS, NO WRAPPERS
            result = await start_local_agent_dev_fn(start_request, ctx)
            elapsed = time.time() - start_time

            # Step 3: Validate results
            print("\n" + "=" * 80)
            print("RESULTS")
            print("=" * 80)
            print(f"Status: {result.status}")
            print(f"Agent: {result.agent_name}")
            print(f"Elapsed time: {elapsed:.3f}s")
            print(f"Startup logs: {len(result.startup_logs)} lines")

            # Verify router and agent are running
            router_check = subprocess.run(
                ["lsof", "-i", ":8080"],
                capture_output=True,
            )
            router_running = router_check.returncode == 0
            print(f"Router running: {router_running}")

            pid_file = agent_dir / ".dispatch" / "agent.pid"
            agent_running = pid_file.exists()
            print(f"Agent running: {agent_running}")

            # Assertions
            assert result.status == "running", f"Expected running, got {result.status}"
            assert result.agent_name == "hello_world"
            assert router_running, "Router should be running"
            assert agent_running, "Agent should be running"

            # Performance assertion: should complete in under 5 seconds
            # (allows for real router startup + agent startup)
            assert elapsed < 5.0, (
                f"start_local_agent_dev took {elapsed:.2f}s, expected < 5.0s. "
                f"Optimization may not be working properly."
            )

            print(f"\n✓ Performance test PASSED: {elapsed:.3f}s (target: < 5.0s)")

        finally:
            # Cleanup
            print("\n" + "=" * 80)
            print("CLEANUP: Stopping router and agent...")
            print("=" * 80)

            try:
                cleanup_ctx = MCPContext()
                stop_request = StopRouterRequest()
                await stop_local_router_fn(stop_request, cleanup_ctx)
            except Exception as e:
                print(f"Cleanup warning: {e}")
