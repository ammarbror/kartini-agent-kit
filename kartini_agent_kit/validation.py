"""Detect and run the least-surprising project validation command."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple


def detect_validations(root: Path) -> List[List[str]]:
    commands: List[List[str]] = []
    if (root / "package.json").exists():
        try:
            data = json.loads((root / "package.json").read_text(encoding="utf-8"))
            scripts = data.get("scripts", {})
            for name in ("lint", "typecheck", "test", "build"):
                if name in scripts:
                    commands.append(["npm", "run", name])
        except (OSError, json.JSONDecodeError):
            pass
    if (root / "pyproject.toml").exists() or (root / "pytest.ini").exists() or (root / "tests").exists():
        if shutil.which("pytest"):
            commands.append(["pytest"])
        elif (root / "tests").exists():
            commands.append(["python3", "-m", "unittest", "discover", "-s", "tests", "-v"])
    if (root / "Cargo.toml").exists():
        commands.append(["cargo", "test"])
    if (root / "go.mod").exists():
        commands.append(["go", "test", "./..."])
    if (root / "tsconfig.json").exists() and not any(command[0:2] == ["npm", "run"] and command[2] == "typecheck" for command in commands):
        if shutil.which("npx"):
            commands.append(["npx", "tsc", "--noEmit"])
    return commands


def run_validations(root: Path) -> List[Tuple[List[str], int, str]]:
    results = []
    for command in detect_validations(root):
        result = subprocess.run(command, cwd=root, text=True, capture_output=True)
        output = (result.stdout + result.stderr).strip()
        results.append((command, result.returncode, output[-4000:]))
    return results
