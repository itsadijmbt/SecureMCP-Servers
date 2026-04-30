"""Integration tests for CLI commands."""

import os
import tempfile
from unittest.mock import MagicMock, patch

import yaml
from typer.testing import CliRunner

from dispatch_cli.main import app
from dispatch_cli.utils import DISPATCH_DIR, DISPATCH_LISTENER_FILE, DISPATCH_YAML


class TestInitCommand:
    def test_init_creates_dispatch_directory(self):
        """Test that init command creates .dispatch directory with files."""
        runner = CliRunner(echo_stdin=True)

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a side effect that creates pyproject.toml when uv init is called
            def mock_subprocess_run(args, **kwargs):
                if args[0] == "uv" and args[1] == "init":
                    # Create pyproject.toml as uv init would
                    pyproject_path = os.path.join(
                        kwargs.get("cwd", tmpdir), "pyproject.toml"
                    )
                    with open(pyproject_path, "w") as f:
                        f.write(
                            '[project]\nname = "test"\nrequires-python = ">=3.13"\n'
                        )
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = ""
                mock_result.stderr = ""
                return mock_result

            with patch("typer.prompt", return_value="agent.py"):
                with patch("typer.confirm", return_value=True):
                    with patch("subprocess.run", side_effect=mock_subprocess_run):
                        result = runner.invoke(app, ["agent", "init", "--path", tmpdir])

            # Check command succeeded
            if result.exit_code != 0:
                print(f"Exit code: {result.exit_code}")
                print(f"Output: {result.output}")
                if result.exception:
                    print(f"Exception: {result.exception}")
            assert result.exit_code == 0

            # Check .dispatch directory was created
            dispatch_dir = os.path.join(tmpdir, DISPATCH_DIR)
            assert os.path.exists(dispatch_dir)

            # Check listener was created
            listener_path = os.path.join(dispatch_dir, DISPATCH_LISTENER_FILE)
            assert os.path.exists(listener_path)

            # Check agent.py was created
            agent_path = os.path.join(tmpdir, "agent.py")
            assert os.path.exists(agent_path)

            # Check dispatch.yaml configuration exists
            config_path = os.path.join(tmpdir, DISPATCH_YAML)
            assert os.path.exists(config_path)

    def test_init_with_existing_agent_py(self):
        """Test init with existing agent.py file."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create existing agent.py
            agent_path = os.path.join(tmpdir, "agent.py")
            with open(agent_path, "w") as f:
                f.write(
                    'from dispatch_agents import on\n\n@on(topic="test")\nasync def trigger(message: dispatch_agents.Message):\n    return "existing"'
                )

            # Create a side effect that creates pyproject.toml when uv init is called
            def mock_subprocess_run(args, **kwargs):
                if args[0] == "uv" and args[1] == "init":
                    # Create pyproject.toml as uv init would
                    pyproject_path = os.path.join(
                        kwargs.get("cwd", tmpdir), "pyproject.toml"
                    )
                    with open(pyproject_path, "w") as f:
                        f.write(
                            '[project]\nname = "test"\nrequires-python = ">=3.13"\n'
                        )
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = ""
                mock_result.stderr = ""
                return mock_result

            # Mock the prompt to use default entrypoint and confirm creation
            with patch("typer.prompt", return_value="agent.py"):
                with patch("typer.confirm", return_value=True):
                    with patch("subprocess.run", side_effect=mock_subprocess_run):
                        result = runner.invoke(app, ["agent", "init", "--path", tmpdir])

            if result.exit_code != 0:
                print(f"Exit code: {result.exit_code}")
                print(f"Output: {result.output}")
                print(f"Exception: {result.exception}")
            assert result.exit_code == 0
            assert os.path.exists(os.path.join(tmpdir, ".dispatch"))

            # Verify entrypoint was saved to dispatch.yaml
            config_path = os.path.join(tmpdir, DISPATCH_YAML)
            assert os.path.exists(config_path)
            with open(config_path) as fh:
                config = yaml.safe_load(fh)
            assert config["entrypoint"] == "agent.py"

    def test_init_with_pyproject_config(self):
        """
        Test init reads configuration from pyproject.toml.
        """
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create pyproject.toml with dispatch config including entrypoint
            pyproject_path = os.path.join(tmpdir, "pyproject.toml")
            with open(pyproject_path, "w") as f:
                f.write(
                    """
[project]
name = "test"
requires-python = ">=3.13"

[tool.dispatch]
base_image = "python:3.11-slim"
port = 3000
entrypoint = "my_agent.py"
system_packages = []
"""
                )

            # Create the agent file with @on decorator
            agent_path = os.path.join(tmpdir, "my_agent.py")
            with open(agent_path, "w") as f:
                f.write(
                    "from dispatch_agents import on\n\n@on(topic='test')\nasync def handler(message: dispatch_agents.Message):\n    return 'Hello from my_agent'"
                )

            def mock_subprocess_run(args, **kwargs):
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = ""
                mock_result.stderr = ""
                return mock_result

            # Mock the prompts: confirm creation and provide namespace
            with patch("typer.confirm", return_value=True):
                with patch("typer.prompt", return_value="test-namespace"):
                    with patch("subprocess.run", side_effect=mock_subprocess_run):
                        result = runner.invoke(app, ["agent", "init", "--path", tmpdir])

            if result.exit_code != 0:
                print(f"Exit code: {result.exit_code}")
                print(f"Output: {result.output}")
                print(f"Exception: {result.exception}")
            assert result.exit_code == 0

            # make sure only the files we expect are created
            assert os.path.exists(
                os.path.join(tmpdir, ".dispatch", DISPATCH_LISTENER_FILE)
            )
            assert os.path.exists(os.path.join(tmpdir, "my_agent.py"))
            assert not os.path.exists(os.path.join(tmpdir, "agent.py"))

            with open(os.path.join(tmpdir, DISPATCH_YAML)) as fh:
                config = yaml.safe_load(fh)
            assert config["entrypoint"] == "my_agent.py"

    def test_init_does_not_prompt_for_sdk_upgrade_after_scaffolding(self):
        """Init should not run the SDK suggestion check after creating the project."""
        runner = CliRunner()

        with tempfile.TemporaryDirectory() as tmpdir:

            def mock_subprocess_run(args, **kwargs):
                if args[0] == "uv" and args[1] == "init":
                    pyproject_path = os.path.join(
                        kwargs.get("cwd", tmpdir), "pyproject.toml"
                    )
                    with open(pyproject_path, "w") as f:
                        f.write(
                            '[project]\nname = "test"\nrequires-python = ">=3.13"\n'
                        )
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = ""
                mock_result.stderr = ""
                return mock_result

            with patch("typer.prompt", return_value="agent.py"):
                with patch("typer.confirm", return_value=True):
                    with patch("subprocess.run", side_effect=mock_subprocess_run):
                        with patch(
                            "dispatch_cli.commands.agent._check_and_suggest_sdk_update"
                        ) as suggest_sdk_update:
                            result = runner.invoke(
                                app, ["agent", "init", "--path", tmpdir]
                            )

            assert result.exit_code == 0
            suggest_sdk_update.assert_not_called()
