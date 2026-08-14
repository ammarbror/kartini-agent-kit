import re


def conventional_message(ticket: str, summary: str) -> str:
    summary = re.sub(r"\s+", " ", summary.strip()).strip(" .")
    summary = summary[:72] or "update code"
    change_type = "fix" if re.search(r"\b(fix|bug|repair|resolve)\b", summary, re.I) else "feat"
    return f"{change_type}({ticket}): {summary.lower()}"
