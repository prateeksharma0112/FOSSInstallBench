# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** Interaktive Gartenkarte

**Description:** Interactive web application for visualizing live sensor data (LoRaWAN) in the Ochsenfurt climate garden on a graphic map.

## Supplied installation guide

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

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

## Environment & context
- Ubuntu 22.04.5 LTS container, root user, shared workspace at `/workspace` containing the project repo checked out at commit `7edb795` (detached HEAD = `main`, remote `https://gitlab.opencode.de/wuerzburg/heimatforum/mitmachgarten.git`, shallow clone with merge parents stripped).
- No PHP, Composer, Node, or npm were preinstalled; only git 2.34.1 was present.

## Prerequisites installed
- PHP 8.2.34 first (apt, ondrej/php PPA) with extensions `php8.2-{sqlite3,mbstring,xml,curl,zip,intl,gd}`; `composer install` then failed because `composer.lock` pins `symfony/*` v8.0.x packages requiring `php >=8.4`. Reinstalled PHP 8.4.26 with the same extensions and set it as the default `php` via `update-alternatives` (the guide's Herd section explicitly allows "8.3, 8.4 oder höher"). `php -m` confirmed sqlite3, mbstring, xml, curl, fileinfo.
- Composer 2.10.3 via the official installer (`getcomposer.org/installer`, binary at `/usr/local/bin/composer`). A direct download of a hard-coded phar version had failed (wrong version → HTML response); the official installer was used instead.
- Node.js v22.23.3 + npm 10.9.9: official `nodejs.org/dist` linux-x64 tarball extracted into `/usr/local` (satisfies `package.json` engines `node >=22` and `.nvmrc` = 22).

## Installation (guide's "Lokales Dev-Setup", executed in /workspace)
1. `composer install --no-interaction` → first run failed with "The /workspace/bootstrap/cache directory must be present and writable" (the gitignored standard Laravel dirs are absent from the checkout). Created `bootstrap/cache`, `storage/framework/cache/data`, `storage/framework/sessions`, `storage/framework/views`, `storage/app/{public,private}` and re-ran: exit 0, 138 packages, `artisan package:discover` completed.
2. `cp .env.example .env` and `php artisan key:generate` → "Application key set successfully" (verified `APP_KEY=base64:...` in .env).
3. `mkdir -p database && touch database/database.sqlite` and `php artisan migrate --force` → exit 0; created tables users, cache, cache_locks, jobs, job_batches, failed_jobs, migrations, password_reset_tokens, sessions.
4. `npm install` → exit 0 (it touched `yarn.lock` with linux platform entries and chmod'd some storage `.gitignore` files; both restored with `git checkout --` afterwards so the working tree is clean apart from the gitignored `bootstrap/cache/`).
5. `composer dev` (background, log `storage/logs/dev-server.log`) → runs `php artisan serve` (:8000), `php artisan queue:listen --tries=1`, `php artisan pail --timeout=0`, and `npm run dev` (Vite :5173) via concurrently.

## Verification evidence (all observed)
- `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/` → **HTTP 200**; the returned Inertia HTML contains `<script type="module" src="http://127.0.0.1:5173/@vite/client">`, `.../resources/js/app.ts`, and `.../resources/js/pages/MainPage.vue`.
- `curl http://localhost:5173/resources/js/app.ts` → 200; `.../pages/MainPage.vue` → 200.
- Process check: `php artisan serve` (PID 17467), `php artisan queue:listen` (17469), `php artisan pail` (17471), `node .../vite` (17485) all running.
- Custom Node script (emulating browser module loading, comments stripped) walked the Vite-transformed module graph from `MainPage.vue`: **18/18 reachable modules resolved, 0 real failures** (two apparent 404s were JSDoc-comment false positives inside the `@inertiajs/vue3` prebundle).
- External sensor-data source required by the guide: `curl https://opendata.wuerzburg.de` → HTTP 302 (reachable).
- `php artisan tinker` schema listing confirmed the 9 migrated tables; `config/show-garden.php` (navigation + sensor markers) present.

## Known limitations (upstream source defect, not an installation step)
- The committed tree is missing two Vue components that exist only as imports: `resources/js/components/UserInfo.vue` and `resources/js/components/UserMenuContent.vue` (both imported by `NavUser.vue`; the latter also by `AppHeader.vue`). Verified absent from the git tree (`git ls-tree -r HEAD --name-only | grep -iE "UserInfo|UserMenuContent"` → empty; not gitignored; no other refs).
- Consequences: `npm run build` fails with exit 1 — "Could not resolve ./UserMenuContent.vue from resources/js/components/NavUser.vue"; and `Dashboard.vue` (only reachable via `import.meta.glob` in app.ts, not via any defined route) fails Vite transform ("Failed to resolve import"). The single defined route `GET /` renders `MainPage.vue` (the interactive garden map), whose full dependency tree resolves cleanly, so the main application page is served correctly. The missing files were deliberately not created by me, as that would be code authorship beyond installation.
- Abandoned attempts: direct Composer phar download at a hard-coded version (wrong artifact, HTML returned) — replaced by the official installer; PHP 8.2 (lockfile requires ≥8.4) — replaced by PHP 8.4 per the guide's allowance.

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