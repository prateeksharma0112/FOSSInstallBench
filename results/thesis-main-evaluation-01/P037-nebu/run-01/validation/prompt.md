# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** Nebu

**Description:** Enterprise-ready, Matrix-compatible chat server - Apache 2.0, SSO-ready, horizontally scalable.

## Supplied installation guide

## Guide: Installation.md

# Getting Started with Nebu

This guide walks you through setting up a local Nebu development environment from scratch.

## Prerequisites

| Tool | Version | Why |
|---|---|---|
| Docker Desktop | 4.x+ | Runs all services in containers |
| `make` | Any | Runs dev targets |
| `git` | Any | Clone the repository |

**No local Elixir or buf installation is needed.** All builds run inside Docker containers.

---

## 1. Clone and Initial Setup

```bash
git clone <your-fork-url> nebu
cd nebu
make setup
```

`make setup` does two things:
- Generates `.secrets/internal_secret` (32-byte random hex, the PSK for node registration) if absent
- Prints the dev OIDC credentials (Dex local users, see step 4 below)

The `.secrets/` directory is in `.gitignore` - never commit it. If you need a custom
`POSTGRES_PASSWORD`, copy `.env.example` to `.env` manually before `make dev`.

---

## 2. Start the Stack

```bash
make dev
```

This runs `docker compose up` and starts:

| Service | URL | Purpose |
|---|---|---|
| Nebu (Matrix API + Admin UI) | http://localhost:8008 | Main endpoint for clients |
| Dex (OIDC provider) | http://localhost:5556 | Dev identity provider |
| PostgreSQL | localhost:5432 | Database (user: `nebu`, db: `nebu`) |
| MinIO | http://localhost:9001 | S3-compatible media storage (dev) |

Wait until you see `Nebu.Application started` in the server logs:

```bash
docker compose logs -f server
```

---

## 3. /etc/hosts Setup (One-Time)

Dex (the development OIDC provider) must be reachable as `dex` in your browser for the OIDC
redirect to work correctly:

```bash
sudo sh -c 'echo "127.0.0.1 dex" >> /etc/hosts'
```

You only need to do this once.

---

## 4. Bootstrap Wizard

Open http://localhost:8080/admin in your browser.

If this is a fresh installation (empty database), you will be redirected to the Bootstrap Wizard.
Complete the following steps:

**Step 1 - Server Name:**
Enter a server name (e.g., `localhost`). This becomes part of all Matrix user IDs
(`@user:localhost`). It cannot be changed after setup without a full data migration.

**Step 2 - OIDC Provider:**
Enter the development Dex configuration:

| Field | Value |
|---|---|
| OIDC Issuer | `http://dex:5556/dex` |
| Client ID | `nebu-admin` |
| Client Secret | `nebu-admin-secret` |
| Role Claim Name | `nebu_role` |

**Step 3 - First Login:**
You will be redirected to Dex. Log in with one of the pre-configured dev users:

| Email | Password | Role |
|---|---|---|
| `kai@example.com` | `changeme` | `instance_admin` |
| `compliance@example.com` | `changeme` | `compliance_officer` |
| `alex@example.com` | `changeme` | `user` |

Log in as `kai@example.com` for the first admin setup.

After login, you will be redirected to the Admin Dashboard. Bootstrap mode is now permanently
disabled.

---

## 5. Connect a Matrix Client

### Element Web

1. Open https://app.element.io (or a self-hosted instance)
2. Click **Sign In** → **Edit** (to change server)
3. Under "Other homeserver", enter: `http://localhost:8008`
4. Click **Continue** → you will be redirected to Dex for SSO login
5. Log in with `alex@example.com` / `changeme`

You are now connected as a Matrix user on your local Nebu instance.

**Create a test room:** Click the `+` next to "Rooms" → give it a name → Create.

**Test messaging:** You can log in with a second account in a separate browser profile or incognito
window and join the same room.

---

## 6. Common make Targets

| Target | Description |
|---|---|
| `make setup` | Generate secrets and dev credentials (run once, then again after `make clean`) |
| `make dev` | Start full stack via docker compose |
| `make test-unit-elixir` | Run Elixir unit tests in container |
| `make test-integration` | Full stack + Playwright/Gherkin integration tests |
| `make build-server` | Compile Elixir app inside the build container (`mix compile`) |
| `make redeploy` | Rebuild the `server` Docker image and recreate the container |

---

## 7. Troubleshooting

### "Server not ready" or 502 errors on first start

**Cause:** The Elixir server takes ~30s to start (OTP release compilation + DB migrations).

**Fix:** Wait for the server health check to pass:
```bash
docker compose logs -f server | grep "Nebu.Application started"
```

---

### "dex: connection refused" during OIDC login

**Cause:** Missing `/etc/hosts` entry for `dex`.

**Fix:**
```bash
sudo sh -c 'echo "127.0.0.1 dex" >> /etc/hosts'
```
Then retry. If you are in a corporate VPN, the VPN may intercept DNS - disable VPN for local dev.

---

### Bootstrap Wizard does not appear; I see a login page

**Cause:** The database already has a `bootstrap_active=false` entry (previous setup).

**Fix:** Reset the database:
```bash
docker compose down -v   # removes volumes
make setup               # regenerate secrets
make dev
```

---

### "Unable to set up keys" or E2EE warnings in Element

**Expected behavior.** Nebu does not implement E2EE. The `keys/upload` and `keys/device_signing/upload`
endpoints return stubs that silence the dialog. If you see the dialog, try refreshing the page.
The UIA flow (m.login.dummy) should dismiss it automatically.

---


### PostgreSQL migration fails on startup

**Cause:** Database schema version mismatch (downgrade attempted, or `.secrets/` was regenerated
without clearing the database).

**Fix:**
```bash
docker compose down -v
make setup
make dev
```

_Source: `README.md`, §Quick Start; `CLAUDE.md`, §Commands; `_bmad-output/planning-artifacts/architecture.md`, §Build-Container-Strategie_

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

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