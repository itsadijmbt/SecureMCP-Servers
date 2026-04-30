"""Tests for source package creation, including .gitignore filtering."""

import os
import tarfile
import tempfile
from unittest.mock import patch

from dispatch_cli.commands.agent import create_source_package


def _create_agent_project(
    tmpdir: str, files: dict[str, str], gitignore: str = ""
) -> str:
    """Create a minimal agent project structure for testing.

    Args:
        tmpdir: Root temp directory
        files: Mapping of relative path → file content
        gitignore: Contents of .gitignore (empty string = no .gitignore)

    Returns:
        Absolute path to the agent project
    """
    agent_dir = os.path.join(tmpdir, "my-agent")
    os.makedirs(agent_dir)

    # Minimum required files
    pyproject = (
        '[project]\nname = "my-agent"\nversion = "0.1.0"\nrequires-python = ">=3.12"\n'
    )
    dispatch_yaml = "agent_name: my-agent\nentrypoint: agent.py\n"

    with open(os.path.join(agent_dir, "pyproject.toml"), "w") as f:
        f.write(pyproject)
    with open(os.path.join(agent_dir, ".dispatch.yaml"), "w") as f:
        f.write(dispatch_yaml)

    # Create .dispatch directory (required by create_source_package)
    os.makedirs(os.path.join(agent_dir, ".dispatch"), exist_ok=True)

    if gitignore:
        with open(os.path.join(agent_dir, ".gitignore"), "w") as f:
            f.write(gitignore)

    # Create test files
    for rel_path, content in files.items():
        full_path = os.path.join(agent_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    return agent_dir


def _extract_tarball_files(tarball_path: str) -> set[str]:
    """Extract file paths from a tarball (relative, normalized)."""
    with tarfile.open(tarball_path, "r:gz") as tar:
        return {
            m.name.removeprefix("./").removeprefix("agent/")
            for m in tar.getmembers()
            if m.isfile() and "agent/" in m.name
        }


@patch("dispatch_cli.commands.agent.generate_schemas_for_dev")
class TestSourcePackageGitignore:
    """Tests that create_source_package respects .gitignore."""

    def test_includes_source_files(self, mock_schemas):
        """Source files are included in the package."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_dir = _create_agent_project(
                tmpdir,
                {
                    "agent.py": "print('hello')",
                    "utils.py": "# utils",
                },
            )

            tarball = create_source_package(agent_dir, {"agent_name": "my-agent"})
            files = _extract_tarball_files(tarball)

            assert "agent.py" in files
            assert "utils.py" in files

    def test_always_excludes_hardcoded_artifacts(self, mock_schemas):
        """__pycache__, .venv, .env, .git are always excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_dir = _create_agent_project(
                tmpdir,
                {
                    "agent.py": "print('hello')",
                    "__pycache__/module.cpython-312.pyc": "bytecode",
                    ".venv/bin/python": "#!/usr/bin/env python",
                    ".env": "SECRET=123",
                    ".git/config": "[core]",
                },
            )

            tarball = create_source_package(agent_dir, {"agent_name": "my-agent"})
            files = _extract_tarball_files(tarball)

            assert "agent.py" in files
            assert not any("__pycache__" in f for f in files)
            assert not any(".venv" in f for f in files)
            assert ".env" not in files
            assert not any(".git" in f for f in files)

    def test_excludes_gitignored_files(self, mock_schemas):
        """Files matching .gitignore patterns are excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_dir = _create_agent_project(
                tmpdir,
                {
                    "agent.py": "print('hello')",
                    "data/large_model.bin": "binary data",
                    "data/config.json": '{"key": "value"}',
                    "notes.txt": "personal notes",
                    "build/output.js": "compiled",
                },
                gitignore="*.bin\nnotes.txt\nbuild/\n",
            )

            tarball = create_source_package(agent_dir, {"agent_name": "my-agent"})
            files = _extract_tarball_files(tarball)

            # Included
            assert "agent.py" in files
            assert "data/config.json" in files

            # Excluded by .gitignore
            assert "data/large_model.bin" not in files
            assert "notes.txt" not in files
            assert not any("build/" in f for f in files)

    def test_excludes_gitignored_directories(self, mock_schemas):
        """Directories matching .gitignore patterns are excluded entirely."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_dir = _create_agent_project(
                tmpdir,
                {
                    "agent.py": "print('hello')",
                    "dist/bundle.js": "bundled",
                    "dist/bundle.css": "styles",
                    "src/main.py": "# source",
                },
                gitignore="dist/\n",
            )

            tarball = create_source_package(agent_dir, {"agent_name": "my-agent"})
            files = _extract_tarball_files(tarball)

            assert "agent.py" in files
            assert "src/main.py" in files
            assert not any("dist/" in f for f in files)
            assert "dist/bundle.js" not in files

    def test_no_gitignore_still_works(self, mock_schemas):
        """Without .gitignore, only hardcoded artifacts are excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_dir = _create_agent_project(
                tmpdir,
                {
                    "agent.py": "print('hello')",
                    "data/model.bin": "binary",
                    "notes.txt": "personal",
                },
            )
            # No .gitignore

            tarball = create_source_package(agent_dir, {"agent_name": "my-agent"})
            files = _extract_tarball_files(tarball)

            # Without .gitignore, everything is included
            assert "agent.py" in files
            assert "data/model.bin" in files
            assert "notes.txt" in files

    def test_gitignore_wildcard_patterns(self, mock_schemas):
        """Wildcard patterns like *.log and **/*.tmp work."""
        with tempfile.TemporaryDirectory() as tmpdir:
            agent_dir = _create_agent_project(
                tmpdir,
                {
                    "agent.py": "print('hello')",
                    "debug.log": "log output",
                    "logs/app.log": "nested log",
                    "data/cache.tmp": "temp file",
                },
                gitignore="*.log\n**/*.tmp\n",
            )

            tarball = create_source_package(agent_dir, {"agent_name": "my-agent"})
            files = _extract_tarball_files(tarball)

            assert "agent.py" in files
            assert "debug.log" not in files
            assert "logs/app.log" not in files
            assert "data/cache.tmp" not in files
