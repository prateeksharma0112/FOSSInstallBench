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

Installed the gitlab-profile (KommunalEnergie) application in /workspace using the prebuilt-image Docker Compose method from the installation guide. Docker Engine 29.7.2 and Compose v5.5.0 were preinstalled. Created /workspace/.env from .env.example and set API_CREDENTIAL_ENCRYPTION_KEY (openssl rand -base64 32), APP_DOMAIN=localhost, INITIAL_ADMIN_PASSWORD, SWAGGER_HTTP_AUTH_PASSWORD, and LETSENCRYPT_EMAIL. The OpenCode registry (registry.opencode.de) allowed anonymous pulls, so no docker login was required. Ran `docker compose pull` (success) and `docker compose up -d`. PostgreSQL initialized the base schema via sql/base_model.sql, and the web entrypoint applied 25 Yii migrations ("Migrated up successfully") before starting Apache. All four containers run: web (yii2_vue_dash_container), postgres (postgres_dashapp_container, healthy), traefik (traefik_proxy_container, 80/443) and iothubsh-adapter. Verified endpoints: https://localhost/ -> 200 (login page), /administration -> 200 (login), /administration/docs/ -> 401 then 200 with Basic auth admin:swaggerpass123, POST /api/v1/node/measurements -> 400 application validation error confirming the route is live. The local TLS cert is Traefik's self-signed default since Let's Encrypt cannot issue for localhost; curl -k was used. This is the final method used; the alternative documented method (local build via docker-compose.build.yml) was not attempted because the prebuilt-image method succeeded.

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