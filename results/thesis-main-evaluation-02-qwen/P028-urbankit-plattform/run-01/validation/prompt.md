# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** UrbanKIT Plattform

**Description:** A city's digital citizen participation platform: public portal plus closed project workspace with modular tools.

## Supplied installation guide

## Guide: Installation.md

# Deployment

Docker Compose with three services (see `docker-compose.yml`):

| Service | Image / build | Host port | Notes |
|---|---|---|---|
| `web` | `Dockerfile` | `127.0.0.1:3020` | runs `next start` directly (no migrations — Mongo is schemaless) |
| `hocuspocus` | `hocuspocus/Dockerfile` | `127.0.0.1:1234` | realtime sidecar for the Board module |
| `mongo` | `mongo:7` | `127.0.0.1:27019` | volume `mongo_data` |

Media uploads live on the `media_data` volume (`/app/media`) — no external
object storage.

## Setup

```bash
cp .env.example .env
# set at minimum: PAYLOAD_SECRET, HOCUSPOCUS_SECRET, NEXT_PUBLIC_HOCUSPOCUS_URL,
# NEXT_PUBLIC_SERVER_URL  (see docs/env-reference.md)

docker compose up -d --build
docker compose ps          # wait for healthy
curl http://localhost:3020/api/health
```

Compose fails fast on missing required vars (`:?` syntax) — intentional.

**Build-time args:** `NEXT_PUBLIC_SERVER_URL` and `NEXT_PUBLIC_HOCUSPOCUS_URL`
are baked into the client bundle at build time (Docker build args). Changing
them requires a rebuild, not just a restart.

## Domains

One deployment serves both hosts; `src/middleware.ts` splits them (see
[architecture.md](./architecture.md)):

- `urbankit.de` → public portal
- `app.urbankit.de` → logged-in workspace

Point both DNS records at the same server. The board WebSocket needs its own
public endpoint: set `NEXT_PUBLIC_HOCUSPOCUS_URL` to a `wss://` URL (e.g.
`wss://ws.urbankit.de`) proxied to port 1234 — plain `ws://` is blocked as
mixed content on https pages.

### Nginx sketch

```nginx
# portal + app → next
server {
    listen 443 ssl;
    server_name urbankit.de app.urbankit.de;
    location / {
        proxy_pass http://127.0.0.1:3020;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# board websocket
server {
    listen 443 ssl;
    server_name ws.urbankit.de;
    location / {
        proxy_pass http://127.0.0.1:1234;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

`Host` must be forwarded unchanged — the middleware's domain routing and the
login "open workspace in new tab" flow depend on it.

## Production override

Same pattern as the urban-kit-methodensammlung stack: `docker-compose.prod.yml`
hardens the base compose for the VPS.

```bash
# additionally set in .env: MONGO_ROOT_USER, MONGO_ROOT_PASSWORD
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

What it changes:

- **MongoDB root auth** — `MONGO_INITDB_ROOT_*` creates the root user on first
  boot, `web` connects with a credentialed `DATABASE_URI` (`authSource=admin`).
  NOTE: init only applies to an EMPTY `mongo_data` volume. For an existing
  volume, create the user once by hand:
  `docker compose exec mongo mongosh --eval 'db.getSiblingDB("admin").createUser({user: "…", pwd: "…", roles: ["root"]})'`
- Mongo publishes **no host port** at all (base maps `127.0.0.1:27019`).
- `restart: always` for web/hocuspocus/mongo.
- The **mailpit** dev mailcatcher is parked behind a compose profile and never
  starts — point `SMTP_*` at a real provider.

## Backup & restore

`scripts/backup.sh` dumps the database (`mongodump --archive --gzip`) and tars
the `media_data` + `uploads_data` volumes into `../backups/` (rotating after 14
days). Run it from cron on the server:

```cron
30 3 * * * /root/projects/urban-kit-plattform/urban-kit-plattform/scripts/backup.sh \
           >> /root/projects/urban-kit-plattform/backups/backup.log 2>&1
```

Restore a DB archive (drops and replaces the current database):

