# Fullstack Website (Flask + MySQL + React via Vite)

This project is a minimal full‑stack setup:
- Backend: Python Flask API with MySQL Connector
- Frontend: React (Vite dev server + proxy to Flask)

Prerequisites
- Python 3.10+
- Node.js 18+
- MySQL server

Quick start
```
# Backend
cd backend
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python run.py

# Frontend (in a separate terminal)
cd frontend
npm install
npm run dev
```
Open the printed URL (default `http://127.0.0.1:5173/`). Keep the Flask server running at the same time.

Backend (Flask)
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
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
python run.py
# or: waitress-serve --listen=0.0.0.0:5000 run:app
```

3) Verify endpoints:
- `GET http://127.0.0.1:5000/` → `{ "status": "ok" }`
- `GET http://127.0.0.1:5000/api/health` → `{ "status": "ok" }`
- `GET http://127.0.0.1:5000/api/db/ping` → `{ "status": "ok" }` if DB creds are valid

Frontend (Vite + React)
1) Install and start dev server:
```
cd frontend
npm install
npm run dev
```

2) Open the printed URL (default `http://127.0.0.1:5173/`). The app shows API and DB status.

Vite is configured to proxy `/api/*` to Flask at `http://127.0.0.1:5000` in `frontend/vite.config.js`.

Folder structure
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

Notes
- For production, build the frontend (`npm run build`) and serve the static files with a web server. Adjust CORS and deployment according to your environment.
- The backend uses environment variables (via `python-dotenv` in dev) to keep secrets out of source control.
