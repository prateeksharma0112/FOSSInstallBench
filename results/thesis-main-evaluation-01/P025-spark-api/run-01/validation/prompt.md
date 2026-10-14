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

## SPARK API installation summary

**Context:** Repository checked out at `/workspace` (commit 520d93f, monorepo root). Host: Docker 29.7.2 (BuildKit), 8 CPUs / 7.6 GB RAM / ~950 GB disk. No preinstalled host `uv`, `node`, or `python3` (Python/Node provided via container images).

**Method used:** Docker image builds (BuildKit) following `DEPLOYMENT.md`, plus the documented non-Docker frontend build (`npm ci && npm run build:all`). Work performed in `/workspace` and temporary assembled contexts under `/tmp` (e.g. `/tmp/g_<service>`, `/tmp/dpctx`, `/tmp/addon_api`, `/tmp/addon_exec`, `/tmp/core_ctx`).

**Actions performed:**
1. Applied the guide's `sed` replacement of `<CONTAINER_REGISTRY>` base-image placeholders across all Dockerfiles.
2. Installed `uv 0.12.23` on the host to generate the missing `uv.lock` files (none present in the export although all Python Dockerfiles use `uv sync --locked`).
3. Built 27 backend service images plus the two demospipes base images and two addon images, using augmented build contexts containing `03-shared-services/` (and sibling projects where needed) with rewritten relative paths and inserted COPY directives, per the guide's "Path dependencies" workaround.
4. Rebuilt `demospipes-base-executors` locally (original referenced the private `<REDACTED>` index for `demospipes-data-structures`); built the addons FROM the locally-tagged bases using local wheels.
5. Regenerated `01-frontend/package-lock.json` (`npm install --package-lock-only --ignore-scripts`) to fix `npm ci` EUSAGE; the Docker parallel MFE build was OOM-killed (exit 137), so the frontend was built via the documented non-Docker route (9 workspace `dist/` outputs).

**Resulting state / access points:**
- 29 locally built project images (~0.7–5.2 GB each) retained in the local Docker daemon.
- `demospipes-base-api:v1.18.127-main-ce4cc11`, `demospipes-base-executors:v1.24.195-main-8a31fa9`, `demospipes-addon-bmds-api:latest`, `demospipes-addon-bmds-executors:latest`.
- Frontend static assets under `/workspace/01-frontend/{shared,shell,mfe-*/}/dist`; served shell returned HTTP 200.
- Generated lockfiles: `02-backend/xoev-adapter/uv.lock`, `02-backend/fristenmanagement/uv.lock`, `02-backend/dokumentenpruefung/uv.lock` (others created inside temporary `/tmp` contexts).

**Runtime notes (not build failures):** Services need runtime config (PostgreSQL, RabbitMQ, LLM endpoint, env vars) — e.g. `dokumentenpruefung` exits on `NoOpLogger.setLevel` without a broker; `kommentar-service` requires `SERVICE_NAME`.

**Not installed:** `02-backend/demosplan` (no Dockerfiles in export); `tatbestandsmerkmalsextraction` (no Dockerfile; consumed as a path dependency by `rechtsquellenvorbereitung`).

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