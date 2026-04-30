"""Unit tests for MCP operator tools."""

import os
import signal
import tempfile
from pathlib import Path
from unittest.mock import call, patch

import pytest

from dispatch_cli.auth_provider import ResolvedCredential, StaticCredentialProvider
from dispatch_cli.mcp.client import OperatorBackendClient
from dispatch_cli.mcp.operator.tools import (
    cleanup_all_agent_processes,
    read_agent_log_file,
    write_pid_file,
)


def _cleanup_agent_process_by_pid_file(pid_file_path: str) -> bool:
    try:
        with open(pid_file_path) as f:
            pid = int(f.read().strip())

        try:
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            os.remove(pid_file_path)
            return True
        except ProcessLookupError:
            os.remove(pid_file_path)
            return False
    except (OSError, ValueError):
        return False


class FakeOperatorBackendClient:
    def close(self) -> None:
        raise AssertionError("Not expected in prompt tests")

    def list_namespaces(self) -> dict:
        raise AssertionError("Not expected in prompt tests")

    def list_agents(self, namespace: str | None = None, limit: int = 50) -> list[dict]:
        raise AssertionError("Not expected in prompt tests")

    def get_agent_info(self, agent_id: str, namespace: str | None = None) -> dict:
        raise AssertionError("Not expected in prompt tests")

    def delete_agent(self, agent_id: str, namespace: str | None = None) -> dict:
        raise AssertionError("Not expected in prompt tests")

    def stop_agent(self, agent_name: str, namespace: str | None = None):
        raise AssertionError("Not expected in prompt tests")

    def reboot_agent(self, agent_name: str, namespace: str | None = None):
        raise AssertionError("Not expected in prompt tests")

    def get_agent_logs(
        self,
        agent_name: str,
        version: str = "latest",
        namespace: str | None = None,
        limit: int = 100,
        **kwargs,
    ) -> dict:
        raise AssertionError("Not expected in prompt tests")

    def publish_event(
        self,
        topic: str,
        payload: dict,
        namespace: str | None = None,
        sender_id: str = "mcp-cli",
        **kwargs,
    ) -> dict:
        raise AssertionError("Not expected in prompt tests")

    def get_topic_schema(self, topic: str, namespace: str | None = None) -> dict:
        raise AssertionError("Not expected in prompt tests")

    def list_topics(self, namespace: str):
        raise AssertionError("Not expected in prompt tests")

    def get_recent_events(
        self, namespace: str, topic: str | None = None, limit: int = 20
    ):
        raise AssertionError("Not expected in prompt tests")

    def get_event_trace(self, trace_id: str, namespace: str):
        raise AssertionError("Not expected in prompt tests")

    def get_recent_traces(
        self, namespace: str, topic: str | None = None, limit: int = 50
    ):
        raise AssertionError("Not expected in prompt tests")

    async def invoke_function_async(
        self,
        agent_name: str,
        function_name: str,
        payload: dict,
        namespace: str | None = None,
        timeout_seconds: int | None = None,
    ) -> dict:
        raise AssertionError("Not expected in prompt tests")

    def get_invocation_status(self, invocation_id: str, namespace: str | None = None):
        raise AssertionError("Not expected in prompt tests")

    async def get_invocation_status_async(
        self, invocation_id: str, namespace: str | None = None
    ) -> dict:
        raise AssertionError("Not expected in prompt tests")

    async def get_deploy_status_async(
        self, job_id: str, namespace: str | None = None
    ) -> dict:
        raise AssertionError("Not expected in prompt tests")

    def list_long_term_memories(self, agent_name: str, namespace: str):
        raise AssertionError("Not expected in prompt tests")

    async def create_schedule(self, request):
        raise AssertionError("Not expected in prompt tests")

    async def list_schedules(self, request):
        raise AssertionError("Not expected in prompt tests")

    async def get_schedule(self, request):
        raise AssertionError("Not expected in prompt tests")

    async def update_schedule(self, request):
        raise AssertionError("Not expected in prompt tests")

    async def delete_schedule(self, request):
        raise AssertionError("Not expected in prompt tests")

    async def submit_feedback(self, payload: dict) -> None:
        raise AssertionError("Not expected in prompt tests")


