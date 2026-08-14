"""Small Git adapter used by both the terminal workflow and Codex instructions."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List


def run_git(args: List[str], cwd: Path, check: bool = True) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True)
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


@dataclass
class RepositoryState:
    root: Path
    branch: str
    status: str
    diff: str
    staged_diff: str
    changed_files: List[str]


def inspect_repository(cwd: Path) -> RepositoryState:
    root = Path(run_git(["rev-parse", "--show-toplevel"], cwd).strip())
    branch = run_git(["branch", "--show-current"], root).strip()
    status = run_git(["status", "--short"], root)
    diff = run_git(["diff", "HEAD"], root, check=False)
    staged_diff = run_git(["diff", "--cached"], root, check=False)
    changed_files = []
    for line in status.splitlines():
        if len(line) >= 4:
            changed_files.append(line[3:].strip().strip('"'))
    untracked = run_git(["ls-files", "--others", "--exclude-standard"], root).splitlines()
    for path in untracked:
        if path not in changed_files:
            changed_files.append(path)
        file_path = root / path
        if file_path.is_file():
            untracked_diff = subprocess.run(
                ["git", "diff", "--no-index", "--", "/dev/null", path],
                cwd=root,
                text=True,
                capture_output=True,
            ).stdout
            diff += untracked_diff
    return RepositoryState(root, branch, status, diff, staged_diff, changed_files)


def commit_all_changes(root: Path, files: List[str], message: str) -> None:
    if not files:
        raise RuntimeError("no files selected for commit")
    run_git(["add", "--", *files], root)
    run_git(["commit", "-m", message], root)


def push(root: Path) -> str:
    return run_git(["push"], root)
