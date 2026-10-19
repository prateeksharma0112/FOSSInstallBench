# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** DaZ-Pilot

**Project description:** Digital language co-pilot for inclusive vocational school teaching: Learn specialist vocabulary via image recognition, pronunciation and quizzes.

**Installation guide:**

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
