## Environment
Ubuntu 22.04.5 container (root, no systemd); workspace `/workspace` containing the forked consul repo at commit `5c3c7e1` (branch `cli_wur_2`, the "Mitmachportal Würzburg" project). All work done as root; PATH extended via `/etc/profile.d/rbnode.sh` (`/usr/local/ruby/bin:/opt/node/bin`).

## Method
Both documented paths of the guide were executed. The **development setup** was followed first, then the **production setup** to completion. Abandoned nothing; the only incomplete item is a later `db:dev_seed` section caused by a pre-existing repo bug (see below).

### Toolchain (guide step 2/4 equivalents)
- System packages: build-essential, cmake, pkg-config, zlib1g-dev, libssl-dev, libreadline-dev, libyaml-dev, libxml2-dev, libxslt1-dev, libffi-dev, libcurl4-openssl-dev, libpq-dev, imagemagick, shared-mime-info, policykit-1, libgeos-dev, proj-bin, pandoc, postgresql+contrib (14.24), cron, memcached.
- Ruby 3.1.4p223 built from source (ruby-lang.org tarball) → prefix `/usr/local/ruby`. Node v20.11.0 official tarball → `/opt/node` (symlinked into `/usr/local/bin`). Versions match `.ruby-version` (3.1.4) and `.node-version` (20.11.0).
- PostgreSQL started with `service postgresql start`; superuser role `root` (password `root`) created; `config/database.yml` left with empty username/password as in the example, so connections use the OS user.

### Dependencies
- `bundle install` → "Bundle complete! 131 Gemfile dependencies, 311 gems" (later 314 after one addition). `bundle check` → "The Gemfile's dependencies are satisfied".
- `npm install --no-audit --no-fund` → 419 top-level packages in `/workspace/node_modules`.

### Configuration (guide steps 5–6)
- `config/database.yml` from example; `production:` pointed at `consul_production`.
- `config/secrets.yml` from example; production block: `secret_key_base` generated via `RAILS_ENV=production bin/rake secret` (value written in file), `server_name: "localhost"`, `force_ssl: true` kept, no SMTP set (no external mail server available).
- `config/secret_emails.yml` created with `admin@consul.dev` (guide step 6).

### Databases
- `consul_development` + `consul_test`: created via `bin/rake db:create`; schema loaded via `db:schema:load` / `RAILS_ENV=test bin/rake db:setup` → 262 tables each.
- `consul_production`: created per guide with `shared_extensions` schema and plpgsql/unaccent/pg_trgm extensions; additionally `ALTER DATABASE consul_production SET search_path TO public, shared_extensions` (required so `schema.rb`'s `gin_trgm_ops` index resolves); `RAILS_ENV=production` `db:schema:load` ✅, `db:seed` ✅ (admin user + 237 settings + overview projekt), `assets:precompile` ✅ (194 fingerprinted files in `public/assets/`), `bundle exec whenever --update-crontab` ✅.

### Verification / running state
- Development server: `bin/rails s -b 0.0.0.0 -p 3000` — currently running; `curl http://localhost:3000/` → HTTP 200 (CONSUL page), `/users/sign_in` → HTTP 200.
- Production server (transient, stopped after verification): `RAILS_ENV=production bin/rails s -p 3001` — served HTTP 200 with `force_ssl` temporarily off; with the documented `force_ssl: true` it returned 301 → `https://localhost:3001/` (TLS unavailable: no public domain/certbot CA in container).
- Admin credentials verified: BCrypt match of stored hash against `Aa12345678` for `admin@consul.dev` → true; user confirmed and has an `Administrator` record; `mod/manager/valuator/verified/unverified@consul.dev` all present.
- Memcached: `VERSION 1.6.14` response on 127.0.0.1:11211.
- `bin/rspec` runs in the test environment (e.g. `spec/models/signature_spec.rb` → 26 examples, 19 failures — all from the pre-existing factory/model drift below).

## Source modifications made during installation (fork bugs)
1. `config/secrets.yml`: added missing `development:` and `test:` sections (the committed `secrets.yml.example` contains only `staging`/`production`, so `Rails.application.secrets.dt` was nil and the app crashed on boot in dev/test).
2. `Gemfile`/`Gemfile.lock`: added `gem "database_cleaner", "~> 2.0"` to the development/test group (required by `db/dev_seeds.rb` but absent from the Gemfile).
3. `db/dev_seeds.rb`: swapped `require_relative` order so `settings` loads before `projekts` (map.latitude/longitude/zoom settings must exist before the first Projekt's MapLocation is created; upstream master loads settings first).
4. `db/dev_seeds/{users,debates,proposals,budgets,notifications,legislation_proposals}.rb`: this branch removed the `terms_of_service` column (validation commented out in all models; no column or accessor exists) and replaced it with acceptance-validated virtual attributes. Seeds passed the removed attribute and raised `NoMethodError`/`UnknownAttributeError`. Mapped `terms_of_service: "1"` → `terms_data_storage/terms_data_protection/terms_general: "1"` in `users.rb` (matching the fork's own `lib/tasks/seed_evaluation_stats.rake`) and → `resource_terms: "1"` in the four resource seeds.

## Incomplete / broken (pre-existing repo state, not install-related)
`db:dev_seed` completes Settings → Projekts → Geozones → Users (48 users incl. all documented accounts), then aborts in the **Debates** section: `unknown attribute 'projekt' for Debate`. On this branch resource models (Debate, Proposal, Poll, Budget::Investment) were refactored to `belongs_to :projekt_phase` (presence-validated STI model) with the `projekt_id` column removed, but the committed seeds still pass `projekt:` (12 remaining stale references in debates/notifications/polls/proposals) and no seed file creates any `ProjektPhase`. `spec/factories/*` carry the same stale references, causing the observed spec failures. Fixing this would require re-authoring the demo-seed section to the new phase model — application-code work beyond installing the software.

## Final state
- Running services: PostgreSQL 14, memcached 1.6.14, cron, development Rails/Puma server on port 3000 (HTTP 200).
- Databases: `consul_development` (schema + partial dev seed), `consul_test` (schema), `consul_production` (schema + seed + precompiled assets + crontab).
- Start commands: dev `bin/rails s` (port 3000); production `RAILS_ENV=production bin/rails s`; tests `bin/rspec`.
- Access: http://localhost:3000, login admin@consul.dev / Aa12345678.