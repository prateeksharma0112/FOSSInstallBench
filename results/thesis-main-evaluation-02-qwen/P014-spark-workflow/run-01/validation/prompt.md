# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** SPARK Workflow

**Description:** AI assistance solution for complex planning and approval processes in public administration

## Supplied installation guide

## Guide: Installation.md

## Getting Started

### Prerequisites

- Docker with Docker Compose
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Process Compose](https://f1bonacc1.github.io/process-compose/installation/)
- Node.js 24 and pnpm 10.30.2 for the frontend
- An OpenAI-compatible LLM provider, for example LiteLLM
- A Docling Serve endpoint

### Dependencies

The local development stack provides the shared platform services used by the modules:

- Temporal for workflow execution and the workflow UI
- MinIO/S3 for document and object storage
- Qdrant for vector storage
- PostgreSQL-backed application databases
- Keycloak, SpiceDB, Redis, and the shared backend services configured in Docker Compose and Process Compose

The local setup starts shared infrastructure with Docker Compose and runs the application services, workers, seed jobs, and frontend on the host with Process Compose.

### External AI Services

The local stack does not start an LLM provider. During secret generation, provide an OpenAI-compatible base URL, API key, chat model, and embedding model.

Document extraction also requires Docling Serve. You can point the setup at an existing Docling deployment, or run a local CPU container:

```bash
docker run -d --name spark-docling-cpu \
  -p 5001:5001 \
  -e DOCLING_NUM_THREADS=4 \
  -e OMP_NUM_THREADS=4 \
  -e DOCLING_SERVE_ENABLE_UI=1 \
  -e DOCLING_SERVE_MAX_DOCUMENT_TIMEOUT=3600 \
  -e DOCLING_SERVE_MAX_SYNC_WAIT=3600 \
  -e DOCLING_SERVE_LOAD_MODELS_AT_BOOT=True \
  quay.io/docling-project/docling-serve-cpu:latest
```

When using the local container, enter these Docling values in the secret generation prompt:

- Protocol: `http`
- Host: `localhost`
- Port: `5001`
- OCR engine: an engine supported by your Docling Serve image, for example `rapidocr`

### First Local Start

Generate the private root `.env` file first. The script prompts for the email and password of your local login user, then for external provider settings, and generates shared local infrastructure secrets. The login user is created automatically in the local Keycloak when the infrastructure starts. The script refuses to overwrite an existing `.env`. If you regenerate it later, wipe the Docker containers and volumes before starting again, because Postgres, MinIO, Temporal, and SpiceDB persist the old credentials.

```bash
uv run poe create-secrets
```

Install frontend dependencies:

```bash
cd 01-frontend/frontend
corepack enable
pnpm install --frozen-lockfile
cd ../..
```

Start shared infrastructure:

```bash
docker compose --env-file .env up --wait
```

Start application services and the frontend:

```bash
uv run poe process-compose
```

Process Compose loads the root `.env` by default. Keep it limited to shared local secrets and external provider credentials. Service-specific application settings stay in each service’s tracked `.env.local` file, with explicit local aliases in `process-compose.yaml` where a service expects a different environment variable name.

The startup automatically runs the seed jobs needed for a fresh local system:

- `project-logic-seed` inserts default project status and project type rows.
- `formal-completeness-seed` inserts FCS template categories and document types.
- `administrative-file-draft-seed` inserts the default VAE template from `src/scripts/data/vae_nodes.json`.

The law database (gesetze-normen) is seeded with `scripts/data/gesetze-normen-seed.sql.gz` when Postgres initializes a fresh volume. The plausibility checks rely on this data.

### Open the Application

Open the frontend at:

```text
http://localhost:3000/app/
```

You are redirected to the local Keycloak login. Sign in with the email and password you chose during `uv run poe create-secrets`.

Useful local endpoints:

- Frontend: `http://localhost:3000/app/`
- Keycloak admin console: `http://localhost:9090`
- Temporal UI: `http://localhost:8233`
- MinIO console: `http://localhost:9001`
- Qdrant API: `http://localhost:6333`
- Process Compose API: `http://localhost:8080`

### Running behind a reverse proxy (`$WEB_HOST`)

The local stack assumes the browser and the containers share `localhost`. Setting the
`$WEB_HOST` variable signals that the stack runs behind a port-prefixing reverse proxy instead:
the browser is remote and reaches each service through `https://<port>-$WEB_HOST`, so every
**browser-facing** URL (the frontend, the Keycloak login redirect, and object-storage presigned
URLs) must use that public host instead of `localhost`.

This is handled automatically: when `$WEB_HOST` is set, `scripts/create_secrets.sh` writes the
public base URLs into `.env`, and `docker-compose.yaml` / `process-compose.yaml` pick them up. No
manual edits are needed — just run the normal flow on the proxied host:

```bash
uv run poe create-secrets        # detects $WEB_HOST, writes FRONTEND_PUBLIC_URL / KEYCLOAK_PUBLIC_URL / S3_PUBLIC_URL
docker compose --env-file .env up --wait
uv run poe process-compose
```

Then open `https://3000-$WEB_HOST/app/` (not `localhost:3000`).

What changes vs. localhost:

- **Keycloak** advertises `https://9090-$WEB_HOST` as its issuer; oauth2-proxy uses the public
  host for the browser-facing (front-channel) login/redirect, while token redeem and JWKS stay on
  the internal docker network (`keycloak:9090`) so they never traverse the authenticating proxy.
- **Object storage** is served **same-origin** through oauth2-proxy (the `/dms-local/` route),
  because an authenticating reverse proxy blocks the cross-origin CORS preflight a direct upload
  to a separate MinIO port would trigger. Presigned URLs use path-style addressing so the
  signature validates behind the proxy.

If you regenerate `.env` after moving between a plain-localhost and a reverse-proxy setup, wipe the Docker volumes
first (as for any `.env` regeneration). Override the Vite host allow-list with
`VITE_DEV_ALLOWED_HOSTS` if you serve the frontend under a different domain.

### Run a Workflow

Use the normal frontend workflow:

1. Open `http://localhost:3000/app/` and sign in.
2. Create a Verfahren.
3. Upload a ZIP file in the Unterlagen area.
4. Click `Zum Verfahren`.
5. On the `Formale Vollständigkeitsprüfung` page, click `KI-Analyse starten`.
6. Follow progress in the frontend or in [Temporal UI](http://localhost:8233).

The formal completeness check workflow runs document extraction, result insertion, Qdrant indexing, document-type matching, table-of-contents matching, and plausibility checks.

### Docker Base Images

By default, the Python service Dockerfiles use `python:3.13-slim` from Docker Hub (no login required). The base images are defined as build arguments in the first lines of each Dockerfile, where `BASE_IMAGE_DEV` is used by the build stages and `BASE_IMAGE` is the final runtime image:

```dockerfile
ARG BASE_IMAGE_DEV=python:3.13-slim
ARG BASE_IMAGE=python:3.13-slim
```

To use Docker Hardened Images instead, replace these defaults with images from `dhi.io/python`. The build stages need the `-dev` variant, which includes a shell and package manager. This requires a prior `docker login dhi.io` with valid credentials:

```dockerfile
ARG BASE_IMAGE_DEV=dhi.io/python:3.13.13-debian13-dev
ARG BASE_IMAGE=dhi.io/python:3.13.13-debian13
```

Alternatively, override the build arguments at build time without editing the Dockerfile. The build context is the repository root:

```bash
docker build \
  -f 02-backend/examination_service/Dockerfile \
  --build-arg BASE_IMAGE_DEV=dhi.io/python:3.13.13-debian13-dev \
  --build-arg BASE_IMAGE=dhi.io/python:3.13.13-debian13 \
  .
```

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

Installed and started the SPARK Workflow local dev stack in /workspace (root; Docker + host processes). Method: follow the guide's flow — install prerequisites (uv, process-compose, Node 24.14.0 + pnpm 10.30.2 via corepack), `uv sync --locked --all-packages` (venv /workspace/.venv), `pnpm install --frozen-lockfile`, generate .env via `uv run poe create-secrets`, `docker compose --env-file .env up --wait` (exit 0), then `uv run poe process-compose`. External AI services (which the stack does not start) were provided: a local OpenAI-compatible LLM endpoint (/workspace/.local-services/llm_stub.py, port 8000, 1024-dim embeddings, any-model) and the documented local Docling CPU container (port 5001).

Notable recovery: the documented `minio/minio` and `minio/mc` images are unavailable (MinIO archived its OSS binaries; images denied on Docker Hub/quay/registry.min.io/ghcr.io). I built local minio/minio:latest and minio/mc:latest Docker images from sha256-verified MinIO GitHub-release binaries (server RELEASE.2025-09-07, mc RELEASE.2025-08-13) so the unchanged compose file worked. Also: process-compose needed `-t=false` (no TUI terminal), and a clean restart to clear an initial orphan-process port conflict; several services needed individual restart via the process-compose API (port 8080) after memory-pressure exits.

Final state: docker infra healthy (Postgres/Temporal/MinIO/Qdrant/SpiceDB/Keycloak/oauth2-proxy); 20/20 backend services ready; 13 workers; 3 seed jobs completed (project_logic statuses/types, FCS template_document_type=24, VAE template nodes=159); law DB (gesetze-normen) seeded (19,792 satz); frontend Vite :3002/app/ → 200; public entry :3000/app/ → 302 to Keycloak; full login with seeded user → app 200 "SPARK Workflow"; Temporal UI :8233, MinIO console :9001, Qdrant :6333, Docling :5001/health all OK; process-compose 35/38 running (3 not running are completed seeds).

Access points: app http://localhost:3000/app/ (Keycloak login, user spark@example.com); Temporal UI :8233; MinIO console :9001; Keycloak admin :9090; Process Compose API :8080. Logs: /tmp/compose-up.log, /tmp/process-compose.log, /tmp/process-compose-root.log.

Caveat: 7.6 GiB RAM is tight for this 38-process ML stack; parallel boot caused host-level (non-cgroup) memory kills of some services, recovered by individual restarts. Stack is stable now but may need individual service restarts under heavy parallel load.

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