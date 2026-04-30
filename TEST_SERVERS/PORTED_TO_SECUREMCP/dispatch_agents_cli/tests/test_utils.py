"""Unit tests for utility functions."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from dispatch_cli.utils import (
    DISPATCH_LISTENER_FILE,
    SDK_DEPENDENCY,
    get_sdk_dependency,
    prompt_for_missing_config,
    read_project_config,
    validate_dispatch_project,
)

SDK_PACKAGE = "dispatch-agents"


class TestSdkInstallGuidance:
    """Ensure customer-facing SDK guidance uses the packaged install path."""

    def test_sdk_dependency_constant_points_to_package(self):
        """SDK_DEPENDENCY should default to the published SDK package."""
        assert SDK_DEPENDENCY == SDK_PACKAGE

    def test_get_sdk_dependency_with_version_points_to_package(self):
        """get_sdk_dependency() should resolve to the packaged SDK name."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SDK_DEPENDENCY", None)
            result = get_sdk_dependency()
        assert result == SDK_PACKAGE

    def test_get_sdk_dependency_fallback_points_to_package(self):
        """Fallback SDK dependency (no version detected) should use the package."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("SDK_DEPENDENCY", None)
            result = get_sdk_dependency()
        assert result == SDK_PACKAGE

    def test_validate_sdk_version_above_minimum_is_valid(self):
        """SDK above minimum but below current should be 'valid', not 'outdated'."""
        from dispatch_cli.version_check import validate_sdk_version

        with patch(
            "dispatch_cli.version_check.get_sdk_version_requirements",
            return_value={
                "cli_current": "99.0.0",
                "cli_minimum": "0.0.1",
                "sdk_current": "99.0.0",
                "sdk_minimum": "0.0.1",
            },
        ):
            status, message = validate_sdk_version("0.0.2", "http://fake")
        assert status == "valid"
        assert message is None

    def test_version_check_sdk_blocked_command(self):
        """Blocked SDK upgrade message should use the packaged upgrade command."""
        from dispatch_cli.version_check import validate_sdk_version

        with patch(
            "dispatch_cli.version_check.get_sdk_version_requirements",
            return_value={
                "cli_current": "99.0.0",
                "cli_minimum": "1.0.0",
                "sdk_current": "99.0.0",
                "sdk_minimum": "1.0.0",
            },
        ):
            status, message = validate_sdk_version("0.0.1", "http://fake")
        assert status == "blocked"
        assert "uv add dispatch-agents --upgrade" in message

    def test_version_check_sdk_not_installed_command(self):
        """SDK not-installed message should use the packaged install command."""
        from dispatch_cli.version_check import check_sdk_version_suggestion

        with patch(
            "dispatch_cli.version_check.get_cli_suggested_sdk_version",
            return_value="1.0.0",
        ):
            status, message = check_sdk_version_suggestion(None)
        assert status == "not_installed"
        assert "uv add dispatch-agents" in message
        assert "--upgrade" not in message

    def test_version_check_sdk_outdated_command(self):
        """SDK outdated message should use the packaged upgrade command."""
        from dispatch_cli.version_check import check_sdk_version_suggestion

        with patch(
            "dispatch_cli.version_check.get_cli_suggested_sdk_version",
            return_value="2.0.0",
        ):
            status, message = check_sdk_version_suggestion("1.0.0")
        assert status == "outdated"
        assert "uv add dispatch-agents --upgrade" in message

    def test_cli_update_check_is_silent_when_stdout_is_not_a_tty(self, capsys):
        """Machine-readable invocations should not emit update notices on stdout."""
        from dispatch_cli.version_check import check_and_notify_cli_update

        with (
            patch("sys.stdout.isatty", return_value=False),
            patch("dispatch_cli.version_check._should_check_version") as should_check,
            patch("dispatch_cli.version_check.get_sdk_version_requirements") as get_req,
            patch("dispatch_cli.version_check._get_version", return_value="0.1.0"),
        ):
            check_and_notify_cli_update("https://dispatchagents.work")

        should_check.assert_not_called()
        get_req.assert_not_called()
        captured = capsys.readouterr()
        assert captured.out == ""


class TestDetectProjectConfig:
    def test_reads_tool_dispatch_config(self):
        """Should read [tool.dispatch] section from pyproject.toml."""
        pyproject_content = """
