Installed Zammad at /workspace using the guide's documented Manual Setup method, since the recommended devcontainer method relies on VS Code's "Reopen in Container" workflow which is not available in this headless environment.

Environment/toolchain installed natively:
- Ruby 3.4.9 compiled from source to /usr/local (matches .ruby-version), gem/bundler 2.6.9.
- Node.js v24.21.0 (NodeSource) + pnpm 11.25.0 via corepack (matches package.json engines).
- PostgreSQL 14 native service with role `zammad` and databases `zammad_development` and `zammad_test`.
- Redis 7 native service (redis-server), verified with redis-cli ping = PONG.
- Elasticsearch 8.15.5 run via Docker container `zammad-es` (image docker.elastic.co/elasticsearch/elasticsearch:8.15.5) on 127.0.0.1:9200; Zammad requires ES >= 8.15.
- System build deps: build-essential, libssl/readline/yaml/ffi/gdbm/ncurses/pq, libimlib2 + libimlib2-dev, libxml2/xslt.

Application setup in /workspace:
- `bundle config set path vendor/bundle` then `bundle install` → 318 gems.
- `pnpm install --frozen-lockfile` → Node deps.
- Created config/database.yml (gitignored) pointing to 127.0.0.1 postgres as user zammad.
- `RAILS_ENV=development bundle exec rails db:prepare` → migrations + seeds applied successfully.
- `Setting.set('es_url', 'http://127.0.0.1:9200')`, `rails zammad:setup:auto_wizard`, `rails zammad:searchindex:rebuild`, `rails assets:precompile`.
- `foreman start -f Procfile.dev` (foreman installed as the documented Linux alternative to forego, which had no downloadable binary) launches 5 processes: vite, puma web (port 3000), websocket (6042), background worker, dartsass.

Runtime environment variables used: RAILS_ENV=development, REDIS_URL=redis://127.0.0.1:6379, VITE_RUBY_HOST=127.0.0.1, ZAMMAD_BIND_IP=0.0.0.0. These are captured in /tmp/zammad_env.sh.

Verification: HTTP GET http://127.0.0.1:3000/ returns 200 with the Zammad login page; POST /api/v1/signin with admin@example.com / test returns HTTP 201 with a full authenticated session; SearchIndexBackend.info confirms ES 8.15.5 connectivity; all 5 processes running.

Access point: http://localhost:3000, default credentials admin@example.com / test. Startup command: source /tmp/zammad_env.sh && cd /workspace && foreman start -f Procfile.dev .