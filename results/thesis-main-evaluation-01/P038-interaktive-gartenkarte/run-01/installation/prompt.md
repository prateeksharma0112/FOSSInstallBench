# ROLE

You are an autonomous software agent responsible for carrying out a software installation task.

# TASK

Install the assigned software and report the outcome based on objective evidence.

# INPUTS

**Project name:** Interaktive Gartenkarte

**Project description:** Interactive web application for visualizing live sensor data (LoRaWAN) in the Ochsenfurt climate garden on a graphic map.

**Installation guide:**

## Guide: Installation.md

# Installation

## Voraussetzungen

| Software | Mindestversion |
|---|---|
| PHP | 8.2 |
| Composer | 2 |
| Node.js | 22 |
| npm | aktuell |

Benötigte PHP-Extensions (bei den meisten Distributionen standardmäßig aktiv):

- `ext-sqlite3` (oder den Treiber der gewählten Datenbank)
- `ext-mbstring`
- `ext-xml`
- `ext-curl`
- `ext-fileinfo`

Prüfbar mit `php -m`. Unter Ubuntu/Debian z. B.: `sudo apt install php8.2-sqlite3 php8.2-mbstring php8.2-xml php8.2-curl`.

---

## Lokales Dev-Setup

```bash
# 1. Repository klonen
git clone https://gitlab.opencode.de/wuerzburg/heimatforum/mitmachgarten.git
cd mitmachgarten

# 2. PHP-Abhängigkeiten installieren
composer install

# 3. Umgebungsdatei anlegen und App-Key generieren
cp .env.example .env
php artisan key:generate

# 4. Datenbank anlegen (SQLite, Standard-Konfiguration von Laravel)
mkdir -p database && touch database/database.sqlite
php artisan migrate

# 5. JS-Abhängigkeiten installieren
npm install

# 6. Alles starten (Backend, Queue, Logs, Vite)
composer dev
```

Die Anwendung ist dann unter http://localhost:8000 erreichbar.
Frontend-Assets werden von Vite (http://localhost:5173) bereitgestellt und automatisch eingebunden.

> **Alternativ** können Backend und Frontend auch einzeln in separaten Terminals gestartet werden:
> ```bash
> php artisan serve   # Terminal 1
> npm run dev         # Terminal 2
> ```

Sensordaten werden live von [opendata.wuerzburg.de](https://opendata.wuerzburg.de) geladen – eine Internetverbindung ist erforderlich. Es gibt keine lokalen Demo-Daten; alle Messwerte kommen direkt von der öffentlichen API.

### Alternative: Laravel Herd oder Valet

Wer [Laravel Herd](https://herd.laravel.com) oder Valet verwendet, überspringt `php artisan serve` – der PHP-Server wird von Herd/Valet übernommen.

```bash
# Projekt in Herd verlinken und PHP-Version setzen
herd link interaktive-gartenkarte
herd isolate 8.2 --site=interaktive-gartenkarte   # oder höher (8.3, 8.4)
```

Wichtig: `APP_URL` in der `.env` muss auf die lokale Domain gesetzt werden, z. B.:

```
APP_URL=http://interaktive-gartenkarte.test
```

Der Vite-Dev-Server (`npm run dev`) wird weiterhin separat benötigt.

---

## Produktions-Deployment (ohne Docker)

```bash
# Abhängigkeiten (ohne Dev-Pakete)
composer install --no-dev --optimize-autoloader

# Frontend bauen
npm ci && npm run build

# Umgebung konfigurieren
cp .env.example .env
# .env anpassen: APP_ENV=production, APP_DEBUG=false, APP_KEY=..., DB_*

php artisan key:generate
php artisan migrate --force

# Caches aufbauen
php artisan config:cache
php artisan route:cache
php artisan view:cache
```

Webserver-Konfiguration: Document Root auf `public/` zeigen lassen. Beispielkonfigurationen für nginx und Apache sind in der [Laravel-Dokumentation](https://laravel.com/docs/deployment) zu finden.

---

## Umgebungsvariablen

Alle Konfigurationsoptionen werden über die `.env`-Datei gesetzt. Vollständige Beschreibung: [docs/CONFIGURATION.md – Umgebungsvariablen](docs/CONFIGURATION.md#umgebungsvariablen).

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
