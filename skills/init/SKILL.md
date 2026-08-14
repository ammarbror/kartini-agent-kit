---
name: init
description: Configure global Jira and Bitbucket Cloud credentials for Kar-Tini workflows. Use when the user invokes /init or asks to initialize kartini-agent-kit.
---

# Kar-Tini Init

Run `kartini init` from any project. Store credentials only in the global local configuration; never write them to a repository or include them in output. Validate both Jira and Bitbucket connections and report only success/failure, never tokens or raw authorization errors.

Expected variables are documented in the repository `.env.example`:

```env
BITBUCKET_EMAIL=your-email@example.com
BITBUCKET_API_TOKEN=your-bitbucket-api-token
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-jira-api-token
JIRA_URL=https://your-domain.atlassian.net
```
