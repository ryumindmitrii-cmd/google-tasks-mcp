#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m py_compile google_tasks_mcp.py setup_auth.py

echo "Setup complete. Configure credentials.json and run setup_auth.py for OAuth."
