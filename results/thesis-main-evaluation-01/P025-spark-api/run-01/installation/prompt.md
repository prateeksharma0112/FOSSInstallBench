# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** SPARK API

**Project description:** Modular AI toolkit for legally compliant and transparent end-to-end support of all planning and approval processes

**Installation guide:**

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
