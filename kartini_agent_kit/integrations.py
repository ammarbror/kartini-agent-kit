"""Jira and Bitbucket Cloud clients using only Python's standard library."""

from __future__ import annotations

import base64
import json
import urllib.error
import urllib.request
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


def add_jira_comment(config: Dict[str, str], ticket: str, comment: str):
    url = f"{config['JIRA_URL'].rstrip('/')}/rest/api/3/issue/{ticket}/comment"
    payload = {"body": {"type": "doc", "version": 1, "content": [{
        "type": "paragraph", "content": [{"type": "text", "text": comment}]
    }]}}
    status, _ = _request(url, config["JIRA_EMAIL"], config["JIRA_API_TOKEN"], "POST", payload)
    return status in (200, 201)
