Installed and started SPARK Workflow locally at /workspace (commit 0cd030a). Method: documented Docker Compose + Process Compose flow.
- Prereqs installed: uv 0.12.23 (curl installer), CPython 3.13.16 via `uv python install`, Process Compose v1.122.0, Node.js 24.11.1 (tarball to /usr/local/node24), pnpm 10.30.2 via corepack.
- Python: `uv sync --locked --all-packages` in /workspace (root uv workspace, ~40 members) succeeded.
- Frontend deps: `pnpm install --frozen-lockfile` in /workspace/01-frontend/frontend succeeded.
- Secrets: `uv run poe create-secrets` run non-interactively (piped answers) → created /workspace/.env (mode 600).
- Infra: `docker compose --env-file .env up -d --wait` → all 11 containers healthy.
- App: `process-compose up -D` (detached, from /workspace; auto-loads root .env).
Workarounds/additional files: created /workspace/docker-compose.override.yaml to substitute bitnamilegacy/minio and bitnamilegacy/minio-client because docker.io/minio/minio and minio/mc are no longer publicly pullable; edited .env S3_SECRET_ACCESS_KEY to a value not starting with '-' (the generated one broke `mc`). Restarted processes that had failed first-run readiness probes during one-time Alembic migrations.
Final state: 33/38 processes Running, 5 seed jobs Completed exit=0, 0 failures; seeds verified in Postgres; frontend dev server on :3002 behind oauth2-proxy on :3000; endpoints and Keycloak token acquisition verified. External LLM/Docling are placeholder endpoints (not part of the local stack).