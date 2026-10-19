# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** SPARK API

**Description:** Modular AI toolkit for legally compliant and transparent end-to-end support of all planning and approval processes

## Supplied installation guide

## Guide: Installation.md

# Deployment Guide

Minimal steps to build and run the monorepo services locally using Docker.

## Prerequisites

| Tool   | Version | Purpose                          |
|--------|---------|----------------------------------|
| Docker | 24+     | Container builds (BuildKit)      |
| uv     | 0.4+    | Python dependency management     |
| Node   | 20+     | Frontend builds (`npm ci`)       |
| Python | 3.12    | Backend services                 |

## Monorepo Structure

```
01-frontend/          # React frontend (npm workspace, build main Dockerfile)
02-backend/           # Python backend services (one Dockerfile each)
  demospipes/         # Pipeline framework (base + addon images)
03-shared-services/   # Shared Python libraries used by backends
helm/                 # Helm charts (for Kubernetes deployments)
```

## Replacing Base Images

All Dockerfiles use `<CONTAINER_REGISTRY>` as a placeholder for the original private container registry.
Replace these references with public equivalents before building:

| Placeholder in Dockerfile                                            | Public replacement (example)                                      |
|----------------------------------------------------------------------|-----------------------------------------------------------|
| `<CONTAINER_REGISTRY>/astral-uv-python-3.12-bookworm:1.0.0`         | `ghcr.io/astral-sh/uv:python3.12-bookworm`               |
| `<CONTAINER_REGISTRY>/python-3.12-bookworm:1.0.0`                   | `python:3.12-bookworm`                                    |
| `<CONTAINER_REGISTRY>/uv:0.9.30-python3.12-bookworm-slim-<hash>`    | `ghcr.io/astral-sh/uv:0.9.30-python3.12-bookworm-slim`   |

Apply with `sed` across all Dockerfiles:

```bash
find . -name 'Dockerfile*' -exec sed -i \
  -e 's|<CONTAINER_REGISTRY>/astral-uv-python-3.12-bookworm:1.0.0|ghcr.io/astral-sh/uv:python3.12-bookworm|g' \
  -e 's|<CONTAINER_REGISTRY>/python-3.12-bookworm:1.0.0|python:3.12-bookworm|g' \
  -e 's|<CONTAINER_REGISTRY>/uv:0\.9\.30-python3\.12-bookworm-slim-[a-f0-9]*|ghcr.io/astral-sh/uv:0.9.30-python3.12-bookworm-slim|g' \
  {} +
```

## Other Placeholders

The export process replaces internal references with placeholders. You may encounter these in configuration files and source code:

| Placeholder         | Meaning                                           | Action required                               |
|---------------------|---------------------------------------------------|-----------------------------------------------|
| `<REDACTED>`        | Internal URL or domain                            | Replace with your own domain or `localhost`   |
| `<LLM_MODEL>`       | LLM model name                                    | Replace with the model name you serve         |
| `<INTERNAL_URL>`    | Internal Kubernetes service URL                   | Replace with your service endpoint            |
| `<ALLOWED_ORIGIN>`  | CORS-allowed origin domain                        | Replace with your frontend URL                |

## Building Backend Services

Each backend service under `02-backend/` has its own Dockerfile. Services depend on shared libraries in `03-shared-services/`, which must be accessible during the Docker build.

```bash
# Example: build a single backend service
cd 02-backend/dokumentenpruefung
DOCKER_BUILDKIT=1 docker build -t dokumentenpruefung .
```

**Path dependencies:** Backend Dockerfiles expect `03-shared-services/` to be reachable via relative paths. If `docker build` fails because of missing path dependencies, either:

1. Use the monorepo root as the build context and point `-f` to the service Dockerfile:
   ```bash
   docker build -f 02-backend/dokumentenpruefung/Dockerfile .
   ```
2. Copy the required shared libraries into the service directory before building.

**Build secrets:** Some Dockerfiles use `--mount=type=secret` for private registry credentials. When building with the public base images listed above, pass dummy values:

```bash
DOCKER_BUILDKIT=1 docker build \
  --secret id=TECHNICAL_USER_USERNAME,env=DUMMY_USER \
  --secret id=TECHNICAL_USER_TOKEN,env=DUMMY_TOKEN \
  -t my-service .
```

