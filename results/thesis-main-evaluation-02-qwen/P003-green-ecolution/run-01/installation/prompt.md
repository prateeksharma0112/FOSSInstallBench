# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** Green Ecolution

**Project description:** Platform for smart irrigation and green space management in municipalities based on LoRaWAN sensor data and route optimization.

**Installation guide:**

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
