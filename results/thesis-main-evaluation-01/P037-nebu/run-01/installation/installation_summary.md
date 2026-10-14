## Nebu Installation Summary

**Working directory:** /workspace (repo at commit a4539d3). **Context:** Docker-enabled Ubuntu 22.04 host; all Nebu services run as Docker Compose containers on the default daemon. Docker-only build system — no local Elixir/buf/Go needed.

### Actions performed
1. Installed missing `make` (apt, GNU Make 4.3). Docker 29.7.2 + Compose v5.5.0 were already present with a working daemon.
2. `make setup` — created gitignored `.secrets/` with `internal_secret`, `minio_root_user`, `minio_root_password`, `minio_app_access_key`, `minio_app_secret_key`.
3. `docker compose build server` — built `nebu-server:latest` (Node 20 assets stage, Elixir 1.20 release, Alpine 3.23 runtime running `Nebu.Release.migrate()` then `./bin/nebu start`).
4. `docker compose up -d` — created network `nebu_default`, four volumes, and containers postgres/dex/minio/createbuckets/clamav/server.
5. Appended `127.0.0.1 dex` to `/etc/hosts` (guide step 3).

### Final method vs abandoned attempts
Final method = supported `make setup` + `docker compose up`. The one abandoned attempt was an initial `docker compose up -d --build` that failed at image pull because guide-pinned `minio/minio` and `minio/mc` tags no longer exist in any reachable registry. Recovery: added `docker-compose.override.yml` mapping those two services to Rancher mirror images.

### Resulting state (verified)
- `docker compose ps`: nebu-server-1, nebu-postgres-1, nebu-dex-1, nebu-minio-1, nebu-clamav-1 all `Up (healthy)`; nebu-createbuckets-1 exit 0.
- Server logs: migrations through version 34, Horde registry/supervisor start, `Running Nebu.Web.Router with Bandit 1.12.0 at 0.0.0.0:4000`; no errors.
- PostgreSQL: 34 migrations, ~38 tables owned by `nebu_migrate`.
- MinIO: bucket `nebu-media`, policy `nebu-app-policy` attached to app IAM user.

### Access points / commands
- Matrix API/media http://localhost:8008; Admin UI http://localhost:8080/admin (302 → /admin/bootstrap); health http://localhost:4000/health; Dex http://localhost:5556/dex; MinIO console http://localhost:9001; Postgres localhost:5432 (nebu/nebu).
- Start/stop: `cd /workspace && docker compose up -d` / `docker compose down`.

### Incomplete / unknown
- Bootstrap Wizard (guide step 4) not completed — requires interactive browser login via Dex; server is correctly fail-closed (fresh DB) so register/media return 401 until the wizard runs. Expected fresh-install state.
- Browser-only flows (Element SSO login, room creation) not exercised.
- Doc drift: guide's `Nebu.Application started` log token absent in this revision (equivalent = Bandit listener + /health); guide references a removed `nebu-admin` client whereas the repo uses single `nebu-gateway`.