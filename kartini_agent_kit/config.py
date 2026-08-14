"""Secure, dependency-free configuration for global and project settings."""

from __future__ import annotations

import os
import stat
from pathlib import Path
from typing import Dict, Iterable, Optional

REQUIRED_KEYS = (
    "BITBUCKET_EMAIL",
    "BITBUCKET_API_TOKEN",
    "JIRA_EMAIL",
    "JIRA_API_TOKEN",
    "JIRA_URL",
)


def global_config_path() -> Path:
    override = os.environ.get("KARTINI_CONFIG")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".config" / "kartini-agent-kit" / "config.env"


def parse_env_file(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if not path.exists():
        return values
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key] = value
    return values


def load_config(project_dir: Optional[Path] = None) -> Dict[str, str]:
    """Load environment, then global config, then project config, then env overrides."""
    values = parse_env_file(global_config_path())
    if project_dir:
        values.update(parse_env_file(project_dir / ".kartini.env"))
        values.update(parse_env_file(project_dir / ".env"))
    values.update({key: value for key, value in os.environ.items() if key in REQUIRED_KEYS})
    return values


def missing_keys(values: Dict[str, str], required: Iterable[str] = REQUIRED_KEYS):
    return [key for key in required if not values.get(key)]


def write_config(values: Dict[str, str], path: Optional[Path] = None) -> Path:
    target = path or global_config_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(f"{key}={values.get(key, '')}\n" for key in REQUIRED_KEYS)
    target.write_text(content, encoding="utf-8")
    try:
        target.chmod(stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass
    return target
