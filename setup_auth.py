from __future__ import annotations

import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


TASKS_SCOPE = "https://www.googleapis.com/auth/tasks"
TASKS_READONLY_SCOPE = "https://www.googleapis.com/auth/tasks.readonly"
MODE = os.environ.get("GOOGLE_TASKS_MCP_MODE", "read_only").strip().lower().replace("-", "_")
if MODE in {"readonly", "read_only", "ro"}:
    MODE = "read_only"
elif MODE in {"write", "read_write", "rw"}:
    MODE = "write"
else:
    raise RuntimeError("GOOGLE_TASKS_MCP_MODE must be read_only or write")

READ_ONLY = MODE == "read_only"
SCOPES = [TASKS_READONLY_SCOPE if READ_ONLY else TASKS_SCOPE]
CONFIG_DIR = Path(os.environ.get("GOOGLE_TASKS_MCP_CONFIG_DIR", Path.home() / ".egzita" / "google-tasks-mcp"))
DEFAULT_TOKEN_FILE = CONFIG_DIR / ("token.readonly.json" if READ_ONLY else "token.tasks.write.json")
CREDENTIALS_FILE = Path(
    os.environ.get("GOOGLE_TASKS_MCP_CREDENTIALS_FILE", CONFIG_DIR / "credentials.json")
)
TOKEN_FILE = Path(os.environ.get("GOOGLE_TASKS_MCP_TOKEN_FILE", DEFAULT_TOKEN_FILE))
OPEN_BROWSER = os.environ.get("GOOGLE_TASKS_MCP_OPEN_BROWSER", "1").strip().lower() not in {
    "0",
    "false",
    "no",
    "off",
}


def _oauth_client_config() -> dict:
    config = json.loads(CREDENTIALS_FILE.read_text(encoding="utf-8"))
    for client_type in ("installed", "web"):
        client = config.get(client_type)
        if isinstance(client, dict):
            client.setdefault("client_secret", None)
    return config


def main() -> int:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not CREDENTIALS_FILE.exists():
        print(f"Missing OAuth Desktop credentials: {CREDENTIALS_FILE}")
        print()
        print("Create an OAuth Desktop client in Google Cloud, enable Google Tasks API,")
        print("download the JSON, and save it exactly as credentials.json in this folder.")
        return 2

    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_config(_oauth_client_config(), SCOPES)
        creds = flow.run_local_server(port=0, open_browser=OPEN_BROWSER)

    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    service = build("tasks", "v1", credentials=creds, cache_discovery=False)
    response = service.tasklists().list(maxResults=10).execute()
    tasklists = response.get("items", [])

    print("Google Tasks authorization OK.")
    print(f"Mode: {MODE}")
    print(f"Scopes: {', '.join(SCOPES)}")
    print(f"Token saved to: {TOKEN_FILE}")
    print("Task lists:")
    for item in tasklists:
        print(f"- {item.get('title')} ({item.get('id')})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
