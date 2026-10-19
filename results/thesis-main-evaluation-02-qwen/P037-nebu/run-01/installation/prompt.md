# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** Nebu

**Project description:** Enterprise-ready, Matrix-compatible chat server - Apache 2.0, SSO-ready, horizontally scalable.

**Installation guide:**

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