@pytest.mark.unit
class TestMCPPrompts:
    """Test that MCP prompt methods return expected text at runtime.

    The prompt functions load markdown files via Path.read_text() when invoked.
    If a file is renamed or deleted, the MCP server won't fail at startup — it
    fails later with a FileNotFoundError when a client calls the prompt. These
    tests exercise the actual runtime code path to catch that.
    """

    @pytest.fixture()
    def mcp_server(self):
        """Create an MCP server instance with a mock API client."""
        from dispatch_cli.mcp.config import MCPConfig
        from dispatch_cli.mcp.operator.tools import create_operator_mcp

        config = MCPConfig(
            credential_provider=StaticCredentialProvider(
                ResolvedCredential(auth_mode="api_key", access_token="test-key")
            ),
            namespace="test-ns",
        )
        client: OperatorBackendClient = FakeOperatorBackendClient()
        return create_operator_mcp(client, config)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "prompt_name",
        [
            "getting_started",
            "fork_session",
        ],
    )
    async def test_prompt_returns_non_empty_text(self, mcp_server, prompt_name: str):
        result = await mcp_server.get_prompt(prompt_name)
        assert result.messages, f"Prompt '{prompt_name}' returned no messages"
        text = result.messages[0].content.text
        assert len(text.strip()) > 0, f"Prompt '{prompt_name}' returned empty text"


@pytest.mark.unit
class TestStopLocalRouter:
    """Test the stop_local_router cleanup logic."""

    @pytest.mark.asyncio
    async def test_stop_router_cleans_up_all_agent_pid_files(self):
        """Test that cleanup_all_agent_processes finds and kills all agent processes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create multiple agent directories with PID files
            pids_to_kill = []

            for i, agent_name in enumerate(["agent1", "agent2", "agent3"]):
                agent_dir = tmpdir_path / agent_name
                agent_dir.mkdir()
                dispatch_dir = agent_dir / ".dispatch"
                dispatch_dir.mkdir()
                pid_file = dispatch_dir / "agent.pid"

                # Write PID file
                fake_pid = 10000 + i
                pid_file.write_text(str(fake_pid))
                pids_to_kill.append(fake_pid)

            # Mock os.killpg and os.getpgid to track calls
            with (
                patch("os.killpg") as mock_killpg,
                patch("os.getpgid", side_effect=lambda pid: pid),
            ):
                # Call the actual cleanup function
                cleaned = await cleanup_all_agent_processes(base_dir=str(tmpdir_path))

                # Verify return value
                assert cleaned == 3

                # Verify all PIDs were killed (killpg kills process groups)
                assert mock_killpg.call_count == 3
                expected_calls = [
                    call(pid, signal.SIGTERM) for pid in sorted(pids_to_kill)
                ]
                # Sort both actual and expected calls for comparison
                actual_calls = sorted(mock_killpg.call_args_list, key=lambda c: c[0][0])
                assert actual_calls == expected_calls

            # Verify all PID files were cleaned up
            remaining_pids = list(tmpdir_path.rglob(".dispatch/agent.pid"))
            assert len(remaining_pids) == 0

    @pytest.mark.asyncio
    async def test_stop_router_handles_missing_pid_files(self):
        """Test that cleanup_all_agent_processes works when no PID files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create agent directories but no PID files
            for agent_name in ["agent1", "agent2"]:
                agent_dir = tmpdir_path / agent_name
                agent_dir.mkdir()
                dispatch_dir = agent_dir / ".dispatch"
                dispatch_dir.mkdir()
                # Intentionally don't create agent.pid

            # Mock os.killpg to verify it's not called
            with patch("os.killpg") as mock_killpg:
                # Call the actual cleanup function
                cleaned = await cleanup_all_agent_processes(base_dir=str(tmpdir_path))

                # Verify return value is 0
                assert cleaned == 0

                # Verify no kills were attempted
                mock_killpg.assert_not_called()


