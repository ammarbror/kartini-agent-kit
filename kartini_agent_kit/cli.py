from __future__ import annotations

import argparse
import getpass
import os
import sys
from pathlib import Path

from .commit_message import conventional_message
from .config import REQUIRED_KEYS, global_config_path, load_config, missing_keys, write_config
from .git_inspection import commit_all_changes, inspect_repository, push
from .integrations import add_jira_comment, validate_connections
from .review import classify_files, has_blocking_findings, review_diff
from .ticket import extract_ticket
from .validation import run_validation


def init_command(args):
    values = load_config(Path.cwd())
    for key in REQUIRED_KEYS:
        if not values.get(key):
            if args.non_interactive:
                print(f"Missing configuration: {key}", file=sys.stderr)
                return 2
            prompt = f"{key}: "
            values[key] = getpass.getpass(prompt) if "TOKEN" in key else input(prompt)
    path = write_config(values)
    print(f"Configuration saved to {path} with owner-only permissions.")
    if args.skip_validation:
        return 0
    try:
        validate_connections(values)
    except RuntimeError as exc:
        print(f"Connection validation failed: {exc}", file=sys.stderr)
        return 1
    print("Jira and Bitbucket connections validated.")
    return 0


def _ask(prompt: str) -> bool:
    return input(f"{prompt} [y/N] ").strip().lower() in {"y", "yes"}


def ship_command(args):
    try:
        state = inspect_repository(Path.cwd())
    except RuntimeError as exc:
        print(f"Not a Git repository: {exc}", file=sys.stderr)
        return 1
    if not state.changed_files:
        print("No changes to ship.")
        return 0
    ticket = extract_ticket(state.branch)
    if not ticket:
        print("No Jira ticket found in the current branch. Expected a key such as KAIRA-654.", file=sys.stderr)
        return 1
    print(f"Branch: {state.branch}\nTicket: {ticket}")
    print("Change groups:")
    for group, files in classify_files(state.changed_files).items():
        print(f"  {group}: {', '.join(files)}")
    findings = review_diff(state.diff)
    if findings:
        print("Review findings:")
        for finding in findings:
            print(f"  [{finding.severity.upper()}] {finding.title}")
    else:
        print("Review: no critical, high, or bug findings detected by local checks.")
    if has_blocking_findings(findings):
        print("Shipping stopped because blocking findings were detected.", file=sys.stderr)
        return 1
    command, code, output = run_validation(state.root)
    if command:
        print(f"Validation: {' '.join(command)} -> {'passed' if code == 0 else 'failed'}")
        if code:
            print(output, file=sys.stderr)
            return 1
    else:
        print(f"Validation: {output}")
    summary = args.summary or input("Short change summary: ").strip()
    message = conventional_message(ticket, summary)
    print(f"\nProposed commit: {message}")
    if not args.yes and not _ask("Create this commit?"):
        print("Commit cancelled.")
        return 0
    commit_all_changes(state.root, message)
    print(f"Committed: {message}")
    should_push = args.push or (not args.no_prompt and _ask("Push this commit to the remote?"))
    if not should_push:
        return 0
    config = load_config(state.root)
    missing = missing_keys(config)
    if missing:
        print("Push cancelled: Jira/Bitbucket integration is not configured. Run `kartini init` first.", file=sys.stderr)
        return 1
    try:
        push(state.root)
    except RuntimeError as exc:
        print(f"Push failed: {exc}", file=sys.stderr)
        return 1
    print("Push succeeded.")
    comment = (f"Perubahan untuk {ticket} telah dikirim ke repository.\n\n"
               f"Perubahan ini berkaitan dengan: {summary}.\n\n"
               "Pemeriksaan kode dan validasi terkait telah berhasil dijalankan.")
    try:
        add_jira_comment(config, ticket, comment)
        print("Jira comment added.")
    except RuntimeError as exc:
        print(f"Push succeeded, but Jira comment failed: {exc}", file=sys.stderr)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="kartini", description="Kar-Tini development workflows")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="configure global Jira and Bitbucket credentials")
    init.add_argument("--non-interactive", action="store_true")
    init.add_argument("--skip-validation", action="store_true")
    init.set_defaults(func=init_command)
    ship = sub.add_parser("ship-code", help="review, validate, commit, and optionally push changes")
    ship.add_argument("--summary", help="short human-readable change summary")
    ship.add_argument("--yes", action="store_true", help="explicitly approve the commit")
    ship.add_argument("--push", action="store_true", help="explicitly approve push")
    ship.add_argument("--no-prompt", action="store_true", help="never prompt for push")
    ship.set_defaults(func=ship_command)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
