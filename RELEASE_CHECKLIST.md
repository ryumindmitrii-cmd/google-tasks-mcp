# Release Checklist

Use this checklist before creating a public GitHub repository or publishing an
announcement.

## Local Safety Gate

- [ ] Work from the sanitized staging directory, not the live credentials
      directory.
- [x] Confirm `credentials.json` is absent.
- [x] Confirm `token*.json` is absent.
- [x] Confirm `.env` is absent.
- [x] Confirm OAuth logs, screenshots, `.b64` files, and backups are absent.
- [x] Run a secret-pattern scan over the release tree.
- [x] Run `python -m py_compile google_tasks_mcp.py setup_auth.py`.
- [x] Review README, Google Cloud guide, and Security policy.
- [x] Verify `.gitignore` inside an initialized Git repository.

## GitHub Gate

- [x] Confirm license choice: Apache-2.0.
- [x] Confirm public repository name.
- [x] Confirm repository owner/account.
- [x] Create GitHub repository only after final owner approval.
- [x] Push only the sanitized staging tree.
- [x] Do not publish announcement text until the repository URL is verified.
- [ ] Publish external announcement or Telegram post only after explicit final
      confirmation.

## OAuth Gate

- [x] Confirm the dedicated Google Cloud project is not a mixed-purpose project.
- [x] Confirm only Google Tasks scopes are requested.
- [x] Confirm OAuth app is `In production`.
- [x] Confirm users are told to create their own Desktop OAuth client.
