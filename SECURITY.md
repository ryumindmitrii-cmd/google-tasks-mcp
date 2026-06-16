# Security Policy

## Supported Use

This project is a local MCP server for Google Tasks. It is intended to run on a
trusted local machine through stdio.

## Secrets

Never commit, publish, paste, or log:

- `credentials.json`;
- `token*.json`;
- `.env` files;
- OAuth authorization codes;
- access tokens;
- refresh tokens;
- Google Cloud project secrets;
- private screenshots or logs.

Use `.gitignore` and keep real credentials outside public repositories.

## OAuth / Google Cloud

Use a dedicated Google Cloud project for this MCP. Enable only Google Tasks API
in that project. Do not publish an unrelated mixed-purpose OAuth app to solve
refresh-token lifetime issues.

Publishing OAuth apps, creating clients, replacing credentials, and issuing
tokens are account-affecting actions and require explicit confirmation from the
project owner.

## Reporting Issues

For public issues, do not include secrets, task contents, task list IDs, account
metadata, screenshots with private data, or full debug logs. Provide sanitized
steps to reproduce and version information instead.

## Maintainer Checklist

- Confirm `credentials.json` and `token*.json` are ignored before any commit.
- Run a secret scan over tracked files before publishing.
- Verify read-only and write modes separately.
- Keep write operations behind explicit user confirmation in the host agent.

