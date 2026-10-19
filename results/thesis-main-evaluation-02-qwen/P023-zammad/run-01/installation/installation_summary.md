Zammad 7.2.0 was installed as a local development environment using the repository's own devcontainer configuration, reproduced with `docker compose` (the recommended VS Code Dev Containers path is unavailable in this headless container).

**Execution context:** host is an Ubuntu 22.04 container (Docker 29.7.2, 8 CPUs, ~7.6GB RAM, ~951GB free disk). The repository is checked out at `/workspace` (shared workspace). The devcontainer's `.devcontainer/default/compose.yaml` (project name `zammad-devcontainer`) was started with `docker compose up -d` from `/workspace/.devcontainer/default`, creating 5 containers: `devcontainer` (image `ghcr.io/rails/devcontainer/images/ruby:3.4.9`), `postgresql` (17.5-alpine), `redis` (7.0), `memcached` (1.6.38-alpine), `elasticsearch` (9.3.2). The repo is mounted at `/workspaces/workspace` inside the devcontainer (user `vscode`, uid 1000).

**Steps (all inside the devcontainer unless noted):**
1. Reproduced the devcontainer features: apt packages (`curl gnupg libimlib2-dev libimlib2 postgresql-client libpq-dev`), Go 1.24 + `go install github.com/ddollar/forego@master`, and Node 24.22.0 + pnpm 11.25.0 (via mise shims on PATH).
2. `chown -R 1000:1000 /workspace` (on host) — the checkout was root-owned; the container user (uid 1000) could not write `Gemfile.lock`, so the first `bin/setup` aborted. After chown it succeeded.
3. `bin/setup --skip-server` → exit 0: `bundle install`, `CI=true pnpm install --frozen-lockfile`, `npm -g install coffeelint stylelint`, created `config/database.yml` from sample, `db:prepare` (all DB migrations ran), `log:clear tmp:clear`.
4. `rails r "Setting.set('es_url','http://elasticsearch:9200')"`.
5. `rails zammad:setup:auto_wizard` → exit 0 (seeds admin@example.com and default data).
6. `rails zammad:searchindex:rebuild` → exit 0 (rebuilds all Elasticsearch indexes).
7. `bin/dev` (forego start of vite, web/puma, websocket, worker, dartsass) → running.

**Startup / access points:**
- App: `http://localhost:3000` (in-container `http://127.0.0.1:3000`); Vite dev server on `:3036`; websocket on `:6042`.
- Dev credentials: `admin@example.com` / `test`.
- To restart the app services: `bin/dev` in the devcontainer; the data services are managed by `docker compose` in `/workspace/.devcontainer/default`.

**Known state / issues recovered:**
- Search index rebuild first failed twice with `resource_already_exists_exception` because it ran concurrently with the dev background worker that also manages ES indexes. Recovered by stopping `bin/dev`, running `searchindex:rebuild` cleanly (exit 0), then restarting `bin/dev`.
- The devcontainer's `post_create.sh` references `pnpm setup` (there is no `setup` script in package.json); I used `bin/setup --skip-server` directly, which is the documented manual-setup script and is what performs the install/migrate/seed.

**Resulting state (verified):** all 5 compose services `Up`; 6 app processes running (forego, puma, vite, websocket-server, background-worker, dartsass); `GET /` returns HTTP 200 with title "Zammad Test System"; login with the documented credentials succeeds (HTTP 201) and yields an authenticated session (signshow HTTP 200); all `zammad_development_*` Elasticsearch indexes are present.