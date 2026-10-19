## What was done

**Context:** Shared workspace at `/workspace` (SVA Studio monorepo, checked out at commit `6394d99`). Host: Ubuntu 22.04 container, Docker 29.7.2 + Compose v5.5.0, 8 CPU / 7.6 GiB RAM. Node/pnpm were not preinstalled.

**Profile selection:** The guide defines three runtime profiles. `studio` requires a remote Portainer/Quantum endpoint + private ghcr image + live Keycloak at `studio.smart-village.app`; `local-keycloak` requires a live Keycloak realm (`svs-intern-studio-staging`). `local-builder` is the self-contained local profile (mock auth, no OIDC), so it was used for installation.

## Steps (all in `/workspace`)

1. **Toolchain** — installed Node v24.15.0 (official tarball → `/usr/local`) and pnpm 11.3.0 via corepack, matching `.nvmrc`/`.node-version`/`packageManager`. `pnpm check:toolchain-consistency` → exit 0.
2. **Dependencies** — `pnpm install --frozen-lockfile` → exit 0 (~1500 packages).
3. **Local config** (git-ignored, created per the guide's vars-file model `config/runtime/base.vars` + `config/runtime/<profil>.vars`) — `config/runtime/base.vars` (shared local values, locally generated dev secrets: ENCRYPTION_KEY, IAM_PII_KEYRING_JSON, DB/Redis/worker passwords, OIDC local fallback values, `SVA_MAINSERVER_REQUIRED=false` because the mainserver is an external service not present in this workspace, `SVA_ENABLE_MONITORING=false`, `ENABLE_OTEL=false` + `SVA_ENABLE_SERVER_CONSOLE_LOGS=true` (documented early-test-phase console-to-loki path), IAM feature flags, `MIGRATIONS_DIR` pinned to an absolute path, `POSTGRES_HOST=127.0.0.1`, job-worker credentials) and `config/runtime/local-builder.vars` (`SVA_MOCK_AUTH=true`, `VITE_MOCK_AUTH=true`, `VITE_PUBLIC_BUILDER_KEY`).
4. **Redis TLS certs** — `bash dev/generate-tls-certs.sh` (repo script) → `dev/redis-tls/`.
5. **Infra** — `docker compose -f compose.yaml -f compose.override.yaml up -d postgres redis` (the canonical `env:up` also scales up `provisioner`/`migrate`/`bootstrap`/`candidate` services which need the private image `ghcr.io/smart-village-solutions/sva-studio` — pull returns 403 anonymous, so those remote/Keycloak-oriented services were not started; the local profiles run the app as a dev server anyway). Postgres 16 and Redis 7 (with password + TLS ports) healthy.
6. **Database** — goose migrations via `packages/data/scripts/run-migrations.sh up` (pinned goose v3.26.0 auto-downloaded, DB migrated to version 102), `packages/data/scripts/bootstrap-app-user.sh` (creates `sva_app` + `iam_app` grants), `deploy/portainer/migrate-graphile-worker.mjs` (provisions `graphile_worker` schema + `sva_enqueue_job`), worker role `sva_job_worker` + RLS policy `sva_job_worker_access` (same SQL as the repo's production bootstrap), and `packages/data/scripts/run-seeds.sh` (seeds `de-musterhausen`/`bb-guben` instances + personas).
7. **Workspace builds** — `pnpm build` (all 35 projects, exit 0) — required for the Vite dev SSR to resolve workspace plugin packages (`@sva/*` dist entries).
8. **App** — `pnpm nx run sva-studio-react:serve` launched with the exact env produced by the repo's own `buildProfileEnv('local-builder')` helper (same env the canonical `env:up:local-builder` would pass), listening on `http://localhost:3000` (pid 22747, log `/tmp/app-serve2.log`).

## Resulting state / access points

- App UI: `http://localhost:3000` (verified 200, `<title>SVA Studio</title>`); Postgres `127.0.0.1:5432` (sva/sva_local_dev_password, db sva_studio); Redis `127.0.0.1:6379` (password-protected, TLS on 6380).
- Runtime profile commands work against this state, e.g. `pnpm env:doctor:local-builder --json` (read-only diagnosis), `pnpm env:status:local-builder`.

## Caveats (environment/contract, not installation defects)

- `GET /health/ready` = 503: db=true, redis=true, jobWorker=ready, but `keycloak=false` (`keycloak_dependency_failed` — the readiness contract pings a live Keycloak admin `listRoles`; no local Keycloak exists in the repo and the `local-builder` mock profile has no IdP in this workspace).
- `env:doctor:local-builder`/`env:smoke:local-builder` report `auth_login_failed`/`auth_me_failed`: the checked-in smoke contract expects the legacy mock-login redirect `/?auth=mock-login` and a mock user named "Builder Mock User", while the checked-out app implements the current dev-auth flow (`/?auth=dev-login`, session-less `/auth/me` returns 401, session user has no `name` field) — a repo-internal contract drift, not an environment issue. The actual user flow works end-to-end (verified below).