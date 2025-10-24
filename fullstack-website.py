"""
Bootstrap this project structure and files, then delete this script.

Assumptions:
- Run from the repository root; this script creates/overwrites files in-place.
"""

from __future__ import annotations

import os
from typing import Dict


def ensure_parent_directory(file_path: str) -> None:
    parent_dir = os.path.dirname(file_path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)


def write_file(path: str, content: str) -> None:
    ensure_parent_directory(path)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def main() -> None:
    files: Dict[str, str] = {
        # Backend
        "backend/app/__init__.py": """import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv


def create_app() -> Flask:
    """Application factory creating the Flask app with minimal setup."""
    load_dotenv()

    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False

    # Restrict CORS in production; allow all in local dev
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "*")
    CORS(app, resources={r"/*": {"origins": frontend_origin}})

    # Register API blueprint
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.get("/")
    def root():
        return jsonify({"status": "ok"})

    return app
""",
        "backend/app/routes.py": """from flask import Blueprint, jsonify
from .db import ping_database
import logging

api_bp = Blueprint("api", __name__)

# Configure a logger for error reporting
logger = logging.getLogger(__name__)

@api_bp.get("/health")
def api_health():
    """Lightweight health endpoint for API layer monitoring."""
    return jsonify({"status": "ok", "service": "api"})

@api_bp.get("/db/ping")
def db_ping():
    """Verifies DB connectivity/credentials with a trivial SELECT."""
    ok, error = ping_database()
    if not ok and error:
        # Log the detailed error internally, avoid exposing sensitive info to client
        logger.error("DB ping failed: %s", error)
    return jsonify({
        "status": "ok" if ok else "error",
        "error": None if ok else "Database connection failed",
    })

# Example insert route (commented):
# from flask import request
# from .db import insert_name
#
# @api_bp.post("/names")
# def create_name():
#     """Minimal insert endpoint; expects JSON body { "name": "...", "email": "..." }."""
#     data = request.get_json(silent=True) or {}
#     name = (data.get("name") or "").strip()
#     email = (data.get("email") or "").strip()
#     if not name or not email:
#         return jsonify({"status": "error", "error": "name and email are required"}), 400
#
#     ok, error = insert_name(name)
#     if not ok:
#         return jsonify({"status": "error", "error": error}), 500
#     return jsonify({"status": "ok"})
""",
        "backend/app/db.py": """import os
from typing import Tuple, Optional


import mysql.connector
from mysql.connector import Error


def _get_db_config() -> dict:
    """Load DB configuration from environment variables.

    Using env vars (with python-dotenv during local dev) keeps secrets out of
    source control and allows configuration per environment.
    """
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "mysql"),
    }


def get_connection() -> mysql.connector.connection.MySQLConnection:
    """Create and return a new MySQL connection using the above config."""
    cfg = _get_db_config()
    return mysql.connector.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        connection_timeout=3,
    )


def ping_database() -> Tuple[bool, Optional[str]]:
    """Execute a trivial query to confirm connectivity and credentials.

    Returns (ok, error_message_if_any).
    """
    try:
        conn = get_connection()
    except Error as exc:
        return False, str(exc)
    except Exception as exc:
        return False, str(exc)

    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.fetchone()
        cur.close()
        return True, None
    except Error as exc:
        return False, str(exc)
    except Exception as exc:
        return False, str(exc)
    finally:
        try:
            conn.close()
        except Exception:
            pass

# Example helpers (commented):
# def ensure_table_exists() -> None:
#     """Create the `names` table if it does not already exist.
#     Example includes an email column to store a second field.
#     """
#     conn = get_connection()
#     try:
#         cur = conn.cursor()
#         cur.execute(
#             """
#             CREATE TABLE IF NOT EXISTS names (
#                 id INT PRIMARY KEY AUTO_INCREMENT,
#                 name VARCHAR(255) NOT NULL,
#                 email VARCHAR(255) NOT NULL,
#                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#             )
#             """
#         )
#         conn.commit()
#         cur.close()
#     finally:
#         conn.close()
#
# def insert_name(name: str, email: str) -> Tuple[bool, Optional[str]]:
#     """Insert a single row into `names` after ensuring the table exists.
#     This example writes both name and email.
#     """
#     try:
#         ensure_table_exists()
#         conn = get_connection()
#         cur = conn.cursor()
#         cur.execute("INSERT INTO names (name, email) VALUES (%s, %s)", (name, email))
#         conn.commit()
#         cur.close()
#         conn.close()
#         return True, None
#     except Error as exc:
#         return False, str(exc)
#     except Exception as exc:
#         return False, str(exc)



""",
        "backend/run.py": """import os

from app import create_app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)


