# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** Green Ecolution

**Description:** Platform for smart irrigation and green space management in municipalities based on LoRaWAN sensor data and route optimization.

## Supplied installation guide

## Guide: Installation.md

## Quick Start

For a development setup with hot reload:

```bash
just infra-up    # Start infra (Postgres, Keycloak, Traefik, Valhalla, Streamlet)
just migrate-up  # Apply database migrations
just run-dev     # Run backend (hot reload) + frontend
```

Open [http://localhost:3000](http://localhost:3000).

To run everything in containers with a single command (infra + app + migrations), use `just run-docker` instead.

### With HTTPS (Let's Encrypt)

For valid TLS certificates (required for PWA testing on mobile), you need a domain with DNS API access on [Porkbun](https://porkbun.com). Either ask the `green-ecolution.dev` domain owner for API keys, or register your own domain on Porkbun and set `DOMAIN=your-domain.dev` in `.env`.

1. Copy `.env.example` to `.env` and add your Porkbun API keys (and optionally `DOMAIN`)
2. Create DNS records: `just dns-setup`
3. Start infra: `just infra-up`
4. Apply migrations: `just migrate-up`
5. Start dev environment: `just run-dev`

Open `https://<your-ip>.green-ecolution.dev:3443` (or your custom domain).

## Setup

### Requirements

- Rust toolchain (rustup, includes cargo)
- WASM target (`rustup target add wasm32-unknown-unknown`) — required for WASM builds used by the domain bindings
- Node.js + pnpm (`corepack enable`)
- Docker + Docker Compose
- [`just`](https://github.com/casey/just) — command runner (`cargo install just`)
- [`wasm-pack`](https://github.com/rustwasm/wasm-pack) (`cargo install wasm-pack`) — builds the domain WASM bindings, required by `just build`
- [`bacon`](https://github.com/Canop/bacon) (`cargo install bacon`) — live reload, required by `just run-dev`
- [`sqlx-cli`](https://crates.io/crates/sqlx-cli) (`cargo install sqlx-cli --no-default-features --features rustls,postgres`) for migrations and offline-cache regeneration

### Installation

```bash
just setup       # cargo fetch + pnpm install + build frontend workspace packages + domain WASM
just build       # Build frontend + backend
```

### Common Commands

| Command | Description |
|---------|-------------|
| `just run-dev` | Backend + frontend dev via Traefik (bacon live reload) |
| `just run-docker` | Full stack via Docker Compose |
| `just infra-up` | Start infrastructure only |
| `just test` | Run all tests (Rust workspace + frontend) |
| `just lint` | Lint Rust workspace + frontend |
| `just generate-sqlx` | Refresh sqlx offline query cache |
| `just migrate-up` | Apply database migrations |
| `just migrate-new <name>` | Create new migration |
| `just seed-up` | Apply seed data on top of the migrated DB |

> For a reproducible dev environment, you can also use `nix develop`.

### Services

`just infra-up` starts these services and routes them via Traefik. The Backend API is not part of the infra stack — it becomes available once you run `just run-dev` or `just run-docker`.

**Without Porkbun keys** (HTTP on port 3000):

| Service | URL |
|---------|-----|
| Backend API | <http://localhost:3000/api> (needs `run-dev` / `run-docker`) |
| Keycloak | <http://auth.localhost:3000> |
| pgAdmin | <http://pgadmin.localhost:3000> |
| Valhalla | <http://valhalla.localhost:3000> |
| Streamlet | <http://streamlet.localhost:3000> |

**With Porkbun keys** (HTTPS on port 3443, valid Let's Encrypt certs):

| Service | URL |
|---------|-----|
| Backend API | `https://<ip>.green-ecolution.dev:3443/api` (needs `run-dev` / `run-docker`) |
| Keycloak | `https://auth.<ip>.green-ecolution.dev:3443` |
| pgAdmin | `https://pgadmin.<ip>.green-ecolution.dev:3443` |
| Valhalla | `https://valhalla.<ip>.green-ecolution.dev:3443` |
| Streamlet | `https://streamlet.<ip>.green-ecolution.dev:3443` |

## Architecture

```
backend/  → Rust (axum, sqlx, tokio) - REST API, MQTT subscriber, auth
frontend/    → React (Vite, TanStack Router/Query, Zustand, Tailwind)
```

The backend is a Cargo workspace with two crates: a portable `domain` crate
(no sqlx/axum/tokio dependencies, reusable on WASM / mobile targets) and a
`server` crate that wires up the Postgres adapters, Keycloak integration,
MQTT subscriber, and the axum HTTP layer.

## PWA

The frontend is installable as a Progressive Web App with offline support via a Workbox service worker.

### HTTPS with valid certificates

PWA features like service workers require HTTPS. The project uses [Let's Encrypt](https://letsencrypt.org/) with DNS-01 challenge via [Porkbun](https://porkbun.com) to obtain valid TLS certificates for local development.

```bash
# 1. Add Porkbun API keys to .env (see .env.example)
# 2. Create DNS records pointing to your local IP
just dns-setup

# 3. Start dev environment (HTTPS on port 3443)
just run-dev
```

Your local IP is auto-detected. Access the app at `https://<ip>.green-ecolution.dev:3443`.

### Mobile testing

With HTTPS enabled, the app is accessible from any device on the local network. No certificate installation needed since Let's Encrypt certs are trusted by default.

- Frontend: `https://<ip>.green-ecolution.dev:3443`
- Auth: `https://auth.<ip>.green-ecolution.dev:3443`

### Without HTTPS

Without Porkbun API keys, the dev environment runs on plain HTTP (port 3000). PWA install and service workers won't work, but general development is unaffected.

```bash
just run-dev   # HTTP on localhost:3000
```

### Testing the service worker

The service worker is **disabled in `vite dev`** (`devOptions.enabled: false` in `vite.config.ts`) to avoid HMR conflicts with Workbox precaching. To verify PWA behavior (install prompt, update flow, offline fallback), build and serve the production bundle:

```bash
cd frontend/app && pnpm build && pnpm preview
```

…or run the full Docker stack via `just run-docker`.

## Configuration

All settings via environment variables (prefix `APP_`, separator `__`) or YAML files in `backend/config/` (`base.yaml`, `local.yaml`, `production.yaml`). The active profile is selected by `APP_ENVIRONMENT`.

Key areas: `application.*`, `database.*`, `auth.*`, `mqtt.*`, `log.*`

See the `backend` service in `compose.yaml` for examples.

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

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