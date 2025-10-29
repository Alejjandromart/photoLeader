# Copilot Coding Agent Instructions for PhotoLeader

## Project Overview
PhotoLeader is a distributed photo upload and gallery system using a MongoDB Replica Set (5 nodes: 1 primary, 4 secondaries) for high availability. Only photo metadata is stored in MongoDB; media files are not persisted in the database.

## Architecture
- **backend/**: Python code for interacting with MongoDB. Includes:
  - `client/`: Scripts for simulating uploads (`upload_sim.py`) and reads (`read_sim.py`).
  - `tests/`: Unit tests for backend logic.
  - `requirements.txt`: Python dependencies (mainly `pymongo`).
- **frontend/**: Static web app (HTML/CSS/JS) for user interaction. No build step required.
- **infrastructure/**: Scripts and configs for local/remote deployment:
  - `docker-compose.yml`: Spins up 5 MongoDB containers and a setup service.
  - `mongo-init.js`: Initializes the replica set.
  - PowerShell scripts for setup, deployment, and troubleshooting (Windows-focused).

## Key Workflows
- **Local Development (Windows, PowerShell):**
  1. Start MongoDB cluster: `cd infrastructure; docker-compose up -d`
  2. Wait 10+ seconds, check status: `docker exec -it mongo1 mongosh --eval "rs.status()"`
  3. Activate Python venv: `.\.venv\Scripts\Activate.ps1`
  4. Install dependencies: `pip install -r backend/requirements.txt`
  5. Simulate uploads: `python backend/client/upload_sim.py --count 10`
  6. Read gallery: `python backend/client/read_sim.py`
- **Frontend:**
  - Open HTML files directly or serve via `python -m http.server 8080` in `frontend/`.
- **Testing:**
  - Run backend tests in `backend/tests/` using standard Python test runners.

## Conventions & Patterns
- **MongoDB Access:**
  - All writes use `writeConcern=majority` for consistency.
  - Reads prefer secondaries (`readPreference=secondaryPreferred`).
  - Connection URIs and replica set names are parameterized in scripts.
- **Windows-first:**
  - PowerShell scripts automate most infrastructure tasks.
  - Guides and scripts assume Windows + Docker Desktop.
- **No media storage in DB:**
  - Only metadata (filename, user, tags, etc.) is persisted.

## Integration Points
- **MongoDB Replica Set:**
  - Managed via Docker Compose (local) or PowerShell (remote).
  - `mongo-init.js` and `setup-mongo.ps1` are critical for cluster setup.
- **Python Backend:**
  - Uses `pymongo` for all DB operations.
  - Scripts in `backend/client/` are entry points for data flow.
- **Frontend:**
  - Purely static; communicates with backend via REST (if/when API is present).

## Examples
- Simulate upload: `python backend/client/upload_sim.py --count 5`
- Read with tag: `python backend/client/read_sim.py --tag natureza`
- Start frontend server: `cd frontend; python -m http.server 8080`

## References
- See `README.md` files in root, `backend/`, `frontend/`, and `infrastructure/` for detailed guides and command examples.
- For Windows setup, see `README_WINDOWS.md` and PowerShell scripts in `infrastructure/`.

---
If you are unsure about a workflow or convention, check the relevant `README.md` or ask for clarification.
