## Samarbeid Installation Summary

**Working directory:** `/workspace` (repository checked out at the predefined commit). Execution context: Ubuntu 22.04.5 container, root user, Docker available (daemon reachable).

### Method
The documented method was used: install prerequisites, then run `bin/setup`. The guide's stated requirements (Ruby per `.ruby-version` = 3.4.10, Node/yarn per `.tool-versions` = nodejs 24.9.0 / yarn 4.13.0, PostgreSQL, Docker & Docker Compose) were all absent initially and were installed fresh.

### Prerequisites installed
- **PostgreSQL 14** via apt (`postgresql`, `postgresql-contrib`, `libpq-dev`, plus build toolchain). Cluster started with `pg_ctlcluster 14 main start`. Created superuser role `samarbeid` (password `samarbeid`) and set postgres password.
- **Ruby 3.4.10** compiled from source using `rbenv/ruby-build` into prefix `/usr/local/ruby-3.4.10`; symlinked `ruby`, `gem`, `bundle`, `bundler`, `rake`, and later `foreman` into `/usr/local/bin`; installed bundler gem.
- **Node.js 24.9.0** from the official nodejs.org tarball into `/usr/local/node-v24.9.0-linux-x64`, symlinks in `/usr/local/bin`; `corepack enable` + `corepack prepare yarn@4.13.0 --activate`.

### Configuration
- Created `/workspace/config/database.yml` from `config/database.yml.sample`, defaulting `host: 127.0.0.1`, `username/password: samarbeid`.

### Install actions
1. `bundle install` — exit 0.
2. `yarn install` — exit 0, 598 packages, node-modules linker.
3. `bin/rails db:prepare` — exit 0; created `samarbeid_development` and `samarbeid_test`; seeded super-admin `admin@example.org` (password `UxbuS7Zp8BNM`). This step also auto-started the `docker-compose` dependency services.
4. `bin/setup --skip-server` — exit 0 (idempotent re-run confirming dependency/DB setup).
5. `bin/dev` (foreman + `Procfile.dev`) started in background — Puma on `127.0.0.1:3000`, Vite dev server on `3036`. Log: `/tmp/samarbeid-dev.log`.

### Resulting state
- App reachable at **http://localhost:3000**, redirecting unauthenticated users to `/users/sign-in`, page title `samarbeid`.
- Docker containers running: `workspace-apache-tika-1` (9998), `workspace-mailpit-1` (1025/8025).
- Database seeded with 1 user (admin@example.org, role `super_admin`).

### Notes / incomplete
- No application-level configuration secrets/env beyond the database were changed.
- The `bin/dev` process runs in the background; it was not daemonized as a system service.