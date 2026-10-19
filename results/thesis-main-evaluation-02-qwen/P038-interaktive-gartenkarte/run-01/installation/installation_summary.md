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