Set `DUMMY_USER` and `DUMMY_TOKEN` to any non-empty string (e.g., `export DUMMY_USER=x DUMMY_TOKEN=x`).

## Demospipes Build Order

The `demospipes` pipeline framework requires a specific build order. Base images must be built before addon images that depend on them:

1. **Base images** (no external dependencies on each other):
   - `02-backend/demospipes/api/Dockerfile` (tag as `demospipes-base-api`)
   - `02-backend/demospipes/core/Dockerfile` (tag as `demospipes-base-executors`)

2. **Addon images** (reference the base images via `FROM`):
   - `02-backend/demospipes/addons/bmds/api/Dockerfile`
   - `02-backend/demospipes/addons/bmds/executors/Dockerfile`

Replace the `<CONTAINER_REGISTRY>/demospipes-base-api:*` and `<CONTAINER_REGISTRY>/demospipes-base-executors:*` references in addon Dockerfiles with the local tags you used in step 1.

## Building the Frontend

### Via Docker (recommended)

The frontend Dockerfile handles `npm ci` and the full build internally:

```bash
cd 01-frontend
DOCKER_BUILDKIT=1 docker build -t frontend .
```

### Without Docker

To build directly on the host (e.g., for development):

```bash
cd 01-frontend
npm ci
npm run build:all
```

The frontend is an npm workspace. `npm ci` installs all workspace dependencies; `build:all` compiles all micro-frontends.

## Runtime Configuration

Most services require environment variables for database connections, message brokers, and external service URLs. Check each service's `.env.example` (if present) or its settings/config module for required variables. Common dependencies include:

- PostgreSQL
- RabbitMQ
- An LLM inference endpoint (configure the API URL and replace `<LLM_MODEL>` with the model name served there)

## Helm Charts

The `helm/` directory contains Kubernetes deployment charts. These are provided for reference and production deployments. Chart `values.yaml` files contain `<CONTAINER_REGISTRY>` placeholders that need the same replacement as the Dockerfiles. For local development, Docker builds are sufficient.

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

## Environment
- Workspace: `/workspace` (SPARK API monorepo, commit 520d93f, v0.5.0). Ubuntu 22.04 container, Docker 29.7.2 + BuildKit (dockerd on `/var/run/docker.sock`), 8 CPU / 7.6 GB RAM.
- Host tools installed during the task: `uv` 0.13.1 (standalone installer, `/root/.local/bin`), `rsync`.

