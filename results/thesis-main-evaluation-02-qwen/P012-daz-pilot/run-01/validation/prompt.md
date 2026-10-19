# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** DaZ-Pilot

**Description:** Digital language co-pilot for inclusive vocational school teaching: Learn specialist vocabulary via image recognition, pronunciation and quizzes.

## Supplied installation guide

## Guide: Installation.md

# Installation (On-Premises)

Runbook für die Erstinstallation von DaZ-Pilot auf einem Schulserver mit Docker Compose.

Für die Entwicklungsumgebung siehe [README.md](README.md#entwicklung). Dieses Dokument beschreibt ausschließlich den Produktivbetrieb.

## Inhaltsverzeichnis

- [Voraussetzungen](#voraussetzungen)
- [1. Repository klonen](#1-repository-klonen)
- [2. Secrets erzeugen](#2-secrets-erzeugen)
- [3. `.env` konfigurieren](#3-env-konfigurieren)
- [4. Reverse Proxy einrichten](#4-reverse-proxy-einrichten)
- [5. Stack starten](#5-stack-starten)
- [6. Funktionsprüfung](#6-funktionsprüfung)
- [7. Schule und Admin-Lehrkraft anlegen](#7-schule-und-admin-lehrkraft-anlegen)
- [8. Single Sign-On einrichten](#8-single-sign-on-einrichten)
- [9. Moodle anbinden](#9-moodle-anbinden)
- [10. Backups aktivieren](#10-backups-aktivieren)
- [Betrieb](#betrieb)
- [Fehlerbehebung](#fehlerbehebung)

---

## Voraussetzungen

| Anforderung | Wert                                                                    |
| ----------- | ----------------------------------------------------------------------- |
| Docker      | >= 24 mit Compose >= 2.20                                               |
| RAM         | 8 GB — der ML-Service hält das SigLIP-Modell (4,6 GB) im Speicher       |
| Festplatte  | 40 GB, davon 4,6 GB allein für die Modellgewichte im Volume             |
| Netz        | Zwei öffentliche DNS-Namen (API und Dashboard) mit TLS                   |
| Extern      | SMTP-Relay; optional Moodle ab 4.x mit aktivierter REST-API             |

Alle Dienste laufen in Containern. PostgreSQL, Qdrant und der ML-Service müssen nicht separat installiert werden. Node.js ist auf dem Server nicht nötig.

---

## 1. Repository klonen

```sh
git clone https://gitlab.opencode.de/sh/digitalhub-sh/landesprogramm-offene-innovationen/daz-pilot.git
cd daz-pilot
```

---

## 2. Secrets erzeugen

Vier Werte müssen erzeugt werden. Die Vorgabewerte in `.env.example` stehen öffentlich im Repository und sind für einen Produktivbetrieb unbrauchbar.

```sh
openssl rand -hex 48     # SUPER_ADMIN_API_KEY (min. 64 Zeichen)
openssl rand -base64 32  # SECRETS_ENCRYPTION_KEY
openssl rand -base64 32  # MEDIA_URL_SIGNING_KEY
openssl rand -hex 32     # DB_PASS
```

Zusätzlich das Schlüsselpaar für die Backup-Verschlüsselung erzeugen, idealerweise auf einem anderen Rechner:

```sh
age-keygen -o age-identity.txt
```

Die Zeile `# public key: age1…` in der Datei ist der Wert für `AGE_RECIPIENT`. Die Datei selbst wird nur zum Wiederherstellen gebraucht und gehört **nicht** auf den Anwendungsserver.

---

## 3. `.env` konfigurieren

```sh
cp .env.example .env
```

Diese Werte müssen gesetzt werden:

| Variable                                                  | Wert                                                  |
| --------------------------------------------------------- | ----------------------------------------------------- |
| `ENVIRONMENT`                                             | `production`                                          |
| `CORE_BACKEND_DOMAIN`                                     | Öffentliche API-URL, z. B. `https://api.schule.de`    |
| `FRONTEND_DOMAIN`                                         | Öffentliche Dashboard-URL, z. B. `https://daz.schule.de` |
| `NEXT_PUBLIC_CORE_BACKEND_DOMAIN`                         | Identisch mit `CORE_BACKEND_DOMAIN`                   |
| `SCHOOL_SLUG`                                             | Optional. On-Premise mit einer Schule: Kürzel, damit das Dashboard die Schulauswahl überspringt |
| `TRUST_PROXY`                                             | `1` bei einem Reverse Proxy, `2` bei zusätzlichem CDN |
| `AUTH_RATE_LIMIT_MAX`                                     | Höher als 60, wenn die Schule hinter einer NAT-IP sitzt |
| `DB_PASS`, `SUPER_ADMIN_API_KEY`, `SECRETS_ENCRYPTION_KEY`, `MEDIA_URL_SIGNING_KEY` | Werte aus Schritt 2 |
| `SMTP_*`                                                  | Zugangsdaten des Mailservers                          |
| `AGE_RECIPIENT`                                           | Öffentlicher age-Schlüssel aus Schritt 2              |

> `NEXT_PUBLIC_*`-Werte werden beim Image-Build in das Dashboard-Bundle kompiliert. Eine Änderung wirkt erst nach `docker compose build dashboard`. `SCHOOL_SLUG` gilt zur Laufzeit; nach einer Änderung reicht ein Neustart des Dashboard-Containers.

> `TRUST_PROXY` muss zur Zahl der Proxies passen. Ist der Wert zu niedrig, teilen sich alle Clients ein Rate-Limit; ist er zu hoch, lässt sich `X-Forwarded-For` fälschen.

Die Variablen `POSTGRES_PORT`, `ML_SERVICE_PORT`, `BACKEND_PORT` und `DASHBOARD_PORT` werden nur von `docker-compose.local.yml` gelesen und sind im Produktivbetrieb ohne Wirkung.

---

## 4. Reverse Proxy einrichten

`docker-compose.yml` veröffentlicht **keine** Host-Ports. Der Stack wird ausschließlich über einen Reverse Proxy erreichbar, der dem Compose-Netz beitritt und TLS terminiert.

| Öffentliche Domain    | Ziel im Compose-Netz |
| --------------------- | -------------------- |
| `CORE_BACKEND_DOMAIN` | `backend:4000`       |
| `FRONTEND_DOMAIN`     | `dashboard:3000`     |

Die API-Domain bedient dabei `/api/v1`, `/media` und `/.well-known` — sie darf nicht auf `/api` beschnitten werden, sonst finden die mobilen Apps ihre App-Links nicht.

Netzname ermitteln (Präfix ist der Compose-Projektname, in der Regel `daz-pilot`):

```sh
docker network ls | grep daz-pilot
```

Läuft der Proxy als eigener Container, muss er dem Netz beitreten:

```sh
docker network connect daz-pilot_default <proxy-container>
```

Beispiel für Caddy:

```caddyfile
api.schule.de {
	reverse_proxy backend:4000
}

daz.schule.de {
	reverse_proxy dashboard:3000
}
```

Der Proxy muss Uploads von Arbeitsaufträgen und Videos durchlassen. Bei nginx entsprechend `client_max_body_size` erhöhen (Standard sind 1 MB).

---

## 5. Stack starten

```sh
docker compose up -d --build
```

Das startet PostgreSQL, Qdrant, den ML-Service, die Datenbank-Migration, Backend, Worker, Dashboard und den Backup-Sidecar. Die Migration läuft als einmaliger Job vor dem Backend.

> Auf einem Rechner mit Node.js ist `npm run docker:up` die gleichwertige Kurzform.

> Der erste Start dauert lange: Der ML-Service lädt 4,6 GB SigLIP-Gewichte herunter und bleibt bis dahin `unhealthy`. Backend und Worker warten darauf. Fortschritt mit `docker compose logs -f ml-service` verfolgen.

---

## 6. Funktionsprüfung

```sh
docker compose ps
```

Alle Dienste müssen `healthy` sein, `migrate` muss `exited (0)` zeigen.

```sh
# API von außen
curl https://api.schule.de/api/v1/health

# Dashboard von außen
curl -I https://daz.schule.de
```

Die Swagger-UI liegt unter `https://api.schule.de/api/v1/swagger`.

---

## 7. Schule und Admin-Lehrkraft anlegen

Beide Schritte laufen über die Super-Admin-API mit dem Header `x-super-admin-api-key`.

Schule anlegen. Der Slug ist Teil aller Dashboard-URLs (Kleinbuchstaben, Ziffern und einzelne Bindestriche, 3–56 Zeichen):

```sh
curl -X POST https://api.schule.de/api/v1/school/create-one-school \
  -H "x-super-admin-api-key: $SUPER_ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "name": "Eckener-Schule Flensburg", "slug": "eckener-schule" }'
```

Erste Lehrkraft mit der Rolle `admin` anlegen. Sie richtet anschließend SSO, Moodle und weitere Konten im Dashboard ein:

```sh
curl -X POST https://api.schule.de/api/v1/teacher/create-one-teacher \
  -H "x-super-admin-api-key: $SUPER_ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
        "schoolSlug": "eckener-schule",
        "emailAddress": "admin@schule.de",
        "role": "admin",
        "firstName": "Vorname",
        "lastName": "Nachname"
      }'
```

Der Login ist danach unter `https://daz.schule.de/eckener-schule/login` erreichbar. Ohne konfiguriertes SSO läuft er über einen per E-Mail versandten Einmalcode — dafür muss `SMTP_*` funktionieren.

> Den Super-Admin-Key nur für diese Ersteinrichtung verwenden und nicht in Skripten oder Shell-History hinterlassen. Er umgeht jede Mandantentrennung.

---

## 8. Single Sign-On einrichten

DaZ-Pilot spricht OpenID Connect und liest die Endpunkte aus dem Discovery-Dokument des Identity Providers. Pro Schule werden zwei Clients gebraucht:

| Client    | Redirect-URI                                    |
| --------- | ----------------------------------------------- |
| Dashboard | `https://daz.schule.de/<schoolSlug>/login`      |
| App       | `https://api.schule.de/auth/oidc`               |

Die Zugangsdaten trägt die Admin-Lehrkraft im Dashboard unter **Konto → Verbindungen** ein. Client-Secrets werden mit `SECRETS_ENCRYPTION_KEY` verschlüsselt gespeichert.

Vollständige Anleitung inklusive der benötigten Claims: [OIDC_SETUP.md](OIDC_SETUP.md).

Damit der SSO-Rücksprung in der installierten App landet, müssen `UPLOAD_KEY_FINGERPRINT`, `PLAY_APP_SIGNING_FINGERPRINT` und `APPLE_APP_TEAM_ID` in `.env` gesetzt sein. Sonst endet der Callback im Browser.

---

## 9. Moodle anbinden

Optional. Ohne Moodle werden Arbeitsaufträge im Dashboard hochgeladen.

1. Plugin `local_oauth2` in Moodle installieren.
2. Ordner `infra/daz_bridge` nach `<moodle>/public/local/daz_bridge` kopieren (bei Moodle ohne `public/`-Verzeichnis nach `<moodle>/local/daz_bridge`) und `php admin/cli/upgrade.php` ausführen.
3. In Moodle unter **Website-Administration → Plugins → Lokale Plugins → DAZ Bridge** die Backend-URL (`CORE_BACKEND_DOMAIN`) und ein Shared Secret setzen (`openssl rand -hex 32`).
4. Dasselbe Shared Secret sowie Moodle-URL, OAuth2-Client-ID und -Secret im Dashboard unter **Konto → Verbindungen → Moodle-Konfiguration** hinterlegen.

Details: [infra/moodle/README.md](infra/moodle/README.md). Das dortige Compose-Setup ist eine Testumgebung und nicht für den Produktivbetrieb gedacht.

---

## 10. Backups aktivieren

Der `backup`-Service läuft mit dem Stack und sichert PostgreSQL, Qdrant und die Mediendateien im laufenden Betrieb, standardmäßig um 03:00 UTC. Ohne `AGE_RECIPIENT` beendet er sich sofort.

```sh
docker compose logs backup          # muss den Zeitplan melden, nicht abbrechen
docker compose run --rm backup backup.sh   # einmaliger Lauf zur Kontrolle
```

Die Archive liegen im Volume `backup_data` und müssen vom Server weg gesichert werden — ein Backup auf derselben Maschine überlebt deren Ausfall nicht.

Anleitung: [infra/backup/BACKUP.md](infra/backup/BACKUP.md), Wiederherstellung: [infra/backup/RESTORE.md](infra/backup/RESTORE.md).

---

## Betrieb

```sh
# Status und Logs
docker compose ps
docker compose logs -f backend

# Update auf einen neuen Stand
git pull
docker compose up -d --build

# Stack stoppen (Daten bleiben in den Volumes)
docker compose down
```

Ein Update baut die Images neu und lässt die Migration erneut laufen. Vorher ein Backup ziehen.

> `docker compose down -v` löscht alle Volumes und damit Datenbank, Vektorindex und Mediendateien.

---

## Fehlerbehebung

| Symptom                                                        | Ursache                                                                                        |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `ml-service` dauerhaft `unhealthy`                             | Modell-Download nicht abgeschlossen oder abgebrochen; Logs prüfen, Plattenplatz für `ml_model_cache` |
| `backend` startet nicht, `EACCES … /app/media/_upload_tmp`     | `media_data` gehört root; Volume nach der Anleitung im [Backend-README](backend/README.md#non-root-betrieb-und-media_data) umstellen |
| Dashboard lädt, aber jeder API-Aufruf schlägt fehl             | `FRONTEND_DOMAIN` passt nicht zur aufgerufenen Domain (CORS) oder `NEXT_PUBLIC_CORE_BACKEND_DOMAIN` wurde nach dem Build geändert |
| Login-Code kommt nicht an                                      | `SMTP_*` falsch; `docker compose logs backend` zeigt den Fehler des Mailservers                 |
| Rate-Limit greift für eine ganze Klasse                        | `TRUST_PROXY` zu niedrig, dadurch teilen alle Clients eine IP; danach `AUTH_RATE_LIMIT_MAX` erhöhen |
| `oidcNotConfigured` beim SSO-Login                             | Für die Schule sind Issuer-URL oder Client-Zugangsdaten nicht hinterlegt                        |
| `userNotWhitelisted` beim SSO-Login                            | Es existiert keine Lehrkraft bzw. kein:e Schüler:in mit dieser E-Mail-Adresse in der Schule     |
| `backup` beendet sich direkt nach dem Start                    | `AGE_RECIPIENT` fehlt in `.env`                                                                |

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

Installed the DaZ-Pilot production stack with Docker Compose in the shared workspace `/workspace` (repo already checked out at commit `ba32aab`, so step 1 "clone" was a no-op).

Prereqs: Docker 29.7.2, Compose v5.5.0, 8 CPUs, ~7.6 GB RAM, ~952 GB disk. Installed the host `age` tool via apt to run `age-keygen`.

Secrets (step 2): generated `SUPER_ADMIN_API_KEY` (openssl rand -hex 48), `SECRETS_ENCRYPTION_KEY` and `MEDIA_URL_SIGNING_KEY` (openssl rand -base64 32), `DB_PASS` (openssl rand -hex 32), and an age keypair `age-keygen -o age-identity.txt`.

`.env` (step 3): wrote `/workspace/.env` (chmod 600) from the .env.example layout with `ENVIRONMENT=production`, `SCHOOL_SLUG=eckener-schule`, `TRUST_PROXY=1`, `AUTH_RATE_LIMIT_MAX=300`, `AGE_RECIPIENT` (age public key), `SMTP_*` pointing at the local relay, and all generated secrets. Because this sandbox has no public DNS names/TLS, `CORE_BACKEND_DOMAIN=http://localhost:4000` and `FRONTEND_DOMAIN=http://localhost:3000` were used (the guide's reverse-proxy step is not feasible here).

Build & start (step 5): `docker compose up -d --build`. First run built all images (backend, dashboard, ml-service, backup) and started postgres/qdrant/migrate/backup/ml-service; it then aborted with "dependency ml-service failed to start" because the one-time 4.6 GB SigLIP model download (HF google/siglip2-so400m-patch14-384) exceeded the 300 s health start_period — the exact "first start is long / ml-service stays unhealthy" behavior the guide documents. After the download finished and `ml-service` reported healthy, re-ran `docker compose up -d` to start `migrate`, `backend`, `worker`, `dashboard`. migrate ran the 001–009 migrations and exited 0.

Verification (steps 6/7/10): all long-running services `healthy`, `migrate` `exited (0)`. `GET /api/v1/health` on backend:4000 → `{"status":"pass","healthCheckResults":[{"status":"pass","message":"Database is healthy"...}]}`. Dashboard `/` → HTTP 200 and `/eckener-schule/login` → HTTP 200 (SCHOOL_SLUG school-skip works). Swagger UI served under `/api/v1/swagger`. School `eckener-schule` ("Eckener-Schule Flensburg") and admin teacher `admin@schule.de` created via the super-admin API (`x-super-admin-api-key`), both HTTP 201, confirmed in Postgres `schools`/`teachers`. Backup sidecar logs its supercronic schedule (does not exit). A one-off `docker compose run --rm backup backup.sh` completed and wrote age-encrypted archives (`.age` files begin with `age-encryption.org/v1`) for postgres/qdrant/media.

Additional end-to-end check: stood up a local SMTP relay container on the compose network (alias `mailcatcher`), then verified the no-SSO login loop: `POST /api/v1/auth/init-email-login` → OTP email delivered through the relay (code visible in the relay log) → `POST /api/v1/auth/complete-email-login` → HTTP 201 with a teacher session. Test teachers created for this check were removed afterward, leaving only `admin@schule.de`.

Not done (environment-limited, not failures): the reverse proxy (no public DNS/TLS available in this sandbox; documented internal targets validated directly), SSO/IdP (step 8) and Moodle (step 9), both optional/follow-on admin tasks needing external systems absent here.

Access point: dashboard login at `http://localhost:3000/eckener-schule/login` (admin@schule.de, role admin). Start command: `docker compose up -d` from `/workspace`. Volumes: workspace_{postgres_data,qdrant_storage,qdrant_snapshots,ml_model_cache,media_data,backup_data}.

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