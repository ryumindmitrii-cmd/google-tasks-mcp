# Dedicated Google Cloud Project Setup

This guide describes how to create a dedicated Google Cloud project for Google
Tasks MCP and avoid tying refresh tokens to a mixed-purpose OAuth app.

## Target Architecture

- One dedicated Google Cloud project for Google Tasks MCP.
- Only Google Tasks API enabled, plus any Google-managed prerequisite services
  required by Cloud Console.
- Google Auth Platform configured for this MCP only.
- OAuth app can be moved to `In production` after you verify the project is
  dedicated to this MCP.
- OAuth client type: `Desktop app`.

Do not publish an unrelated mixed OAuth app as a shortcut for token stability.

## Confirmation Gates

Require an explicit owner confirmation before:

- creating or deleting a Google Cloud project;
- enabling or disabling APIs;
- configuring Google Auth Platform;
- publishing the OAuth app or moving it to `In production`;
- creating OAuth clients;
- downloading, replacing, or backing up `credentials.json`;
- re-issuing read-only or write tokens;
- calling live Google Tasks API for verification;
- creating, pushing, publishing, or announcing a GitHub repository.

## gcloud Commands

Review current account:

```powershell
gcloud auth list
```

Create a dedicated project:

```powershell
gcloud projects create YOUR_PROJECT_ID --name='Google Tasks MCP Local'
```

Enable Google Tasks API:

```powershell
gcloud services enable tasks.googleapis.com --project=YOUR_PROJECT_ID
```

Verify the project:

```powershell
gcloud projects describe YOUR_PROJECT_ID --format='json(projectId,name,projectNumber,lifecycleState,createTime)'
```

Verify enabled services:

```powershell
gcloud services list --enabled --project=YOUR_PROJECT_ID --format='value(config.name)'
```

Google Cloud can auto-enable default prerequisite services during project
creation. Review the enabled list before publishing the OAuth app.

## Google Auth Platform Console Steps

Google Auth Platform and OAuth Desktop client creation should be done in the
Cloud Console UI. Do not enable IAP OAuth Admin APIs for this; those commands are
IAP-specific and are not the normal OAuth Desktop client route.

Open:

```text
https://console.cloud.google.com/auth/branding?project=YOUR_PROJECT_ID
https://console.cloud.google.com/auth/audience?project=YOUR_PROJECT_ID
https://console.cloud.google.com/auth/clients?project=YOUR_PROJECT_ID
```

Then:

1. Go to Google Auth Platform.
2. Configure Branding / OAuth consent:
   - App name: `Google Tasks MCP Local` or `Tasks MCP Local`.
   - User support email: the project owner's Google account.
   - Audience/User type: `External`.
   - Contact email: the project owner's Google account.
   - Scopes:
     - `https://www.googleapis.com/auth/tasks.readonly`
     - `https://www.googleapis.com/auth/tasks`
3. In Audience, publish the dedicated app to `In production`.
4. In Clients, create client:
   - Application type: `Desktop app`.
   - Name: `Google Tasks MCP Desktop`.
5. Open the created client and check **Client secrets**:
   - Google Auth Platform may create the Desktop client without an immediately
     downloadable secret.
   - If `Download JSON` does not include `client_secret`, use **Add secret** and
     store the new secret immediately.
   - Client secrets are only visible/downloadable at creation or rotation time.
     A lost secret cannot be recovered.
6. Save the complete OAuth client JSON locally as `credentials.json` after
   backing up any old local credential file.

## Local Migration

After the dedicated OAuth Desktop JSON is downloaded:

1. Back up old `credentials.json` by renaming it to a dated local backup.
2. Save the new downloaded JSON as `credentials.json`.
3. Re-run read-only auth:

```powershell
$env:GOOGLE_TASKS_MCP_MODE='read_only'
.\.venv\Scripts\python.exe .\setup_auth.py
```

4. Re-run write auth:

```powershell
$env:GOOGLE_TASKS_MCP_MODE='write'
$env:GOOGLE_TASKS_MCP_TOKEN_FILE=(Join-Path $PWD 'token.tasks.write.json')
.\.venv\Scripts\python.exe .\setup_auth.py
```

5. Restart Codex so MCP servers reload.
6. Verify both MCPs with `auth_status` and `list_tasklists`.

Do not print or inspect credential/token contents during migration.

## Client Secret Visibility

For new OAuth clients, Google may show only masked saved secrets such as
`****abcd`. Masked values are not usable in `credentials.json`.

Safe handling pattern:

1. Create or rotate the secret.
2. Store the full value locally immediately, without printing it to chat,
   terminal logs, screenshots, Git history, or docs.
3. Verify only metadata such as presence and length.
4. Run OAuth setup and verify `auth_status` / `list_tasklists`.

If the secret is lost before verification, create a fresh Desktop client or
rotate the secret again. Do not attempt to recover masked secret values from
logs, screenshots, or public docs.