```bash
scripts/restore.sh ../backups/db_2026-08-20_0330.archive.gz
```

Both scripts read `MONGO_ROOT_USER`/`MONGO_ROOT_PASSWORD` from `.env`.

## Updates

```bash
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build web hocuspocus
```

## Demo accounts (public prototype logins)

Two read-only test accounts (citizen + project lead) can be shown on the login
page while the prototype notice is on:

```bash
docker compose exec web npm run seed:demo          # defaults, see script header
DEMO_PROJECT_SLUG=… DEMO_PASSWORD=… docker compose exec -e DEMO_PROJECT_SLUG -e DEMO_PASSWORD web npm run seed:demo
```

The script flags the users `isDemo`, puts them into the project and fills
`platform-settings.prototypeDemoAccounts` (only if empty). Writes from these
accounts are refused platform-wide; the board is read-only (the `hocuspocus`
image must be rebuilt after updating — it sets `connection.readOnly`).

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

**Method:** Primary documented path — `cp .env.example .env`, set required vars, `docker compose up -d --build` in /workspace (Ubuntu 22.04 dind sandbox, WSL2 host, Docker 29.7.2, Compose v5.5.0).

**Environment setup:** Created `/workspace/.env` from `.env.example`; generated random `PAYLOAD_SECRET`/`HOCUSPOCUS_SECRET` (openssl rand -hex 32), kept default `NEXT_PUBLIC_HOCUSPOCUS_URL=ws://localhost:1234`, set `NEXT_PUBLIC_SERVER_URL=http://localhost:3020` (matching the published host port).

**Build:** `docker compose up -d --build` built the `web` image (Next.js 15.4.11 multi-stage: deps → builder with `npm run generate:types`, `generate:importmap`, `next build` → runner with volumes pre-created nextjs-owned) and the `hocuspocus` image (node:22-alpine, `npm install --omit=dev`); pulled `mongo:7` and `axllent/mailpit`.

**Environment obstacle + workaround:** All container creation initially failed: `runc create failed: ... cannot enter cgroupv2 "/sys/fs/cgroup/docker" with domain controllers -- it is in threaded mode`. Root cause: the sandbox itself runs in a cgroup namespace whose root cgroup (`/proc/self/cgroup` = `0::/docker`) is in cgroup-v2 "threaded" mode; minimal-test bisection showed `docker run --rm busybox true` succeeds while `docker run --rm --memory 1g busybox true` fails with the identical error — runc cannot write cgroup limit files in that state, and the compose files set `deploy.resources.limits.memory` on every service. Attempts to clear threaded mode (`echo 0 > cgroup.threads`) were silent no-ops from inside the namespace. Workaround: local-only override file `/workspace/docker-compose.noresources.yml` (same multi-file pattern as the guide's prod setup) with `deploy: !reset null` for all four services, started via `docker compose -f docker-compose.yml -f docker-compose.noresources.yml up -d`.

**Final state (running, loopback-only):**
- `workspace-web-1` — Up (healthy), 127.0.0.1:3020 → container :3000
- `workspace-hocuspocus-1` — Up, 127.0.0.1:1234 (board WebSocket, Hocuspocus v2.15.3 "Ready.")
- `workspace-mongo-1` — Up (healthy), 127.0.0.1:27019 → :27017
- `workspace-mailpit-1` — Up (healthy), 127.0.0.1:1025/8025 (dev mailcatcher)

**Known access points:** portal `http://localhost:3020` (Host: urbankit.de → /de), workspace login (Host: app.urbankit.de → /de/login), health `http://localhost:3020/api/health`, board WS `ws://localhost:1234`. To re-run the stack: `cd /workspace && docker compose -f docker-compose.yml -f docker-compose.noresources.yml up -d`.

**Not done (documented as optional/VPS-only):** production override `docker-compose.prod.yml` (Mongo root auth, un-published Mongo port, `restart: always`), demo-account seeding (`npm run seed:demo`), backup/restore scripts, external nginx/TLS for the urbankit.de domains — all out of scope for the base install in this environment.

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