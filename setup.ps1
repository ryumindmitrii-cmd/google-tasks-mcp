$ErrorActionPreference = "Stop"

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m py_compile google_tasks_mcp.py setup_auth.py

Write-Host "Setup complete. Configure credentials.json and run setup_auth.py for OAuth."