""",
        "backend/requirements.txt": """Flask==3.0.3
Flask-Cors==4.0.0
python-dotenv==1.0.1
mysql-connector-python==9.0.0
waitress==3.0.2
""",
        # Frontend (Vite + React)
        "frontend/index.html": """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>CS-364-Project</title>
  <link rel=\"stylesheet\" href=\"assets/css/style.css\">
  
</head>
<body>
    <div class=\"container\">
      <h1>CS-364-Project</h1>
      <div id=\"root\"></div>
      <!--
        Example form (commented):
        <form id=\"example-form\">
          <label for=\"example-name\">Name</label>
          <input id=\"example-name\" name=\"name\" type=\"text\" placeholder=\"Your name\" required>

          <label for=\"example-email\">Email</label>
          <input id=\"example-email\" name=\"email\" type=\"email\" placeholder=\"you@example.com\" required>

          <button type=\"submit\">Submit</button>
        </form>
        <div id=\"example-result\" aria-live=\"polite\"></div>

        This pairs with the commented JS in assets/js/script.js
        and the example backend route in backend/app/routes.py.
      -->
      
    
    <script type=\"module\" src=\"/src/main.jsx\"></script>


    
  
</body>
</html>

""",
        "frontend/src/App.jsx": """import { useEffect, useState } from 'react';

export default function App() {
  const [apiStatus, setApiStatus] = useState('checking...');
  const [dbStatus, setDbStatus] = useState('checking...');

  useEffect(() => {
    fetch('/api/health')
      .then((r) => r.json())
      .then((d) => setApiStatus(d.status || 'unknown'))
      .catch(() => setApiStatus('unreachable'));

    fetch('/api/db/ping')
      .then((r) => r.json())
      .then((d) => setDbStatus(d.status || 'unknown'))
      .catch(() => setDbStatus('unreachable'));
  }, []);

  return (
    <div>
      <h2>Backend Status</h2>
      <ul>
        <li>API: {apiStatus}</li>
        <li>Database: {dbStatus}</li>
      </ul>
    </div>
  );
}

""",
        "frontend/src/main.jsx": """import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';

const container = document.getElementById('root');
const root = createRoot(container);
root.render(<App />);


""",
        "frontend/vite.config.js": """import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    },
  },
});


""",
        "frontend/package.json": """{
  \"name\": \"cs-364-frontend\",
  \"private\": true,
  \"version\": \"0.0.1\",
  \"type\": \"module\",
  \"scripts\": {
    \"dev\": \"vite\",
    \"build\": \"vite build\",
    \"preview\": \"vite preview --port 5173\"
  },
  \"dependencies\": {
    \"react\": \"^18.3.1\",
    \"react-dom\": \"^18.3.1\"
  },
  \"devDependencies\": {
    \"@vitejs/plugin-react\": \"^4.3.1\",
    \"vite\": \"^5.4.8\"
  }
}


""",
        "frontend/assets/css/style.css": """/* Minimal, device-friendly base styles */

/* Box sizing reset */
*,
*::before,
*::after {
  box-sizing: border-box;
}

/* Basic sensible defaults */
html {
  font-family: system-ui, -apple-system, \"Segoe UI\", Roboto, \"Helvetica Neue\", Arial;
  font-size: 16px; /* base size; scales with browser settings */
  -webkit-text-size-adjust: 100%;
  line-height: 1.45;
}

body {
  margin: 0;
  padding: 1rem;
  background-color: #ffffff;
  color: #111;
  min-height: 100vh;
  display: block;
}

/* Make images responsive if later added */
img,
picture,
video {
  max-width: 100%;
  height: auto;
  display: block;
}

/* Utility container that stays readable on any device */
.container {
  max-width: 90ch;
  margin-left: auto;
  margin-right: auto;
  padding-left: 1rem;
  padding-right: 1rem;
}


""",
        # Repo files
        ".gitignore": """# Python virtual environment
.venv/
venv/

# Byte-compiled / cache files
__pycache__/
*.py[cod]

# Environment variables
*.env
""",
        # Project TODO (updated)
        "TODO.md": """## Project TODO

