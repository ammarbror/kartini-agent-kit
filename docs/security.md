# Security guidance

## Credential handling

Use a Bitbucket API token and Jira API token with the smallest practical scope. Store them in the global local config created by `kartini init`, or provide them through the process environment for ephemeral automation.

Do not:

- commit `.env` or `config.env` files;
- include tokens in branch names, commit messages, Jira comments, or logs;
- share tokens in chat or issue trackers;
- use a token after it has been exposed.

If a token is exposed, revoke it immediately at the provider and generate a replacement.

## Push approval

`ship-code` intentionally requires a separate push approval after the commit approval. Automation using `--yes` or `--push` should run only in a trusted, isolated environment and should inspect the proposed file list first.

## Review limitations

The CLI includes deterministic heuristics for common credential and unsafe-code patterns. The Codex skill adds semantic review. Neither replaces project-specific security testing, dependency scanning, or human review for high-impact changes.
