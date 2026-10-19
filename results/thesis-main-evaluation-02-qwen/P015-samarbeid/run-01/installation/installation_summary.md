Installed and verified the "samarbeid" collaboration hub (Ruby on Rails 8.1.3.1 + Vue 2/Vuetify SPA, PostgreSQL) in the workspace at `/workspace` on Ubuntu 22.04.

**Environment/requirements (from `.ruby-version`, `.tool-versions`):** Ruby 3.4.10, Node 24.9.0 + Yarn 4.13.0, PostgreSQL, Docker + Compose. None of Ruby/Node/yarn/PostgreSQL were preinstalled (Docker 29.7.2 + Compose v2 were present).

**Steps performed:**
1. Installed build prerequisites via apt: build-essential, libpq-dev, libyaml-dev, libssl-dev, zlib1g-dev, libffi-dev, git, curl.
2. Built Ruby 3.4.10 from source (`cache.ruby-lang.org`) into `/opt/tools/ruby-3.4.10`; PATH persisted in `/root/.bashrc`.
3. Installed Node.js v24.9.0 (prebuilt tarball at `/opt/downloads/node-v24.9.0-linux-x64`, symlinked to `/usr/local/bin`), activated Yarn 4.13.0 via corepack.
4. Installed PostgreSQL 14.24 via apt, started the `main` cluster on :5432, created superuser role `samarbeid` (password `samarbeid`).
5. Started dependency services `apache/tika:3.2.3.0-full` (9998) and `axllent/mailpit` (1025/8025) with `docker compose up -d` (images pre-pulled).
6. Copied `config/database.yml.sample` → `config/database.yml`; set connection env vars APP_DB_HOST=localhost, APP_DB_USERNAME=samarbeid, APP_DB_PASSWORD=samarbeid, APP_DB_DATABASE=samarbeid_development.
7. Ran the documented `bin/setup` (with `--skip-server`): satisfied bundle, ran `bin/yarn`, prepared + seeded the DB. Output: "Created database 'samarbeid_development'/'samarbeid_test'" and generated super-admin **admin@example.org / TTOF3UHA0bsQ**.
8. Started the dev server with `bin/dev` (background; foreman → Puma/Rails `bin/rails s` on :3000 + Vite dev on :3036; log at `/tmp/dev/server.log`).

**Known startup/access points:**
- App: http://localhost:3000 (redirects to /users/sign-in; admin login admin@example.org / TTOF3UHA0bsQ).
- Start dev server from `/workspace` with `bin/dev` (requires the APP_DB_* env vars). Dependency services via `docker compose up -d`.

**Final state:** All components running and healthy — Rails 8.1.3.1 + Puma on :3000, Vite on :3036, PostgreSQL online, tika + mailpit containers up. No outstanding work.