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
