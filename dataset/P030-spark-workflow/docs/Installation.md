# SPARK Workflow

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
