# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** UrbanKIT Plattform

**Project description:** A city's digital citizen participation platform: public portal plus closed project workspace with modular tools.

**Installation guide:**

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
