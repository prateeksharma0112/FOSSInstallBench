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