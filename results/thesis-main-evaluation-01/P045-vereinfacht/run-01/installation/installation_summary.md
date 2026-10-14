## Method
Installed via Docker Compose from `/workspace` at commit `c2a2b2e`. The `vereinfacht` compose stack was built and started, then the Laravel API and Next.js frontend were configured following the supplied guide.

## Key actions & state
- **Images built**: `vereinfacht-api:latest`, `vereinfacht-web_application:latest`, `vereinfacht-tooling:latest` (plus pulled `mariadb:11.8`, `docker.swagger.io/swaggerapi/swagger-ui`).
- **Containers running** (`docker compose ps`): `vereinfacht-database-1` (3306), `vereinfacht-api-1` (3001→80), `vereinfacht-api-docs-1` (3002→8080), `vereinfacht-tooling-1` (3000), `vereinfacht-web_application-1` (3003→3000).
- **Blocking bug fixed**: `docker/tooling/tooling.Dockerfile` had `COPY --from=node /usr/lib /usr/lib`, which replaced the PHP image's newer `libapk.so.3.0.0` (apk-tools 3.0.8) with node image's older copy (apk-tools 3.0.6), breaking `apk` inside later RUN steps (`Error relocating /sbin/apk: apk_fs_is_malicious_filename: symbol not found`, exit 127). The line was commented out; `docker compose build tooling` then succeeded.
- **API setup** (all inside `vereinfacht-tooling-1`, working dir `/var/www/html/api`): `composer install`; `cp .env.example .env`; `php artisan key:generate`; `php artisan migrate:fresh --seeder=FakeDatabaseSeeder`; `php artisan filament:assets`; `npm ci`; `npm run build`; super-admin token created with `php artisan tinker`.
- **Web setup**: `cp .env.local.example .env.local` (in `/var/www/html/web_application`) with the API bearer token; `npm ci`; `npm run dev` started in the tooling container on port 3000.
- **Permission fix**: `chown -R 1000:1000 api/storage api/bootstrap/cache` on the host — php-fpm worker runs as uid 1000 (`verein`) while files were root-owned, causing HTTP 500 on every request.
- **Compose tweak**: added `env_file: ./web_application/.env.local` and `API_DOMAIN`/`NEXTAUTH_URL` to the `web_application` service so the dockerized build (port 3003) works (previously next-auth `NO_SECRET` 500).

## Access points
- API/admin: http://localhost:3001 (admin login `hello@vereinfacht.digital` / `password`)
- Swagger docs: http://localhost:3002
- Web dev frontend: http://localhost:3000 (test user `club-admin-1@example.org` / `password`)
- Dockerized web frontend: http://localhost:3003

## Files changed in repo
`docker/tooling/tooling.Dockerfile` and `docker-compose.yml`. Local runtime config (`api/.env`, `web_application/.env.local`) and dependency dirs are gitignored. No incomplete work; the Cypress `e2e` project referenced by the guide is absent from the repository.