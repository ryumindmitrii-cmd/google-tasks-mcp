from __future__ import annotations

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from mcp.server.fastmcp import FastMCP


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
DEFAULT_CONFIG_DIR = Path.home() / ".egzita" / "google-tasks-mcp"
CONFIG_DIR = Path(os.environ.get("GOOGLE_TASKS_MCP_CONFIG_DIR", DEFAULT_CONFIG_DIR))
DEFAULT_TOKEN_FILE = CONFIG_DIR / ("token.readonly.json" if READ_ONLY else "token.tasks.write.json")
CREDENTIALS_FILE = Path(
    os.environ.get("GOOGLE_TASKS_MCP_CREDENTIALS_FILE", CONFIG_DIR / "credentials.json")
)
TOKEN_FILE = Path(os.environ.get("GOOGLE_TASKS_MCP_TOKEN_FILE", DEFAULT_TOKEN_FILE))

mcp = FastMCP(
    "Google Tasks Read Only" if READ_ONLY else "Google Tasks Write",
    instructions=(
        (
            "Read the user's Google Tasks through the public Google Tasks API. "
            if READ_ONLY
            else "Manage the user's Google Tasks through the public Google Tasks API. "
        )
        + "Due dates are date-only because the public API discards due times."
    ),
)


class AuthRequiredError(RuntimeError):
    pass


def _oauth_client_config() -> dict[str, Any]:
    config = json.loads(CREDENTIALS_FILE.read_text(encoding="utf-8"))
    for client_type in ("installed", "web"):
        client = config.get(client_type)
        if isinstance(client, dict):
            client.setdefault("client_secret", None)
    return config


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    return value


def _error_payload(error: Exception) -> dict[str, Any]:
    if isinstance(error, HttpError):
        try:
            content = json.loads(error.content.decode("utf-8"))
        except Exception:
            content = error.content.decode("utf-8", errors="replace")
        return {
            "ok": False,
            "error": "google_http_error",
            "status": error.resp.status,
            "details": content,
        }
    return {"ok": False, "error": type(error).__name__, "message": str(error)}


def _load_credentials(interactive: bool = False) -> Credentials:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    creds: Credentials | None = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    if creds and creds.valid:
        return creds

    if not interactive:
        raise AuthRequiredError(
            "Google Tasks OAuth is not authorized yet. Put OAuth Desktop credentials "
            f"at {CREDENTIALS_FILE} and run setup_auth.py once."
        )

    if not CREDENTIALS_FILE.exists():
        raise AuthRequiredError(
            f"Missing OAuth Desktop credentials file: {CREDENTIALS_FILE}"
        )

    flow = InstalledAppFlow.from_client_config(_oauth_client_config(), SCOPES)
    creds = flow.run_local_server(port=0)
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds


def _service():
    creds = _load_credentials(interactive=False)
    return build("tasks", "v1", credentials=creds, cache_discovery=False)


def _normalize_due_date(due_date: str | None) -> str | None:
    if not due_date:
        return None

    value = due_date.strip()
    if not value:
        return None

    # Google Tasks stores date-only due values. Supplying midnight UTC keeps the
    # intended calendar date stable across clients that expect RFC 3339.
    try:
        parsed = date.fromisoformat(value)
        return f"{parsed.isoformat()}T00:00:00.000Z"
    except ValueError:
        pass

    try:
        parsed_dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return f"{parsed_dt.date().isoformat()}T00:00:00.000Z"
    except ValueError as exc:
        raise ValueError(
            "due_date must be YYYY-MM-DD or an RFC3339 datetime. "
            "Google Tasks will keep only the date part."
        ) from exc


def _simplify_task(task: dict[str, Any]) -> dict[str, Any]:
    return _json_safe(
        {
            "id": task.get("id"),
            "title": task.get("title"),
            "notes": task.get("notes"),
            "status": task.get("status"),
            "due": task.get("due"),
            "completed": task.get("completed"),
            "updated": task.get("updated"),
            "parent": task.get("parent"),
            "position": task.get("position"),
            "links": task.get("links"),
            "webViewLink": task.get("webViewLink"),
        }
    )


def _simplify_tasklist(tasklist: dict[str, Any]) -> dict[str, Any]:
    return _json_safe(
        {
            "id": tasklist.get("id"),
            "title": tasklist.get("title"),
            "updated": tasklist.get("updated"),
            "selfLink": tasklist.get("selfLink"),
        }
    )


@mcp.tool()
def auth_status() -> dict[str, Any]:
    """Return Google Tasks OAuth configuration and token status."""
    status: dict[str, Any] = {
        "config_dir": str(CONFIG_DIR),
        "credentials_file": str(CREDENTIALS_FILE),
        "credentials_file_exists": CREDENTIALS_FILE.exists(),
        "token_file": str(TOKEN_FILE),
        "token_file_exists": TOKEN_FILE.exists(),
        "mode": MODE,
        "read_only": READ_ONLY,
        "scopes": SCOPES,
    }

    try:
        creds = _load_credentials(interactive=False)
        status.update(
            {
                "ok": True,
                "authorized": True,
                "expired": bool(creds.expired),
                "valid": bool(creds.valid),
            }
        )
    except Exception as exc:
        status.update({"ok": False, "authorized": False, "message": str(exc)})

    return status


