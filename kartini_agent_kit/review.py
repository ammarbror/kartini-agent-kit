"""Conservative local heuristics; semantic review remains available to the Codex skill."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List


@dataclass
class Finding:
    severity: str
    title: str
    detail: str


BLOCKING = {"critical", "high", "bug"}


def review_diff(diff: str) -> List[Finding]:
    findings: List[Finding] = []
    added = [line[1:] for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++")]
    text = "\n".join(added)
    rules = [
        (r"AKIA[0-9A-Z]{16}", "critical", "Possible AWS access key exposed in a change."),
        (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", "critical", "Private key material appears in a change."),
        (r"(?:api[_-]?key|secret|token|password)\s*[:=]\s*[\"'][^\"']{8,}", "high", "Possible hard-coded credential appears in a change."),
        (r"\beval\s*\(", "high", "Dynamic eval usage can execute untrusted input."),
        (r"(?:TODO|FIXME)\s*[:!]", "bug", "Unresolved TODO/FIXME appears in the changed code."),
    ]
    for pattern, severity, detail in rules:
        if re.search(pattern, text, re.IGNORECASE):
            findings.append(Finding(severity, detail, detail))
    return findings


def has_blocking_findings(findings: List[Finding]) -> bool:
    return any(f.severity in BLOCKING for f in findings)


def classify_files(files: List[str]):
    groups = {"application": [], "tests": [], "configuration": [], "documentation": [], "other": []}
    for path in files:
        lower = path.lower()
        if any(part in lower for part in ("test", "spec")):
            group = "tests"
        elif lower.endswith((".md", ".rst", ".txt")):
            group = "documentation"
        elif lower.endswith((".json", ".yaml", ".yml", ".toml", ".ini", ".env.example")):
            group = "configuration"
        elif lower.endswith((".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb", ".php")):
            group = "application"
        else:
            group = "other"
        groups[group].append(path)
    return {key: value for key, value in groups.items() if value}
