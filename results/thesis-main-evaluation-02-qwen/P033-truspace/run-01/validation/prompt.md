# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** TruSpace

**Description:** Self-hosted, decentralized document collaboration platform that synchronizes documents between organizations over IPFS and supports local AI-assisted document analysis.

## Supplied installation guide

## Guide: Installation.md

# Local Setup

Run TruSpace on your own machine and access it at `http://localhost:3000`.

## Installation

```bash
git clone https://github.com/openkfw/TruSpace.git
cd TruSpace
./start.sh
```

On the **first run**, `./start.sh` detects that no `.env` file exists and launches the configuration wizard. Select profile **`1) local-dev`** and confirm the defaults with ENTER. TruSpace will then start automatically.

Once running, open [http://localhost:3000](http://localhost:3000) in your browser.

!!! tip "Re-run the wizard at any time"
`bash
    ./start.sh --configure-env
    `

## Options

| Flag               | Effect                                                       |
| ------------------ | ------------------------------------------------------------ |
| `--no-ai`          | Disable Ollama / Open WebUI to save RAM                      |
| `--dev`            | Build images locally instead of pulling                      |
| `--local-frontend` | Run the Next.js frontend outside Docker (enables hot reload) |

### Development with hot reload

If you are actively working on the frontend or backend, you can run those outside Docker while keeping the infrastructure (IPFS, database) containerised:

=== "Frontend hot reload"

    ```bash
    # Terminal 1 — infrastructure + backend in Docker
    ./start.sh --local-frontend

    # Terminal 2 — frontend with hot reload
    cd frontend
    npm install
    npm run dev
    ```

=== "Frontend + backend hot reload"

    ```bash
    # Terminal 1 — IPFS and AI only
    docker compose up ipfs0 cluster0 ollama webui -d

    # Terminal 2 — backend
    cd backend && npm install && npm run dev

    # Terminal 3 — frontend
    cd frontend && npm install && npm run dev
    ```

## Managing Containers

```bash
# View running containers
docker ps

# Follow logs
docker compose logs -f

# Stop (keeps data)
docker compose down

# Stop and delete all data ⚠️
docker compose down -v
```

## Data & Backups

All persistent data is stored in `./volumes/` inside the project folder.

```bash
# Back up
docker compose down
tar czf truspace-backup-$(date +%Y%m%d).tar.gz ./volumes .env
docker compose up -d

# Restore
docker compose down
rm -rf ./volumes
tar xzf truspace-backup-<date>.tar.gz
docker compose up -d
```

## Troubleshooting

**Port already in use**

```bash
lsof -i :3000   # find what's using the port
kill -9 <PID>
```

**Volume permission errors**

```bash
sudo chown -R 1000:1000 ./volumes
```

**Database error after an update**

```bash
# ⚠️ Deletes all accounts and workspace metadata; IPFS documents are unaffected
rm ./volumes/db/truspace.db
docker compose restart backend
```

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

**Method (final, per guide):** The TruSpace repository was already checked out at /workspace. Per the guide, the first-run configuration wizard was completed by selecting profile `1) local-dev` and accepting all defaults: `echo "" | bash /workspace/scripts/configure-env.sh` (start.sh invokes this same script; for the local-dev profile the only interactive prompt is profile selection, which defaults to 1). This wrote /workspace/.env (profile local-dev, NODE_ENV=development, BUILD_OR_PULL_IMAGES=build, ports 3000/8000/3333, IPFS 4001/5001/8080, cluster 9094/9097). Then `./start.sh` was run from /workspace (backgrounded with nohup, log monitored). The local-dev profile builds the backend and frontend Docker images from source (Dockerfile.dev / frontend Dockerfile) and pulls ipfs/kubo:v0.42.0, ipfs/ipfs-cluster:v1.1.6, and ghcr.io/open-webui/open-webui:0.10.2-ollama. start.sh completed: it created the ./volumes/ directories, built workspace-backend:latest and workspace-frontend:latest, started all containers, and confirmed "IPFS API is ready".

**Resulting state (all under /workspace, host Docker 29.7.2 / Compose v5.5.0, project dir /workspace):**
- Containers (docker ps): truspace-frontend (Up), truspace-backend (Up), ipfs0 (Up, healthy), cluster0 (Up), workspace-webui-1 (Up, healthy after one-time embedding-model download on first boot).
- Frontend: http://localhost:3000 → HTTP 200, `<title>TruSpace</title>` (the guide's access point).
- Backend API: http://localhost:8000/api, logs show "TruSpace API running and listening on port 8000"; knex "Batch 1 run: 1 migrations"; SQLite DB at /workspace/volumes/db/truspace.db.
- IPFS: http://localhost:5001/api/v0/version → v0.42.0; gateway :8080; cluster REST :9094 → v1.1.6; pinning service :9097 responding.
- AI: Open WebUI http://localhost:3333 → healthy, /health → {"status":true}; Ollama v0.30.11 runs bundled inside the webui container (OLLAMA_MODEL=gemma3:1b, model auto-download deferred until first use).

**Known commands:** start `cd /workspace && ./start.sh`; stop `docker compose down`; reconfigure `./start.sh --configure-env`. Access points: frontend :3000, API :8000/api, WebUI :3333, IPFS API :5001, cluster :9094. No incomplete work; temporary start.log was removed.

# ENVIRONMENT

You have access to the same container used for installation, including the files and dependencies left by the installation attempt. Each terminal call starts a fresh shell in `/workspace`. Shell-local directory changes, exported variables, and environment activation do not persist between calls. Include any required directory change, environment variables, or activation of an existing environment in each command.

# VALIDATION PROCEDURE

1. Review the guide and installation summary. Use the summary to locate the software and its components, and confirm the installation method, locations, and runtime context through inspection.
2. Identify the expected software behavior described in the guide and select checks appropriate to the resulting installation.
3. Run the checks in the correct directory and runtime environment. If needed, start the installed software within the boundaries below. Prefer evidence of software behavior over file existence alone.
4. Record the commands, observed results, and limitations. Assess the outcome using the definitions below and your own observations.

Distinguish the final installation method from abandoned attempts. Missing files required only by another installation method do not establish failure. A process not already running, or a timed-out or unavailable check, does not by itself establish failure.

# VALIDATION BOUNDARIES

You may inspect files, dependencies, processes and ports, run diagnostic commands, start or run the existing installation, and query local interfaces.

Do not install or update dependencies, build missing artifacts, perform missing setup or migrations, edit files or configuration, or repair the installation. Application startup and normal runtime file creation are permitted only when they do not perform these prohibited actions.

# OUTCOME DEFINITIONS

- `success`: Objective evidence obtained during validation demonstrates that the installation is complete and the software is operational according to the supplied guide.
- `failure`: Objective evidence obtained during validation demonstrates that the resulting installation is incomplete or cannot operate without further installation or repair work.
- `inconclusive`: The evidence is insufficient to establish either success or failure, including when observations are ambiguous or an environmental limitation prevents a reliable assessment.

# FINAL OUTPUT

Return the structured validation report with these three fields:

- `assessed_outcome`: Report `success`, `failure`, or `inconclusive` according to the definitions above.
- `outcome_evidence`: Record observable command results or execution evidence that directly support the assessed outcome. Include the exact command, working directory or runtime context, exit code where available, and relevant output for decisive checks. For an inconclusive assessment, record the observations or execution limitations preventing a decision.
- `assessment_summary`: Explain in detail what you inspected, how you performed validation, and how the observations support your assessment. Include checks that could not be completed, limitations, and unresolved uncertainty.