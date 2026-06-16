# Agent Instructions

This project is a local MCP server for Google Tasks.

- Do not read, print, copy, or commit OAuth credentials, tokens, `.env` files,
  logs, backups, or screenshots.
- Treat Google Cloud, OAuth, Google Tasks, GitHub, and publishing actions as
  external writes that require explicit owner confirmation.
- Prefer metadata and source files over private runtime artifacts during audits.
- Before claiming a release is ready, verify the sanitized staging tree, not the
  live credentials directory.
- Keep read-only and write modes separate.
- Any OAuth scope change is security-sensitive and must be called out.
