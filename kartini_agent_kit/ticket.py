import re

TICKET_PATTERN = re.compile(r"(?<![A-Za-z0-9])([A-Z][A-Z0-9]+-\d+)(?![A-Za-z0-9])")


def extract_ticket(branch: str):
    match = TICKET_PATTERN.search(branch.upper())
    return match.group(1) if match else None
