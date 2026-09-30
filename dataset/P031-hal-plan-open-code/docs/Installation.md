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
