# Google Tasks MCP for Codex

Local MCP server that lets Codex read and manage Google Tasks through the
official Google Tasks API.

The server has two modes:

- `read_only` exposes only `auth_status`, `list_tasklists`, `list_tasks`, and
  `get_task`.
- `write` also exposes `ensure_tasklist`, `create_task`, `update_task`,
  `complete_task`, and `reopen_task`.

## Important API Limitation

The public Google Tasks API stores only a task due date. It does not preserve a
due time through the API. If a task must happen at a specific time, put the time
in the title/notes or create a separate Google Calendar event.

## Quick Start

1. Clone or copy this project to a local private directory.
2. Create and activate a Python virtual environment.
3. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

4. Create a dedicated Google Cloud project for this MCP.
5. Enable only Google Tasks API.
6. Configure Google Auth Platform for this dedicated project.
7. Create an OAuth client of type `Desktop app`.
8. Add/download the OAuth client secret immediately and save the OAuth client
   JSON as `credentials.json` into the local MCP config directory. Do not commit
   it.
9. Run OAuth setup for read-only and write modes.
10. Add the MCP server entries to Codex config and restart Codex.

See [GOOGLE_CLOUD_SETUP.md](GOOGLE_CLOUD_SETUP.md) for the detailed Google Cloud
and OAuth flow.

## Files

- `google_tasks_mcp.py` - MCP server.
- `setup_auth.py` - first-time OAuth authorization helper.
- `requirements.txt` - Python dependencies.
- `config.example.env` - public example environment variables.
- `examples/codex_config.example.toml` - Codex MCP config example.
- `GOOGLE_CLOUD_SETUP.md` - dedicated Google Cloud project setup.
- `SECURITY.md` - supported security policy.

Private local files that must never be committed:

- `credentials.json`
- `token.readonly.json`
- `token.tasks.write.json`
- `.env`
- OAuth logs, screenshots, backups, and virtual environments

## Recommended Google Cloud Separation

Use a dedicated Google Cloud project for this MCP. Do not reuse a mixed product
or research project just to stabilize refresh tokens.

The dedicated project should contain only:

- Google Tasks API;
- Google Auth Platform / OAuth consent for this local MCP;
- one OAuth client of type `Desktop app`.

If refresh tokens are expiring weekly because an OAuth app is left in Testing
mode, publish only the dedicated Google Tasks MCP OAuth app after you have
verified the project isolation. Do not publish an unrelated mixed OAuth app as a
shortcut.

## OAuth Setup

Google Auth Platform now shows/downloads OAuth client secrets only at creation
or rotation time. If the downloaded JSON does not contain `client_secret`, open
the OAuth client, use **Client secrets -> Add secret**, and immediately store the
new secret in your local `credentials.json`. A lost secret cannot be recovered;
create a new secret or a new Desktop client instead.

Run read-only authorization:

```powershell
$env:GOOGLE_TASKS_MCP_MODE='read_only'
python .\setup_auth.py
```

Run write authorization:

```powershell
$env:GOOGLE_TASKS_MCP_MODE='write'
$env:GOOGLE_TASKS_MCP_TOKEN_FILE=(Join-Path $PWD 'token.tasks.write.json')
python .\setup_auth.py
```

Complete Google authorization in the browser for each mode. Keep the generated
token files private.

For remote-debug/browser-controlled setups, prevent `setup_auth.py` from opening
the default browser and copy the printed URL into the browser you control:

```powershell
$env:GOOGLE_TASKS_MCP_OPEN_BROWSER='0'
python .\setup_auth.py
```

## Codex Config

Codex config is usually stored at:

```text
%USERPROFILE%\.codex\config.toml
```

Use absolute paths in the MCP entries. On Windows accounts with non-ASCII user
folders, Windows 8.3 short paths can avoid stdio/env encoding issues.

See [examples/codex_config.example.toml](examples/codex_config.example.toml).

After changing MCP config, restart Codex so the server is loaded as a native
tool provider.

## Token Lifetime and invalid_grant Recovery

Google OAuth access tokens are short-lived. Offline access stores a refresh
token that can request new access tokens without browser login.

Refresh tokens can still be invalidated by Google or the user. Common causes:
revoked app access, OAuth consent screen left in Testing mode, password/security
changes, unused tokens, too many refresh tokens for the same user/client, or a
scope/client change.

If `auth_status` reports `invalid_grant`:

1. Rename the broken token file to a dated local backup. Do not print or inspect
   token contents.
2. Re-run the matching OAuth setup command.
3. Verify both `auth_status` and `list_tasklists` for the affected mode.

If tokens are expiring weekly and the OAuth app is in Testing mode, create a
dedicated Google Cloud project for this MCP, publish only that dedicated OAuth
app, then re-run both read-only and write OAuth setup commands so the new
refresh tokens are tied to the dedicated project.

If OAuth setup fails with `client_secret is missing` or `invalid_client`, check
only credential metadata: the local `credentials.json` must contain an
`installed.client_secret` value for Google Desktop OAuth. Do not print the
secret. If it is missing or invalid, rotate/create a new secret in Google Auth
Platform and store it locally immediately.

## Tools

Read-only mode:

- `auth_status`
- `list_tasklists`
- `list_tasks`
- `get_task`

Write mode additionally exposes:

- `ensure_tasklist`
- `create_task`
- `update_task`
- `complete_task`
- `reopen_task`

## Open-Source Release Safety

Before publishing or pushing anywhere:

- keep `credentials.json`, `token*.json`, `.env`, logs, screenshots, backups,
  and virtual environments out of Git;
- run a targeted secret scan over the release tree;
- verify `.gitignore` in a real Git repository;
- do not include private project IDs, private paths, task data, OAuth logs, or
  screenshots in public docs;
- do not create a public GitHub repository, push, publish, or announce without a
  final explicit release confirmation.
