# kartini-agent-kit

Global Kar-Tini workflows for Codex and the terminal. The first workflows are:

- `/init` or `kartini init` — configure and validate global Jira/Bitbucket Cloud access.
- `/ship-code` or `kartini ship-code` — inspect, review, validate, commit, and optionally push changes.

## Install the CLI

Install this repository into a virtual environment or with `pipx`:

```bash
python3 -m pip install .
# or: pipx install .
```

Then configure the global integration:

```bash
kartini init
```

The credentials are written to `~/.config/kartini-agent-kit/config.env` with owner-only permissions. Project-local `.kartini.env` and `.env` values override global values, but secrets should not be committed.

## Configure Codex

Install or link this repository as a Codex plugin. The plugin exposes the `init` and `ship-code` skills from `skills/`; they call the same `kartini` CLI for deterministic Git and integration operations.

## Example environment

See [.env.example](.env.example). Never replace its placeholders with real credentials or commit a secret-bearing `.env` file.

## Safe defaults

`ship-code` requires a Jira key in the branch, blocks on critical/high/bug findings and failed validation, asks before creating a commit, and asks separately before pushing. A Jira comment is created only after a successful push.