Environment
- [ ] Create `backend/.env` with:
  - FLASK_RUN_HOST=`0.0.0.0`
  - FLASK_RUN_PORT=`5000`
  - FLASK_DEBUG=`0`
  - FLASK_ENV=`production`
  - DB_HOST=`<your-db-host>`
  - DB_PORT=`3306`
  - DB_USER=`<your-db-user>`
  - DB_PASSWORD=`<your-db-password>`
  - DB_NAME=`<your-database>`
  - FRONTEND_ORIGIN=`<your-frontend-url>`  # e.g., `http://127.0.0.1:5500` if using Live Server, or `*` for quick local tests

- Install & Run (backend)
  - [ ] `cd backend`
  - [ ] Create venv: `python -m venv .venv`
  - [ ] Activate venv: `.venv\\Scripts\\activate` (Windows)
  - [ ] `pip install -r requirements.txt`
  - [ ] `waitress-serve --listen=0.0.0.0:5000 run:app`

- Verify API
  - [ ] Root health: open `http://127.0.0.1:5000/` → expect `{ "status": "ok" }`
  - [ ] API Health: open `http://127.0.0.1:5000/api/health` → expect `{ "status": "ok" }`
  - [ ] DB Ping: open `http://127.0.0.1:5000/api/db/ping`
    - Expect `{ "status": "ok" }` if credentials are valid
    - Otherwise `{ "status": "error", "error": "..." }`

- Frontend
  - [ ] `cd frontend`
  - [ ] Install Node deps: `npm install`
  - [ ] Start dev server: `npm run dev` (serves on `http://127.0.0.1:5173`)
  - [ ] Confirm the page shows API and Database status

- MySQL Checklist
  - [ ] Ensure MySQL server is running and accessible
  - [ ] Confirm user/password and DB exist
  - [ ] If needed, update `.env` with correct credentials

Notes
- Vite dev server proxies `/api/*` to Flask at `http://127.0.0.1:5000` per `frontend/vite.config.js`. Keep Flask running while using `npm run dev`.


""",
        # README (updated)
        "README.md": """# Fullstack Website (Flask + MySQL + React via Vite)

This project is a minimal full‑stack setup:
- Backend: Python Flask API with MySQL Connector
- Frontend: React (Vite dev server + proxy to Flask)

## Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL server

## Backend (Flask)
1) Create and populate `backend/.env`:
```
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
FLASK_DEBUG=0
FLASK_ENV=production
DB_HOST=<your-db-host>
DB_PORT=3306
DB_USER=<your-db-user>
DB_PASSWORD=<your-db-password>
DB_NAME=<your-database>
# For production, set a specific origin. During local dev Vite uses http://127.0.0.1:5173
FRONTEND_ORIGIN=http://127.0.0.1:5173
```

2) Install deps and run:
```
cd backend
python -m venv .venv
.venv\\Scripts\\activate   # Windows
pip install -r requirements.txt
python run.py
# or: waitress-serve --listen=0.0.0.0:5000 run:app
```

3) Verify endpoints:
- `GET http://127.0.0.1:5000/` → `{ "status": "ok" }`
- `GET http://127.0.0.1:5000/api/health` → `{ "status": "ok" }`
- `GET http://127.0.0.1:5000/api/db/ping` → `{ "status": "ok" }` if DB creds are valid

## Frontend (Vite + React)
1) Install and start dev server:
```
cd frontend
npm install
npm run dev
```

2) Open the printed URL (default `http://127.0.0.1:5173/`). The app shows API and DB status.

Vite is configured to proxy `/api/*` to Flask at `http://127.0.0.1:5000` in `frontend/vite.config.js`.

## Folder structure
```
backend/
  app/
    __init__.py        # Flask app factory + CORS
    routes.py          # /api routes (health, db ping)
    db.py              # MySQL connection + helpers
  requirements.txt
  run.py               # Dev server entry

frontend/
  src/
    main.jsx           # React entry
    App.jsx            # Example API/DB status component
  vite.config.js       # Dev proxy to Flask
  package.json         # deps + scripts
  index.html           # Vite HTML entry
  assets/css/style.css # basic styles

TODO.md                # setup checklist
```

## Notes
- For production, build the frontend (`npm run build`) and serve the static files with a web server. Adjust CORS and deployment according to your environment.
- The backend uses environment variables (via `python-dotenv` in dev) to keep secrets out of source control.
""",
    }

    for path, content in files.items():
        write_file(path, content)

    # Delete this script at the end
    try:
        os.remove(os.path.abspath(__file__))
    except Exception:
        # Non-fatal if deletion fails
        pass


if __name__ == "__main__":
    main()


