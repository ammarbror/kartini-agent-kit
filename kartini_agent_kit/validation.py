"""Detect and run the least-surprising project validation command."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple


def detect_validation(root: Path) -> Optional[List[str]]:
    if (root / "package.json").exists():
        try:
            data = json.loads((root / "package.json").read_text(encoding="utf-8"))
            if "test" in data.get("scripts", {}):
                return ["npm", "test"]
        except (OSError, json.JSONDecodeError):
            pass
    if (root / "pyproject.toml").exists() or (root / "pytest.ini").exists() or (root / "tests").exists():
        return ["python3", "-m", "pytest"]
    if (root / "Cargo.toml").exists():
        return ["cargo", "test"]
    if (root / "go.mod").exists():
        return ["go", "test", "./..."]
    return None


def run_validation(root: Path) -> Tuple[Optional[List[str]], Optional[int], str]:
    command = detect_validation(root)
    if not command:
        return None, None, "No standard validation command detected."
    result = subprocess.run(command, cwd=root, text=True, capture_output=True)
    output = (result.stdout + result.stderr).strip()
    return command, result.returncode, output[-4000:]
