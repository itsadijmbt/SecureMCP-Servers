#!/usr/bin/env python3
"""Enforce release version policy for CI workflows."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ci_git import fetch_tags, get_latest_tag

SEMVER_VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


@dataclass(frozen=True)
class PolicyResult:
    mode: str
    current_version: str
    current_tag: str
    baseline_ref: str
    baseline_version: str | None
    source_changed: bool
    requires_version_bump: bool
    has_version_bump: bool
    should_release: bool
    relevant_pyproject_changed: bool
    failure_reason: str | None


def parse_version(version: str) -> tuple[int, int, int]:
    match = SEMVER_VERSION_RE.fullmatch(version)
    if not match:
        raise ValueError(f"Unsupported version format: {version}")
    return tuple(int(part) for part in match.groups())


def compare_versions(current_version: str, baseline_version: str) -> int:
    current = parse_version(current_version)
    baseline = parse_version(baseline_version)
    if current > baseline:
        return 1
    if current < baseline:
        return -1
    return 0


def is_relevant_pyproject_change(
    current_pyproject: dict[str, Any], baseline_pyproject: dict[str, Any] | None
) -> bool:
    if baseline_pyproject is None:
        return False

    current_project = dict(current_pyproject.get("project", {}))
    baseline_project = dict(baseline_pyproject.get("project", {}))
    current_project.pop("version", None)
    baseline_project.pop("version", None)

    current_tool = current_pyproject.get("tool", {})
    baseline_tool = baseline_pyproject.get("tool", {})

    relevant_current_tool = {
        "hatch": current_tool.get("hatch", {}),
        "uv": current_tool.get("uv", {}),
    }
    relevant_baseline_tool = {
        "hatch": baseline_tool.get("hatch", {}),
        "uv": baseline_tool.get("uv", {}),
    }

    return (
        current_pyproject.get("build-system", {})
        != baseline_pyproject.get("build-system", {})
        or current_project != baseline_project
        or relevant_current_tool != relevant_baseline_tool
    )


def evaluate_policy(
    *,
    mode: str,
    source_changed: bool,
    current_pyproject: dict[str, Any],
    baseline_pyproject: dict[str, Any] | None,
    baseline_ref: str,
    baseline_version: str | None,
) -> PolicyResult:
    current_version = current_pyproject["project"]["version"]
    current_tag = f"v{current_version}"
    relevant_change = is_relevant_pyproject_change(
        current_pyproject, baseline_pyproject
    )
    bump_required = source_changed or relevant_change
    comparison = (
        1
        if baseline_version is None
        else compare_versions(current_version, baseline_version)
    )
    has_bump = comparison > 0
    should_release = mode == "release" and has_bump
    failure_reason: str | None = None

    if mode == "release":
        if baseline_version is not None and comparison < 0:
            failure_reason = f"Current version {current_tag} is behind latest release {baseline_ref}."
        elif baseline_version is not None and bump_required and comparison <= 0:
            failure_reason = (
                "Changes require a semantic version bump, "
                f"but {current_tag} is not greater than {baseline_ref}."
            )
    elif baseline_version is not None and bump_required and comparison <= 0:
        failure_reason = (
            "Changes require a semantic version bump compared with "
            f"{baseline_ref} version v{baseline_version}, "
            f"but current version is {current_tag}."
        )

    return PolicyResult(
        mode=mode,
        current_version=current_version,
        current_tag=current_tag,
        baseline_ref=baseline_ref,
        baseline_version=baseline_version,
        source_changed=source_changed,
        requires_version_bump=bump_required,
        has_version_bump=has_bump,
        should_release=should_release,
        relevant_pyproject_changed=relevant_change,
        failure_reason=failure_reason,
    )


def load_pyproject(path: Path) -> dict[str, Any]:
    with path.open("rb") as file_obj:
        return tomllib.load(file_obj)


def load_pyproject_from_ref(ref: str | None, repo_root: Path) -> dict[str, Any] | None:
    if ref is None:
        return None

    result = subprocess.run(
        ["git", "show", f"{ref}:pyproject.toml"],
        check=False,
        capture_output=True,
        text=True,
        cwd=repo_root,
    )
    if result.returncode != 0:
        return None
    return tomllib.loads(result.stdout)


def write_github_outputs(result: PolicyResult) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return

    outputs = {
        "current_version": result.current_version,
        "current_tag": result.current_tag,
        "baseline_ref": result.baseline_ref,
        "source_changed": str(result.source_changed).lower(),
        "requires_version_bump": str(result.requires_version_bump).lower(),
        "has_version_bump": str(result.has_version_bump).lower(),
        "relevant_pyproject_changed": str(result.relevant_pyproject_changed).lower(),
        "should_release": str(result.should_release).lower(),
    }

    with Path(output_path).open("a", encoding="utf-8") as file_obj:
        for key, value in outputs.items():
            file_obj.write(f"{key}={value}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("feature-branch", "release"),
        required=True,
        help="Execution mode for workflow messaging.",
    )
    parser.add_argument(
        "--source-changed",
        choices=("true", "false"),
        required=True,
        help="Whether the workflow determined that release-relevant non-pyproject files changed.",
    )
    parser.add_argument(
        "--pyproject-baseline-ref",
        default="",
        help="Git ref to use as the pyproject.toml comparison baseline.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd()
    fetch_tags()

    latest_tag = get_latest_tag()
    current_pyproject = load_pyproject(repo_root / "pyproject.toml")
    source_changed = args.source_changed == "true"

    if args.mode == "feature-branch":
        pyproject_baseline_ref = args.pyproject_baseline_ref
        baseline_pyproject = load_pyproject_from_ref(pyproject_baseline_ref, repo_root)
        baseline_ref = pyproject_baseline_ref or "feature branch base"
        baseline_version = (
            None
            if baseline_pyproject is None
            else str(baseline_pyproject["project"]["version"])
        )
    else:
        pyproject_baseline_ref = args.pyproject_baseline_ref or latest_tag
        baseline_pyproject = load_pyproject_from_ref(pyproject_baseline_ref, repo_root)
        baseline_ref = latest_tag or "initial repository state"
        baseline_version = latest_tag[1:] if latest_tag is not None else None

    result = evaluate_policy(
        mode=args.mode,
        source_changed=source_changed,
        current_pyproject=current_pyproject,
        baseline_pyproject=baseline_pyproject,
        baseline_ref=baseline_ref,
        baseline_version=baseline_version,
    )
    write_github_outputs(result)

    print(f"Version policy check ({args.mode})")
    print(f"  baseline: {result.baseline_ref}")
    print(f"  current tag: {result.current_tag}")
    print(f"  pyproject baseline: {pyproject_baseline_ref or '(none)'}")
    print(f"  source changed: {str(result.source_changed).lower()}")
    print(f"  requires bump: {str(result.requires_version_bump).lower()}")
    print(f"  should release: {str(result.should_release).lower()}")

    if result.failure_reason:
        print(result.failure_reason, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
