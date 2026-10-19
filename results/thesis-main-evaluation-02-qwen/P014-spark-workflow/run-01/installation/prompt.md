# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** SPARK Workflow

**Project description:** AI assistance solution for complex planning and approval processes in public administration

**Installation guide:**

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

# ENVIRONMENT
The project repository has already been checked out at the predefined commit SHA in the current working directory. This directory is the shared installation workspace; keep additional project repositories and project-local artifacts within it.

# RULES
* Treat the supplied installation guide as the primary source of installation instructions.
* You may perform actions that are reasonably necessary to carry out the installation using the available tools.
* You may install prerequisites or dependencies when required for the installation.
* Strictly use non-interactive command options whenever available. Never issue commands that wait for user input.
* If the supplied guide provides multiple documented installation methods, do not declare the installation failed solely because one method fails.
* When feasible, attempt another documented installation method before concluding that the installation cannot be completed.
* When a command times out, inspect the resulting state and continue from any partial progress before declaring failure.
* Do not treat an encountered error as an installation failure if you are able to recover from it and subsequently complete and verify the installation.
* Base the reported outcome on evidence obtained during this installation attempt.
* The absence of a preinstalled tool or package is not an infrastructure failure unless observable evidence demonstrates that it cannot reasonably be installed or used in the environment.
* For a decisive failed command, include its command, exit code, and relevant error output in `reported_outcome_evidence`.


# OUTCOME & REPORTING DEFINITIONS

## Installation Success

Classify the installation as `SUCCESS` only when the installation has been completed and objective evidence demonstrates that the software is installed correctly.

## Installation Failure

Classify the installation as `FAILURE` when the installation cannot be completed or when sufficient objective evidence of successful installation cannot be obtained.

For a failed attempt, report both:

**Failure mode:** A concise, evidence-based description of what happened and how the installation failed.

**Failure attribution:** What was the primary cause/source of the failure?

Select exactly one primary attribution from the following categories:

* `DOCUMENTATION` — The supplied installation documentation is incomplete, incorrect, ambiguous, inconsistent, or outdated in a way that materially contributes to the failure.
* `AGENT` — Sufficient and correct information was available, but the agent's interpretation, decision, or action materially contributed to the failure.
* `INFRASTRUCTURE` — The failure is caused by a limitation or incompatibility of the available execution environment that cannot reasonably be changed as part of the installation task, such as unavailable required hardware, unsupported system capabilities, or absence of required infrastructure.
* `EXTERNAL_RESOURCE` — The failure is caused by a required resource outside the available execution environment that is unavailable or inaccessible, such as a private package registry, unavailable external service, inaccessible download endpoint, or required credentials.
* `INDETERMINATE` — The available evidence is insufficient to reliably attribute the failure to one of the categories above.

Select an attribution based on observed evidence rather than speculation.

## Installation summary

Describe in Markdown what was done during installation and the resulting state: the method used, relevant absolute paths and working directories, actions performed, known startup commands or access points, and any incomplete work or unknown state. Include the execution context needed to interpret paths and commands, such as an application container or virtual environment. Distinguish the final method from abandoned attempts where applicable.

Provide factual context for independent inspection, without outcome judgments or recommendations.

# FINAL OUTPUT

Return the final installation report using the required structured output fields.

- `reported_outcome`: Report `success` or `failure` according to the criteria defined above.
- `installation_summary`: Describe complete summary of the installation attempt as defined above.
- `additional_actions`: List installation or configuration actions performed that were not explicitly stated in the supplied installation guide. Return an empty list if none were performed.
- `verification`: Report the verification method used and the observed result. Include the command and exit code where applicable. If verification was not performed, state this and provide the reason.
- `reported_outcome_evidence`: Record the observable command results or execution evidence that directly support the reported outcome.
- `failure_mode`: For a failed attempt, provide a concise, evidence-based description of how the installation failed. For a successful attempt, return `null`.
- `failure_attribution`: For a failed attempt, select exactly one predefined failure-attribution category. For a successful attempt, return `null`.

Base the reported outcome only on evidence observed during the installation attempt.
