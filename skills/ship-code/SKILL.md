---
name: ship-code
description: Review and safely ship code changes using the Kar-Tini workflow. Use when the user invokes /ship-code or asks to review, commit, and optionally push current changes.
---

# Kar-Tini Ship Code

Use `kartini ship-code` for deterministic Git inspection and validation, then perform the semantic review below before allowing a commit.

1. Inspect branch, staged/unstaged status, and the complete diff.
2. Group changes by purpose and identify affected behavior.
3. Review only actionable `critical`, `high`, and bug/regression findings. Do not report medium/low noise.
4. Run relevant tests, lint, typecheck, and build checks. Treat failures as blockers.
5. Extract a Jira key such as `KAIRA-654` from the branch. Stop if absent.
6. Explain the findings and validation result, then propose a Conventional Commit such as `feat(KAIRA-654): add payment validation`.
7. Ask for explicit confirmation before creating the commit.
8. Never push automatically. Ask separately for explicit push approval.
9. Only after a successful push, add a concise Jira comment in non-technical language describing the user-facing purpose and validation result.

Never expose credentials. Do not claim a push or Jira comment succeeded without fresh command/API evidence.