[tool.dispatch]
base_image = "python:3.11-slim"
port = 3000
"""

        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = os.path.join(tmpdir, "pyproject.toml")
            with open(pyproject_path, "w") as f:
                f.write(pyproject_content)

            config = read_project_config(tmpdir)

        # Only keys present in pyproject.toml and in DEFAULT_CONFIG are returned
        # "port" is not in DEFAULT_CONFIG so it's filtered out (shown in warning)
        assert config == {"base_image": "python:3.11-slim"}


class TestEntrypointConfig:
    def test_discovers_agent_py(self):
        """Should discover agent.py if it exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_path = os.path.join(tmpdir, "agent.py")
            with open(agent_path, "w") as f:
                f.write(
                    "from dispatch_agents import on\n\n@on(topic='test')\nasync def trigger(message: dispatch_agents.Message): pass"
                )

            config = {"entrypoint": None}
            with patch(
                "typer.prompt",
                side_effect=["test-namespace", "agent.py", "python:3.11-slim", ""],
            ):
                # prompt_for_missing_config returns only the updated config (not a tuple)
                # Order: namespace, entrypoint, base_image, system_packages
                config = prompt_for_missing_config(config, path=tmpdir)
                entrypoint = config["entrypoint"]

        assert entrypoint == "agent.py"


class TestValidateDispatchProject:
    def test_returns_true_when_files_exist(self):
        """Should return True when files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # create the .dispatch directory
            dispatch_dir = os.path.join(tmpdir, ".dispatch")
            os.makedirs(dispatch_dir)
            # create the pyproject.toml file with the entry point
            with open(os.path.join(tmpdir, "pyproject.toml"), "w") as f:
                f.write("[tool.dispatch]\nentrypoint = 'agent.py'\n")
            # create the dispatch.yaml file (required by validate_dispatch_project)
            with open(os.path.join(tmpdir, "dispatch.yaml"), "w") as f:
                f.write("entrypoint: agent.py\nnamespace: test\n")
            # create the agent.py file
            with open(os.path.join(tmpdir, "agent.py"), "w") as f:
                f.write(
                    "from dispatch_agents import on\n\n@on(topic='test')\nasync def trigger(message: dispatch_agents.Message): pass"
                )
            # create the listener file
            Path(os.path.join(dispatch_dir, DISPATCH_LISTENER_FILE)).touch()

            result = validate_dispatch_project(tmpdir)

        assert result

    def test_returns_false_when_dispatch_dir_missing(self):
        """Should return False when .dispatch directory doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = validate_dispatch_project(tmpdir)
            assert not result


class TestPromptForMissingConfig:
    def test_prompts_for_all_missing_options(self):
        """Should prompt for all missing config options."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                "entrypoint": None,
                "base_image": None,
                "system_packages": None,
            }

            with (
                patch(
                    "typer.prompt",
                    side_effect=[
                        "test-namespace",
                        "agent.py",
                        "python:3.11-slim",
                        ["git", "vim"],
                    ],
                ) as mock_prompt,
                patch("typer.confirm", return_value=True),
            ):
                # prompt_for_missing_config returns only the updated config (not a tuple)
                updated_config = prompt_for_missing_config(config, path=tmpdir)

            assert updated_config["entrypoint"] == "agent.py"
            assert updated_config["namespace"] == "test-namespace"
            assert updated_config["base_image"] == "python:3.11-slim"
            assert updated_config["system_packages"] == ["git", "vim"]
            assert mock_prompt.call_count == 4

    def test_skips_existing_config_options(self):
        """Should not prompt for options already in config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = {
                "entrypoint": "main.py",
                "namespace": "test-ns",
                "base_image": None,
            }
            # create main.py with the entrypoint
            with open(os.path.join(tmpdir, "main.py"), "w") as f:
                f.write(
                    "from dispatch_agents import on\n\n@on(topic='test')\nasync def handler(message: dispatch_agents.Message): pass"
                )

            with patch(
                "typer.prompt", side_effect=["python:3.11-slim", []]
            ) as mock_prompt:
                # prompt_for_missing_config returns only the updated config (not a tuple)
                updated_config = prompt_for_missing_config(config, path=tmpdir)

            # Should keep existing values
            assert updated_config["entrypoint"] == "main.py"
            assert updated_config["namespace"] == "test-ns"

            # Should prompt for missing ones
            assert updated_config["base_image"] == "python:3.11-slim"
            assert updated_config["system_packages"] == []
            assert mock_prompt.call_count == 2
