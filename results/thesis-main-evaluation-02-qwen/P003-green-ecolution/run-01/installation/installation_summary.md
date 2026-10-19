## Installation: Green Ecolution (Rust/axum backend + React/Vite frontend + Docker infra)

**Environment:** shared container at `/workspace` (Ubuntu 22.04, 8 cores, 7.6 GB RAM), Docker Engine 29.7.2 dind on a WSL2 host, Docker Compose v5.5.0. Project repo already checked out at `/workspace`.

### Toolchain installed (guide "Requirements")
- Rust via rustup: stable 1.99.0 (at `~/.cargo`), plus `rustup target add wasm32-unknown-unknown`
- Node.js v24.4.0 installed to `/usr/local`; pnpm 10.20.0 via `corepack enable` + `corepack prepare pnpm@10.20.0 --activate` (matches `packageManager` pin)
- `just` 1.59.0 (prebuilt binary from GitHub release — the version-less `latest/download` URL 404s; used pinned `1.59.0` URL; installed to `/usr/local/bin/just`)
- `typst` 0.15.1 (pinned version from `frontend/Dockerfile`) from GitHub releases → `/usr/local/bin/typst`
- `cargo install wasm-pack` (0.15.0), `cargo install bacon` (3.26.0), `cargo install sqlx-cli --no-default-features --features rustls,postgres` (0.9.0)
- **Additional prerequisites not listed in the guide but required:** gcc/g++/make (Rust linking), `maven` + `openjdk-11-jdk-headless` (Keycloak theme build runs `jar xf`), `clang` + `lld` (hard requirement: `backend/.cargo/config.toml` sets `linker=clang`, `link-arg=-fuse-ld=lld`)

### Installation steps (per guide)
1. `cp .env.example .env` (no Porkbun keys → HTTP mode on port 3000)
2. `just setup` — ran 3 times: 1st failed on missing Maven, 2nd on missing `jar` (JRE without JDK), 3rd succeeded after installing maven + openjdk-11-jdk. Re-run confirms idempotent exit 0. Produced: domain WASM (`frontend/packages/domain-wasm/pkg`), built frontend workspace packages (ui, backend-client, plugin-interface, keycloak-theme), Keycloak login theme (`frontend/keycloak-theme/dist_keycloak/`).
3. **Valhalla tiles** (prerequisite for `infra-up`, via the justfile's `_build-valhalla-tiles` recipe replicated manually): `pbf-patch` image downloaded the Schleswig-Holstein OSM PBF from geofabrik and produced a patched Flensburg PBF; `generate-valhalla` image built the tiles into `.docker/infra/valhalla/custom_files/` incl. `valhalla_tiles.tar` (892 MB total) — this makes `_ensure-valhalla` skip the build.
4. `just infra-up` — 1st attempt failed: runc error `cannot enter cgroupv2 "/sys/fs/cgroup/docker" with domain controllers -- it is in threaded mode` on valhalla and streamlet (the only two services with `deploy.resources` limits; reproduced deterministically with `docker run --cpus 1 alpine` and `-m 256m`). This is a WSL2/cgroup-v2 host limitation not fixable from inside the container. **Workaround:** removed the two `deploy.resources` blocks from `compose.yaml` (YAML re-validated). 2nd attempt: all 6 infra containers up (db, keycloak, pgadmin, valhalla, streamlet, reverse-proxy/traefik); keycloak, valhalla, db healthy.
5. `just build` — 1st attempt failed with `error: linker 'clang' not found`; succeeded after installing clang+lld. Artifacts: `/workspace/bin/green-ecolution` (27.8 MB release binary), frontend production build `frontend/app/dist/`, handbook PDF, Keycloak theme.
6. `just migrate-up` — built the `migrate` binary (debug) and applied all migrations to the Postgres container (log: "Migrations applied").
7. `just run-dev` — running in background: backend on host port 3030 via `bacon --headless` (hot reload, SQLX_OFFLINE=true, APP_ENVIRONMENT=local) and Vite dev server on 5173, both routed through Traefik via `host.docker.internal` to port 3000.

### Verification (all exit 0 / HTTP 200)
- `curl -H 'Host: localhost' http://localhost:3000/` → 200, `<title>Dashboard | Green Ecolution</title>`
- `.../api/health` → 200; `.../api/ready` → 200 with `{"ready":true,... database healthy:true}`
- Keycloak `auth.localhost`: 302 to login, `/health/ready` 200 status UP, OIDC `.well-known/openid-configuration` 200
- pgAdmin `pgadmin.localhost`: 302 (login page)
- Valhalla `valhalla.localhost/status`: 200 (version 3.9.0, tileset loaded)
- Streamlet `streamlet.localhost/health`: 200 "ok"
- `/workspace/backend/target/release/green-ecolution healthcheck ready` → exit 0
- All containers `Up` (db/keycloak/valhalla `healthy`)

### Access points (HTTP mode, no Porkbun)
- App: http://localhost:3000 · API: http://localhost:3000/api · Keycloak: http://auth.localhost:3000 · pgAdmin: http://pgadmin.localhost:3000 · Valhalla: http://valhalla.localhost:3000 · Streamlet: http://streamlet.localhost:3000

### Notes / unknowns
- `just run-dev` runs as a background process (log: `/tmp/rundev.log`); stopping it via `just infra-stop` / process kill removes the app layer but infra containers persist.
- `compose.yaml` was modified (removed `deploy.resources` from valhalla/streamlet) as an environment workaround; otherwise the file is unmodified.
- `run-docker` and the Porkbun/HTTPS paths were not executed (not needed; run-dev is the primary documented path and works end-to-end).