## Method (per the provided guide, with necessary additions)
1. **Base-image replacement**: applied the guide's `sed` to all 34 Dockerfiles (`<CONTAINER_REGISTRY>/astral-uv-python-3.12-bookworm:1.0.0` → `ghcr.io/astral-sh/uv:python3.12-bookworm`, `python-3.12-bookworm:1.0.0` → `python:3.12-bookworm`, hashed uv-slim → `ghcr.io/astral-sh/uv:0.9.30-python3.12-bookworm-slim`). Addon `FROM <CONTAINER_REGISTRY>/demospipes-base-*:*` → local tags per the guide's demospipes section.
2. **Missing lock files**: the repo contains **no `uv.lock`** although every Dockerfile runs `uv sync --locked`. Generated `uv.lock` for all 37 Python projects (26 backend dirs, 6 demospipes sub-projects, 6 shared services — 41 pyprojects total minus workspaces) using host uv from the monorepo root.
3. **Frontend lockfile**: `01-frontend/package-lock.json` was out of sync with workspace manifests (`npm ci` EUSAGE error, e.g. `@hey-api/openapi-ts@0.80.18 missing`). Regenerated with `npm install --package-lock-only` (package versions unchanged, e.g. react-hook-form 7.87.0 both before/after).
4. **Path dependencies (guide's option 2)**: every backend `uv sync` stage depends on `03-shared-services/*` via relative paths. For each service I staged `<service>/*` plus the full transitive closure of the six shared libs (and `tatbestandsmerkmalsextraction` for rechtsquellenvorbereitung) flat into `/workspace/.build-logs/stage/<name>/`, relabeled `[tool.uv.sources.*] path` entries (`.build-logs/rewrite_paths.py`), re-ran `uv lock`, and inserted `COPY . <WORKDIR>/` (+ `--chown user:user` where the stage runs as a non-root user, e.g. `bmi_user`) before the first `uv sync` (`.build-logs/patch_dockerfile.py`), because the Dockerfiles run `uv sync` before `COPY . /app` and originally resolved those deps from the private registry.
5. **Build secrets**: all builds passed `--secret id=TECHNICAL_USER_USERNAME,env=x --secret id=TECHNICAL_USER_TOKEN,env=x` (dummy values) as the guide documents.
6. **demospipes `<REDACTED>` private pip index** (core + bmds addons): not publicly resolvable. Replaced the `pip wheel --extra-index-url https://user:pass@<REDACTED>` step with local wheels of the path-dep packages (`uv build --wheel` for `data-structures` / `data_structures`, `COPY local-wheels/ + --find-links`, `.build-logs/fix_pipwheel.py`). Verified: the packages do not exist on public PyPI (HTTP 404), and they are **present in the built images** (`demospipes_data_structures 1.0.3` in `demospipes-base-executors`).
7. **Build order**: demospipes bases first (`demospipes-base-api`, `demospipes-base-executors`), then addons (`demospipes-bmds-api`, `demospipes-bmds-executors`) FROM the local base tags.

## Resulting state — 32 SPARK service images built (all exit 0)
- 24 standalone backends: berichtskonfigurator, decision-log-store-service, demos-einwendungsmanagement, dokumentenaufbereitung-data-service, dokumentenaufbereitung-monorepo, dokumentenpruefung, dokumentenschwaerzung-orchestrator, dokumentenschwaerzung-pdf-pii-detector, dokumentensuche, fristenmanagement, graph-api, ki-guv-ai-testing, ki-guv-explainability, ki-guv-feedback, kommentar-service, nachforderungen, ner-extraction, norm-matching, rechtsquellenvorbereitung, request-proxy, risikohinweis-service, subsumtion-service, tex2pdf-service, xoev-adapter
- 4 demospipes: demospipes-base-api, demospipes-base-executors, demospipes-bmds-api, demospipes-bmds-executors
- 1 shared library: ki-validierung
- 3 frontends: `frontend` (main monorepo image, nginx on :8080 with all 8 MFE + 8 injector dists), `mfe-ewm`, `mfe-fp`
- Build logs/orchestrators: `/workspace/.build-logs/` (scripts, per-service logs, results files)

## Fixes required beyond the guide (repo defects encountered)
- `02-backend/tex2pdf-service/CHANGELOG.md` is referenced by its Dockerfile (`COPY CHANGELOG.md`) but absent from the repo → added a stub.
- Frontend main Dockerfile runs 16 parallel `vite build`s; on the 7.6 GB container several were OOM-killed (exit 137) and the unguarded `wait` masked the failure → batched to 2-3 parallel per MFE pair in the staged build context (original Dockerfile untouched).
- Standalone `shell`/`mfe-ws` Dockerfiles: `shell` lacks a `build:injector` script (silently fails under `wait`); `mfe-ws` is missing the `shared` build step its siblings have. Corrected mfe-ws still fails on a pre-existing phantom dependency (`import "uuid"` in `RedactionsLayer.tsx`, undeclared) and `shell` on a pre-existing `TS2322` type error in `MandatoryFeedback.tsx` — both are repo source issues, and both services build and serve correctly inside the main `frontend` image (the guide's recommended method).

## Known startup requirements (documented by the guide)
- Backends start via their ENTRYPOINT (e.g. `/app/.venv/bin/<service>` or `uv run ... uvicorn ...`); three services (kommentar-service, demospipes-bmds-api/executors) require their documented runtime env vars (`SERVICE_NAME/SERVICE_VERSION/POSTGRE_*`, `PREFECT_FLOW_NAME`, `URL_ORIGINAL/URL_REPLACEMENT`, `MICROSERVICE_*_URL`) at import time — verified to import successfully once supplied.
- Frontend: `docker run -p 8080:8080 frontend`.

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