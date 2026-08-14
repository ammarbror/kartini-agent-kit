"""Jira and Bitbucket Cloud clients using only Python's standard library."""

from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request
from urllib.parse import quote
from pathlib import Path
import subprocess
from typing import Dict


def _request(url: str, email: str, token: str, method: str = "GET", payload=None):
    auth = base64.b64encode(f"{email}:{token}".encode()).decode()
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Basic {auth}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.status, json.loads(response.read().decode() or "{}")
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"remote request failed with HTTP {exc.code}") from None
    except urllib.error.URLError:
        raise RuntimeError("remote request could not connect") from None


def validate_connections(config: Dict[str, str]):
    jira_url = config["JIRA_URL"].rstrip("/")
    jira_status, _ = _request(f"{jira_url}/rest/api/3/myself", config["JIRA_EMAIL"], config["JIRA_API_TOKEN"])
    bitbucket_status, _ = _request("https://api.bitbucket.org/2.0/user", config["BITBUCKET_EMAIL"], config["BITBUCKET_API_TOKEN"])
    return jira_status == 200 and bitbucket_status == 200


def bitbucket_remote(root: Path) -> tuple[str, str]:
    result = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=root,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise RuntimeError("Git remote 'origin' is not configured")
    remote = result.stdout.strip()
    if remote.startswith("git@bitbucket.org:"):
        path = remote.split(":", 1)[1]
    elif remote.startswith("https://bitbucket.org/"):
        path = remote.split("bitbucket.org/", 1)[1]
    else:
        raise RuntimeError("Git remote 'origin' is not a Bitbucket Cloud URL")
    path = path.rstrip("/")
    if path.endswith(".git"):
        path = path[:-4]
    parts = path.split("/", 1)
    if len(parts) != 2 or not all(parts):
        raise RuntimeError("Bitbucket remote must contain workspace and repository")
    return parts[0], parts[1]


def validate_bitbucket_remote(config: Dict[str, str], root: Path):
    workspace, repository = bitbucket_remote(root)
    url = f"https://api.bitbucket.org/2.0/repositories/{quote(workspace)}/{quote(repository)}"
    status, _ = _request(url, config["BITBUCKET_EMAIL"], config["BITBUCKET_API_TOKEN"])
    if status != 200:
        raise RuntimeError("Bitbucket remote could not be accessed with the configured account")
    return workspace, repository


def add_jira_comment(config: Dict[str, str], ticket: str, comment: str):
    url = f"{config['JIRA_URL'].rstrip('/')}/rest/api/3/issue/{ticket}/comment"
    payload = {"body": {"type": "doc", "version": 1, "content": [{
        "type": "paragraph", "content": [{"type": "text", "text": comment}]
    }]}}
    status, _ = _request(url, config["JIRA_EMAIL"], config["JIRA_API_TOKEN"], "POST", payload)
    return status in (200, 201)
