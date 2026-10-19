# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** gitlab-profile

**Description:** Web-based application for the collection, management and evaluation of energy data from public properties.

## Supplied installation guide

## Guide: Installation.md

# Setup

## 1. Voraussetzungen

Installiere Docker Engine mit dem Compose-Plugin nach der offiziellen
[Docker-Dokumentation](https://docs.docker.com/engine/install/). Für den Betrieb
ohne dauerhaftes `sudo` kann ein dedizierter Benutzer Mitglied der Gruppe
`docker` werden:

```bash
sudo adduser deploy
sudo usermod -aG docker deploy
su - deploy
docker ps
```

## 2. Repository und Konfiguration

```bash
git clone https://gitlab.opencode.de/sh/digitalhub-sh/landesprogramm-offene-innovationen/kommunalenergie/gitlab-profile.git
cd gitlab-profile
cp .env.example .env
```

Passe mindestens Passwörter, Cookie-Validierungsschlüssel, Domain und
Let's-Encrypt-E-Mail in `.env` an. `SWAGGER_HTTP_AUTH_PASSWORD` schützt die
interaktive API-Dokumentation mit dem Benutzernamen `admin`. Erzeuge außerdem
den dauerhaft aufzubewahrenden Schlüssel für die Verschlüsselung der API-Secrets:

```bash
sed -i "s|^API_CREDENTIAL_ENCRYPTION_KEY=.*|API_CREDENTIAL_ENCRYPTION_KEY=$(openssl rand -base64 32)|" .env
```

Ein späterer Austausch dieses Schlüssels macht bestehende App-Credentials
unbrauchbar; diese müssen dann rotiert werden. Für produktive Installationen sollten
`WEB_IMAGE` und `IOTHUBSH_ADAPTER_IMAGE` auf denselben Release- oder Commit-Tag
festgelegt werden.

Falls die Container Registry eine Anmeldung verlangt:

```bash
docker login registry.opencode.de
```

## 3. Start mit Docker Compose

```bash
docker compose pull
docker compose up -d
docker compose ps
```

Beim ersten Start initialisiert PostgreSQL das Basisschema automatisch. Danach
führt der Webcontainer alle ausstehenden Yii-Migrationen aus und startet Apache
erst nach deren erfolgreichem Abschluss.

Die Startprotokolle können wie folgt verfolgt werden:

```bash
docker compose logs -f web postgres
```

## 4. Erreichbarkeit

Das Webinterface ist unter der in `APP_DOMAIN` angegebenen Domain erreichbar.
Die Administration befindet sich unter `https://APP_DOMAIN/administration`.
Das initiale Administrationskonto heißt `admin`; sein Kennwort wird nur bei der
Erstellung eines leeren Datenbank-Volumes aus `INITIAL_ADMIN_PASSWORD` gelesen.
Die Swagger UI unter `https://APP_DOMAIN/administration/docs/` verwendet ebenfalls
den Benutzernamen `admin`, aber das bei jedem Containerstart neu eingelesene
`SWAGGER_HTTP_AUTH_PASSWORD`.

Der Endpunkt zur Erfassung von Messdaten liegt unter
`https://APP_DOMAIN/api/v1/node/measurements`. Weitere Angaben stehen im Ordner
`docs/`.

## Updates

```bash
docker compose pull
docker compose up -d --remove-orphans
docker compose logs -f web
```

Auch bei Updates werden Migrationen automatisch vor dem Webserver ausgeführt.
Für reproduzierbare Rollbacks sollte in `.env` ein unveränderlicher Release-
oder Commit-Tag statt `latest` verwendet werden.

## Lokale Images bauen

Für Entwicklung oder Tests können beide Images aus dem Checkout gebaut werden:

```bash
docker compose -f docker-compose.yml -f docker-compose.build.yml up -d --build
```

## Datenbank sichern und wiederherstellen

```bash
docker compose exec -T postgres pg_dump -U yii2_user yii2_db > backup.sql
docker compose exec -T postgres psql -U yii2_user -d yii2_db -v ON_ERROR_STOP=1 < backup.sql
```

Passe Benutzer und Datenbanknamen an die Werte aus `.env` an.

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

**Method used:** Default method from the guide — pull pre-built images from `registry.opencode.de` (no login required; `docker compose pull` exited 0) and start with `docker compose up -d`. The local-build alternative (`docker-compose.build.yml`) was not needed.

**Environment/working directory:** Docker 29.7.2 + Compose v5.5.0 already present. Repository pre-checked out at `/workspace` (commit `6f9c4ea`). All compose commands run as root from `/workspace`.

**Configuration (`/workspace/.env`, created from `.env.example` per guide):**
- `API_CREDENTIAL_ENCRYPTION_KEY` generated with `openssl rand -base64 32` via the guide's exact `sed` command.
- `DB_PASSWORD`, `INITIAL_ADMIN_PASSWORD`, `SWAGGER_HTTP_AUTH_PASSWORD`, `FRONTEND_COOKIE_VALIDATION_KEY`, `BACKEND_COOKIE_VALIDATION_KEY` randomized with openssl (guide requires adapting passwords/cookie keys).
- `APP_DOMAIN=localhost`, `LETSENCRYPT_EMAIL=admin@localhost` (no public domain available in the sandbox).
- `TRAEFIK_TLS_CERTRESOLVER` set empty (documented local-development option in `.env.example`) so Traefik does not run a dead Let's Encrypt resolver.

**Startup state:** `docker compose up -d` exited 0. `docker compose ps` shows all 4 services Up: `postgres_dashapp_container` (healthy), `traefik_proxy_container` (ports 80/443 published), `yii2_vue_dash_container` (web, image `registry.opencode.de/.../gitlab-profile:latest`), `iothubsh_adapter` (uvicorn, image `.../gitlab-profile/iothubsh-adapter:latest`). Named volumes created: `workspace_db_data`, `workspace_yii2-uploaded-files`, `workspace_yii2-system-assets`, `workspace_letsencrypt_data`, `workspace_iothubsh-adapter-data`.

**Observed startup:** Web container log shows PostgreSQL base schema init, "25 migrations were applied. Migrated up successfully.", then Apache "resuming normal operations" (Apache 2.4.68).

**Access points (per guide, with sandbox caveats):**
- Traefik on host :80/:443 routes on `Host: APP_DOMAIN` (here `localhost`); HTTP router correctly issues 301 → `https://localhost/`. TLS termination for `localhost` has no certificate (resolver disabled), so HTTPS via Traefik is not usable in the sandbox; this is an environment limitation, not an install defect.
- Web app verified directly inside the web container: `GET /` → 200; administration at `/administration` (initial account `admin`, password from `INITIAL_ADMIN_PASSWORD` read at init — confirmed `admin` row in `backendusers`); Swagger at `/administration/docs/` → 401 without credentials, 200 with `admin:<SWAGGER_HTTP_AUTH_PASSWORD>`; measurements API `POST /api/v1/node/measurements` → 400 with valid Yii validation error body (endpoint live, requires Bearer credential + non-empty `measurements` array per `docs/`).
- iothubsh-adapter: uvicorn up on :8000, `/docs` and `/openapi.json` → 200; webhook routes (`/webhook/config`, `/webhook/measurement`) proxied by Traefik on the APP_DOMAIN host (301 observed, same TLS caveat).

**No incomplete work.** Stack is left running. Known access commands: `docker compose logs -f web postgres`, `docker compose exec -T postgres psql -U yii2_user -d yii2_db`.

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