@mcp.tool()
def list_tasklists(max_results: int = 100) -> dict[str, Any]:
    """List Google Tasks task lists."""
    try:
        service = _service()
        items: list[dict[str, Any]] = []
        page_token: str | None = None
        remaining = max(1, min(max_results, 500))

        while remaining > 0:
            response = (
                service.tasklists()
                .list(maxResults=min(100, remaining), pageToken=page_token)
                .execute()
            )
            batch = response.get("items", [])
            items.extend(_simplify_tasklist(item) for item in batch)
            remaining -= len(batch)
            page_token = response.get("nextPageToken")
            if not page_token or not batch:
                break

        return {"ok": True, "tasklists": items}
    except Exception as exc:
        return _error_payload(exc)


def ensure_tasklist(title: str) -> dict[str, Any]:
    """Find a task list by exact title, or create it if it does not exist."""
    try:
        wanted = title.strip()
        if not wanted:
            raise ValueError("title is required")

        service = _service()
        existing = list_tasklists(max_results=500)
        if not existing.get("ok"):
            return existing

        for item in existing.get("tasklists", []):
            if item.get("title", "").casefold() == wanted.casefold():
                return {"ok": True, "created": False, "tasklist": item}

        created = service.tasklists().insert(body={"title": wanted}).execute()
        return {"ok": True, "created": True, "tasklist": _simplify_tasklist(created)}
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
def list_tasks(
    tasklist_id: str = "@default",
    show_completed: bool = False,
    show_hidden: bool = False,
    max_results: int = 100,
) -> dict[str, Any]:
    """List tasks from a Google Tasks list."""
    try:
        service = _service()
        items: list[dict[str, Any]] = []
        page_token: str | None = None
        remaining = max(1, min(max_results, 500))

        while remaining > 0:
            response = (
                service.tasks()
                .list(
                    tasklist=tasklist_id,
                    showCompleted=show_completed,
                    showHidden=show_hidden,
                    maxResults=min(100, remaining),
                    pageToken=page_token,
                )
                .execute()
            )
            batch = response.get("items", [])
            items.extend(_simplify_task(item) for item in batch)
            remaining -= len(batch)
            page_token = response.get("nextPageToken")
            if not page_token or not batch:
                break

        return {"ok": True, "tasklist_id": tasklist_id, "tasks": items}
    except Exception as exc:
        return _error_payload(exc)


@mcp.tool()
def get_task(task_id: str, tasklist_id: str = "@default") -> dict[str, Any]:
    """Get a single Google Task by ID."""
    try:
        service = _service()
        task = service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
        return {"ok": True, "task": _simplify_task(task)}
    except Exception as exc:
        return _error_payload(exc)


def create_task(
    title: str,
    tasklist_id: str = "@default",
    notes: str | None = None,
    due_date: str | None = None,
    parent: str | None = None,
    previous: str | None = None,
) -> dict[str, Any]:
    """Create a Google Task. due_date accepts YYYY-MM-DD; due time is not supported by the public API."""
    try:
        clean_title = title.strip()
        if not clean_title:
            raise ValueError("title is required")

        body: dict[str, Any] = {"title": clean_title}
        if notes:
            body["notes"] = notes
        normalized_due = _normalize_due_date(due_date)
        if normalized_due:
            body["due"] = normalized_due

        service = _service()
        request = service.tasks().insert(
            tasklist=tasklist_id,
            body=body,
            parent=parent,
            previous=previous,
        )
        created = request.execute()
        return {"ok": True, "task": _simplify_task(created)}
    except Exception as exc:
        return _error_payload(exc)


def update_task(
    task_id: str,
    tasklist_id: str = "@default",
    title: str | None = None,
    notes: str | None = None,
    due_date: str | None = None,
    clear_due: bool = False,
) -> dict[str, Any]:
    """Patch title, notes, or due date for a Google Task."""
    try:
        body: dict[str, Any] = {}
        if title is not None:
            clean_title = title.strip()
            if not clean_title:
                raise ValueError("title cannot be empty")
            body["title"] = clean_title
        if notes is not None:
            body["notes"] = notes
        if clear_due:
            body["due"] = None
        elif due_date is not None:
            body["due"] = _normalize_due_date(due_date)
        if not body:
            raise ValueError("no fields to update")

        service = _service()
        updated = service.tasks().patch(
            tasklist=tasklist_id,
            task=task_id,
            body=body,
        ).execute()
        return {"ok": True, "task": _simplify_task(updated)}
    except Exception as exc:
        return _error_payload(exc)


def complete_task(task_id: str, tasklist_id: str = "@default") -> dict[str, Any]:
    """Mark a Google Task as completed."""
    try:
        service = _service()
        updated = service.tasks().patch(
            tasklist=tasklist_id,
            task=task_id,
            body={"status": "completed"},
        ).execute()
        return {"ok": True, "task": _simplify_task(updated)}
    except Exception as exc:
        return _error_payload(exc)


def reopen_task(task_id: str, tasklist_id: str = "@default") -> dict[str, Any]:
    """Mark a completed Google Task as needing action again."""
    try:
        service = _service()
        updated = service.tasks().patch(
            tasklist=tasklist_id,
            task=task_id,
            body={"status": "needsAction", "completed": None},
        ).execute()
        return {"ok": True, "task": _simplify_task(updated)}
    except Exception as exc:
        return _error_payload(exc)


if not READ_ONLY:
    ensure_tasklist = mcp.tool()(ensure_tasklist)
    create_task = mcp.tool()(create_task)
    update_task = mcp.tool()(update_task)
    complete_task = mcp.tool()(complete_task)
    reopen_task = mcp.tool()(reopen_task)


if __name__ == "__main__":
    mcp.run()
