# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** HAL-Plan Open Code

**Description:** HAL-Plan is a digital twin for the areas of urban development and strategic land management.

## Supplied installation guide

## Guide: Installation.md

# Installation

> How to set up Buildplace for local development using Docker or a manual setup.

## Prerequisites

Before installing Buildplace, ensure you have:

- **Node.js 24** — [Download](https://nodejs.org/) or use `nvm`
- **pnpm** — `npm install -g pnpm`
- **Docker** — [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine
- **Git** — for cloning the repository

## Option 1: Dev Containers (Recommended)

The fastest way to get started. Dev Containers use Docker Compose to automatically set up PostGIS, Valkey, and a development container with all dependencies.

1. **Install VS Code Extensions**

   Install the **Dev Containers** extension (`ms-vscode-remote.remote-containers`).

2. **Clone the repository**

   ```bash
   git clone https://github.com/formfollowsyou/buildplace-opencode.git
   cd buildplace-opencode
   ```

3. **Open in Dev Container**

   Press `Ctrl+Shift+P` → run **Dev Containers: Reopen in Container**.

   This sets up:
   - PostgreSQL 15 with PostGIS extension (port 5432)
   - Valkey for PubSub/Caching (port 6379)
   - Valkey for BullMQ job queue (port 6380)
   - Node.js 24 development environment

4. **Initialize the database**

   ```bash
   pnpm setupDb
   ```

5. **Start the development server**

   ```bash
   pnpm dev:init
   ```

   This runs `pnpm install`, `pnpm prisma generate`, `pnpm codegen`, `pnpm prisma migrate reset`, and starts the dev server.

## Option 2: Manual Setup

### Step 1: Set up PostgreSQL with PostGIS

Pull and run the PostGIS Docker image:

```bash
docker pull postgis/postgis
docker run --name postgis -d -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgrespw \
  postgis/postgis
```

Or use Docker Desktop: search for `postgis/postgis`, click Run, set port to `5432` and environment variable `POSTGRES_PASSWORD` to `postgrespw`.

### Step 2: Set up Valkey (Redis-compatible)

You need **two** Valkey instances with different eviction policies:

```bash
# Instance 1: PubSub and Caching (allkeys-lru)
docker run --name valkey-cache -d -p 6379:6379 valkey/valkey

# Instance 2: BullMQ job queue (noeviction)
docker run --name valkey-queue -d -p 6380:6379 valkey/valkey
```

### Step 3: Clone and install dependencies

```bash
git clone https://github.com/formfollowsyou/buildplace-opencode.git
cd buildplace-opencode
pnpm install
```

### Step 4: Configure environment variables

Copy the defaults and adjust for your setup:

```bash
cp .env.defaults .env
```

At minimum, configure these in `.env`:

```bash
# Database
DATABASE_URL=postgres://postgres:postgrespw@localhost:5432/ffy_dev
TEST_DATABASE_URL=postgres://postgres:postgrespw@localhost:5432/ffy_test
SHADOW_DATABASE_URL=postgres://postgres:postgrespw@localhost:5432/ffy_shadow

# Valkey
VALKEY_SERVER=localhost
VALKEY_PORT=6379
VALKEY_PERSISTENT_SERVER=localhost
VALKEY_PERSISTENT_PORT=6380

# Session (generate random values)
SESSION_KEY=<32-byte-hex>

# Storage (MinIO or S3-compatible)
STORAGE_BUCKET=dev
STORAGE_URL=storage.example.com
STORAGE_KEY=<your-key>
STORAGE_SECRET=<your-secret>

# Core
CRYPTO_SECRET=<random-string>
WEBAPP_DEV_USER_PW=<dev-password>
```

### Step 5: Initialize the database

```bash
pnpm setupDb
pnpm prisma generate
pnpm prisma migrate reset
```

### Step 6: Generate GraphQL types and start

```bash
pnpm codegen
pnpm dev
```

Open localhost:3000.

## Verifying the Installation

After starting the dev server, you should see:

- The Buildplace application at localhost:3000
- The GraphQL playground (if enabled)
- A 3D map view with terrain and buildings
- Working authentication (login with your configured dev user)

If something doesn't work, check:
- PostgreSQL is running and accessible on port 5432
- Both Valkey instances are running on ports 6379 and 6380
- The `.env` file has correct connection strings
- Run `pnpm prisma migrate status` to verify database migrations

## Next Steps

- [Configuration reference](/deployment/configuration)
- [Understand the architecture](/architecture/overview)

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

## HAL-Plan / Buildplace — Installation Summary

**Context:** Ubuntu 22.04 container, working directory `/workspace` (repository already checked out at target SHA). Docker Engine 29.7.2 present; no Node/pnpm preinstalled. Method used: **Manual Setup (Option 2)** from the guide, supplemented by repo `.env.defaults`, `scripts/setupDb.ts`, and `.devcontainer/` files. The Dev Containers method (Option 1) was not used because it requires the VS Code Dev Containers extension/UI.

**Prerequisites installed:**
- Node.js 24.15.0 → `https://nodejs.org/dist/v24.15.0/node-v24.15.0-linux-x64.tar.xz`, extracted to `/usr/local` (`node`, `npm` now in PATH).
- pnpm 11.2.2 → `npm install -g pnpm@11.2.2`.

**Backing services (Docker containers, running):**
- `postgis` — `postgis/postgis:17-3.5`, `0.0.0.0:5432->5432`, `POSTGRES_USER=postgres`, `POSTGRES_PASSWORD=postgrespw`, `POSTGRES_DB=ffy_dev`.
- `valkey-cache` — `valkey/valkey:8.1.4`, `0.0.0.0:6379->6379`, `maxmemory-policy allkeys-lru`.
- `valkey-queue` — `valkey/valkey:8.1.4`, `0.0.0.0:6380->6379`, `maxmemory-policy noeviction`, appendonly.

**Repository setup (in `/workspace`):**
- `cp .env.defaults .env`, then edited `.env`: generated random `SESSION_KEY` and `CRYPTO_SECRET` (32-byte hex via Node crypto), set `WEBAPP_DEV_USER_PW=devpassword123`, appended `VALKEY_PERSISTENT_SERVER=localhost` and `VALKEY_PERSISTENT_PORT=6380`.
- `pnpm install` (success, ~2m52s).
- `pnpm prisma generate` (Prisma client + Pothos types).
- `pnpm setupDb` → created databases `ffy_shadow`, `ffy_test` (ffy_dev created by container).
- `pnpm prisma migrate reset --force` → applied 7 migrations and ran the seed.
- `pnpm codegen` → generated GraphQL types and gql-tada output.
- Copied `web-ifc` wasm files into `web/public/web-ifc/` (per `.devcontainer/setup.sh`).

**Startup / access:**
- Start command: `pnpm dev` (currently running in background; log at `/tmp/dev.log`).
- App URL: http://localhost:3000 (HTTP 200). GraphQL endpoint at `http://localhost:3000/api/graphql`. Dev inspector on 127.0.0.1:9229.

**State:** Fully installed and running. No incomplete work in the documented dev path. Production build (`pnpm build`/`pnpm start`) was not exercised.

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