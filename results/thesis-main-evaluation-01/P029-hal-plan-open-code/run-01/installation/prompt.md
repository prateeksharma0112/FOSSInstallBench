# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** HAL-Plan Open Code

**Project description:** HAL-Plan is a digital twin for the areas of urban development and strategic land management.

**Installation guide:**

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
