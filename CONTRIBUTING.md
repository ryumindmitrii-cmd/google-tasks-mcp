# Contributing

Thanks for considering a contribution.

## Local Setup

1. Create a Python virtual environment.
2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Keep OAuth credentials and tokens outside Git.
4. Run syntax verification before submitting changes:

```powershell
python -m py_compile google_tasks_mcp.py setup_auth.py
```

## Security Boundary

Do not include:

- `credentials.json`
- `token*.json`
- `.env`
- OAuth logs
- screenshots of Google Cloud Console
- task data, task list IDs, or personal account details

Open a private security report for suspected credential handling issues. See
[SECURITY.md](SECURITY.md).

## Pull Requests

Keep changes small and explain:

- what changed;
- which MCP mode is affected;
- how you verified it;
- whether any Google OAuth scopes changed.

Scope changes must be called out explicitly.