@pytest.mark.unit
class TestPIDFileLifecycle:
    """Test PID file creation, persistence, and cleanup through the full lifecycle."""

    @pytest.mark.asyncio
    async def test_write_pid_file_creates_file_correctly(self):
        """Test that write_pid_file creates PID file correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_dir = Path(tmpdir) / "test_agent"
            agent_dir.mkdir()

            # Call the real helper function
            test_pid = 12345
            pid_file_path = write_pid_file(str(agent_dir), test_pid)

            # Verify file exists at correct location
            assert os.path.exists(pid_file_path)
            assert Path(pid_file_path) == agent_dir / ".dispatch" / "agent.pid"

            # Verify content
            with open(pid_file_path) as f:
                assert f.read() == "12345"

    @pytest.mark.asyncio
    async def test_cleanup_finds_pid_files_recursively(self):
        """Test that cleanup finds PID files in nested directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create nested agent directories
            (tmpdir_path / "examples" / "agent1" / ".dispatch").mkdir(parents=True)
            (tmpdir_path / "examples" / "agent2" / ".dispatch").mkdir(parents=True)
            (tmpdir_path / "projects" / "agent3" / ".dispatch").mkdir(parents=True)

            # Create PID files
            pids = [10001, 10002, 10003]
            (
                tmpdir_path / "examples" / "agent1" / ".dispatch" / "agent.pid"
            ).write_text(str(pids[0]))
            (
                tmpdir_path / "examples" / "agent2" / ".dispatch" / "agent.pid"
            ).write_text(str(pids[1]))
            (
                tmpdir_path / "projects" / "agent3" / ".dispatch" / "agent.pid"
            ).write_text(str(pids[2]))

            # Mock os.killpg and os.getpgid
            with (
                patch("os.killpg") as mock_killpg,
                patch("os.getpgid", side_effect=lambda pid: pid),
            ):
                # Call cleanup
                cleaned = await cleanup_all_agent_processes(base_dir=str(tmpdir_path))

                # Verify all processes were found and killed
                assert cleaned == 3
                assert mock_killpg.call_count == 3

            # Verify all PID files were removed
            assert not list(tmpdir_path.rglob(".dispatch/agent.pid"))

    @pytest.mark.asyncio
    async def test_cleanup_agent_process_by_pid_file(self):
        """Test the cleanup_agent_process_by_pid_file helper function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_dir = Path(tmpdir) / "test_agent"
            agent_dir.mkdir()

            # Create PID file using helper
            pid_file_path = write_pid_file(str(agent_dir), 11111)

            # Verify it was created
            assert os.path.exists(pid_file_path)

            # Mock os.killpg and os.getpgid, then call cleanup helper
            with (
                patch("os.killpg") as mock_killpg,
                patch("os.getpgid", return_value=11111),
            ):
                result = _cleanup_agent_process_by_pid_file(pid_file_path)

                # Verify process group was killed
                assert result is True
                mock_killpg.assert_called_once_with(11111, signal.SIGTERM)

            # Verify PID file was removed
            assert not os.path.exists(pid_file_path)

    @pytest.mark.asyncio
    async def test_cleanup_handles_already_dead_process(self):
        """Test cleanup when process is already dead."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_dir = Path(tmpdir) / "test_agent"
            agent_dir.mkdir()

            # Create PID file
            pid_file_path = write_pid_file(str(agent_dir), 99999)

            # Mock os.killpg and os.getpgid to raise ProcessLookupError
            with (
                patch("os.killpg", side_effect=ProcessLookupError),
                patch("os.getpgid", return_value=99999),
            ):
                result = _cleanup_agent_process_by_pid_file(pid_file_path)

                # Should return False (process wasn't killed because it was already dead)
                assert result is False

            # Verify PID file was still removed
            assert not os.path.exists(pid_file_path)

    @pytest.mark.asyncio
    async def test_read_agent_log_file(self):
        """Test the read_agent_log_file helper function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_dir = Path(tmpdir) / "test_agent"
            agent_dir.mkdir()
            logs_dir = agent_dir / ".dispatch" / "logs"
            logs_dir.mkdir(parents=True)

            # Create log file
            log_file = logs_dir / "agent.log"
            test_logs = [
                "2025-12-17 - INFO - Test log 1\n",
                "2025-12-17 - INFO - Test log 2\n",
                "2025-12-17 - INFO - Test log 3\n",
            ]
            log_file.write_text("".join(test_logs))

            # Call the real helper function
            logs = read_agent_log_file(str(agent_dir), lines=10)

            # Verify result
            assert len(logs) == 3
            assert logs[0] == "2025-12-17 - INFO - Test log 1"
            assert logs[1] == "2025-12-17 - INFO - Test log 2"
            assert logs[2] == "2025-12-17 - INFO - Test log 3"

    @pytest.mark.asyncio
    async def test_read_agent_log_file_filters_null_bytes(self):
        """Test that read_agent_log_file filters out null byte lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_dir = Path(tmpdir) / "test_agent"
            agent_dir.mkdir()
            logs_dir = agent_dir / ".dispatch" / "logs"
            logs_dir.mkdir(parents=True)

            # Create log file with null bytes
            log_file = logs_dir / "agent.log"
            test_logs = [
                "Good log line 1\n",
                "\x00\x00\x00\x00\x00\n",  # Null bytes - should be filtered
                "Good log line 2\n",
                "   \n",  # Empty line - should be filtered
                "Good log line 3\n",
            ]
            log_file.write_text("".join(test_logs))

            # Call the real helper function
            logs = read_agent_log_file(str(agent_dir), lines=10)

            # Should only have the good lines
            assert len(logs) == 3
            assert logs[0] == "Good log line 1"
            assert logs[1] == "Good log line 2"
            assert logs[2] == "Good log line 3"

    @pytest.mark.asyncio
    async def test_read_agent_log_file_truncates_long_lines(self):
        """Test that read_agent_log_file truncates very long lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_dir = Path(tmpdir) / "test_agent"
            agent_dir.mkdir()
            logs_dir = agent_dir / ".dispatch" / "logs"
            logs_dir.mkdir(parents=True)

            # Create log file with very long line
            log_file = logs_dir / "agent.log"
            long_line = "X" * 1000 + "\n"
            log_file.write_text(long_line)

            # Call with default max_line_length (500)
            logs = read_agent_log_file(str(agent_dir), lines=10)

            # Should be truncated (500 chars + "... (truncated)" = 515 total)
            assert len(logs) == 1
            assert len(logs[0]) == 515  # 500 + "... (truncated)" (15 chars)
            assert logs[0].endswith("... (truncated)")
            assert logs[0].startswith(
                "X" * 100
            )  # Verify it's the original content truncated

    @pytest.mark.asyncio
    async def test_cleanup_handles_dead_processes(self):
        """Test that cleanup handles ProcessLookupError gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create agent directory with PID file
            agent_dir = tmpdir_path / "test_agent"
            agent_dir.mkdir()
            dispatch_dir = agent_dir / ".dispatch"
            dispatch_dir.mkdir()
            pid_file = dispatch_dir / "agent.pid"

            # Write PID of a process that doesn't exist
            pid_file.write_text("99999")

            # Mock os.killpg and os.getpgid to raise ProcessLookupError
            with (
                patch("os.killpg", side_effect=ProcessLookupError),
                patch("os.getpgid", return_value=99999),
            ):
                # Call the actual cleanup function
                cleaned = await cleanup_all_agent_processes(base_dir=str(tmpdir_path))

                # Should return 0 since process was already dead
                assert cleaned == 0

            # Verify PID file was still cleaned up
            assert not pid_file.exists()
