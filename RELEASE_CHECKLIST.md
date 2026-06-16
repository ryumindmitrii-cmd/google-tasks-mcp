# Release Checklist

Use this checklist before creating a public GitHub repository or publishing an
announcement.

## Local Safety Gate

- [ ] Work from the sanitized staging directory, not the live credentials
      directory.
- [ ] Confirm `credentials.json` is absent.
- [ ] Confirm `token*.json` is absent.
- [ ] Confirm `.env` is absent.
- [ ] Confirm OAuth logs, screenshots, `.b64` files, and backups are absent.
- [ ] Run a secret-pattern scan over the release tree.
- [ ] Run `python -m py_compile google_tasks_mcp.py setup_auth.py`.
- [ ] Review README, Google Cloud guide, and Security policy.
- [ ] Verify `.gitignore` inside an initialized Git repository.

## GitHub Gate

- [x] Confirm license choice: Apache-2.0.
- [ ] Confirm public repository name.
- [ ] Confirm repository owner/account.
- [ ] Create GitHub repository only after final owner approval.
- [ ] Push only the sanitized staging tree.
- [ ] Do not publish announcement text until the repository URL is verified.

## OAuth Gate

- [ ] Confirm the dedicated Google Cloud project is not a mixed-purpose project.
- [ ] Confirm only Google Tasks scopes are requested.
- [ ] Confirm OAuth app is `In production`.
- [ ] Confirm users are told to create their own Desktop OAuth client.
