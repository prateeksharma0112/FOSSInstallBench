Installed vereinfacht (Laravel JSON:API backend + Next.js web frontend + MariaDB + Swagger UI) at /workspace using the Docker Compose development environment described in Installation.md.

**Execution context:** Docker daemon (v29.7.2, overlay2) on Ubuntu 22.04 host; compose project `vereinfacht` started with `docker compose up -d --build` from /workspace. All application work was done inside the `vereinfacht-tooling-1` container (working dir /var/www/html = /workspace bind mount), per the guide.

**Steps completed (per guide):**
1. `docker compose up -d --build` — built and started database (mariadb:11.8), api (nginx+php-fpm, port 3001), api-docs (swagger-ui, port 3002), web_application (Next.js standalone, port 3003), tooling (port 3000).
2. API setup in tooling container `/var/www/html/api`: `composer install`, `cp .env.example .env`, `php artisan key:generate`, `php artisan migrate:fresh --force --seeder=FakeDatabaseSeeder` (all seeders DONE), `php artisan filament:assets`, `npm ci`, `npm run build` (vite production build OK).
3. Created super admin token via `php artisan tinker --execute="echo User::find(1)->createToken('Super Admin Token')->plainTextToken;"` → token `1|BTSJGaZ2zLITV0ZTpEdSNiterXyhlma7hH8TYtLXaec176d2` (non-interactive substitute for the guide's interactive tinker). The guide's second token location `/e2e/cypress.config.ts` does not exist at this commit (the guide itself notes e2e testing is not yet included), so only `web_application/.env.local` was updated.
4. Web frontend setup in `/var/www/html/web_application`: `cp .env.local.example .env.local` + `API_BEARER_TOKEN` filled in, `npm ci`, then `npm run dev` started as a detached background process (`docker compose exec -T -d tooling`); log at /tmp/next_dev.log inside the tooling container. Dev server ready on port 3000; it auto-ran `openapi-typescript` against http://api/v1_openapi.json successfully.

**Workarounds required:**
- First `docker compose up -d --build` failed at tooling image step `docker-php-ext-configure gd` with "Error relocating /sbin/apk: apk_fs_is_malicious_filename: symbol not found". Root cause: tooling.Dockerfile `COPY --from=node /usr/lib /usr/lib` overwrites the php image's libapk.so.3.0.0 (apk-tools 3.0.8) with the node image's older libapk.so.3.0.0 (apk-tools 3.0.6), breaking the apk binary. Patched /workspace/docker/tooling/tooling.Dockerfile to back up the base libapk to /usr/local/etc/ before the node copy and restore it after.
- API returned 500 (storage/logs/laravel.log permission denied) because the /workspace/api host tree was root-owned while the api container runs as uid/gid 1001 (verein). Fixed with `chown -R verein:verein /var/www/html/api /var/www/html/web_application` run as root in the tooling container.

**Final running state (access points):**
- http://localhost:3000 — Next.js web frontend (dev), login at /admin/auth/login (redirects to /en/admin/auth/login), seeded user club-admin-1@example.org / password
- http://localhost:3001 — Laravel API; Filament admin login at /admin/login (hello@vereinfacht.digital / password)
- http://localhost:3002 — Swagger UI (spec from /v1_openapi.json)
- http://localhost:3003 — Next.js production build
- MariaDB on localhost:3306, db `verein`, user `verein`/`verein`

**Known state/notes:** API super-admin token stored in /workspace/web_application/.env.local. No e2e project exists at this commit, so no cypress config to update. The dev server on port 3000 runs as a detached process in the tooling container and will not auto-restart if the tooling container is restarted.