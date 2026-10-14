**Project:** Mitmachportal Würzburg (CONSUL fork, commit 5c3c7e1), installed at `/workspace` on Ubuntu 22.04 as root.

**Method:** Documented development setup from the guide/README.

**Steps performed**
- apt-get install of documented prerequisites: build-essential, postgresql-14 + contrib, imagemagick, libpq-dev, cmake, pkg-config, shared-mime-info, libxml2/libxslt, libffi, libyaml, libgeos/proj, pandoc, git/curl/wget, etc.
- Started PostgreSQL 14 cluster and created superuser role `root` (used by the DB config).
- Ruby 3.1.4 via RVM at `/usr/local/rvm`; Node 20.11.0 via fnm at `/root/.local/share/fnm/node-versions/v20.11.0` (binaries symlinked into `/usr/local/bin`, PATH persisted in `/etc/profile.d/rvm-fnm.sh`).
- `bundle config set --local path vendor/bundle`; `bundle install` (314 gems, success); `npm install` (571 packages).
- Copied `config/database.yml` and `config/secrets.yml` from their examples; populated DB user/password and added the missing `development`/`test` secret sections (the supplied secrets example contained only staging/production, so Rails otherwise crashed at boot in `lib/dt.rb` / `config/initializers/cors.rb`).
- Database: `bin/rake db:create` → `bin/rake db:schema:load` → `bin/rake db:dev_seed` (success) → `RAILS_ENV=test bin/rake db:setup`.

**Resulting state (verified)**
- Working dir `/workspace`; app runs via `bin/rails s` on Puma at `http://127.0.0.1:3000`.
- HTTP: `/` 200, `/proposals` 200, `/debates` 200, `/polls` 200, `/admin` 302 (auth), `/users/sign_in` 200; admin login POST returns 302 and session shows `data-current-user-id="1"`.
- Seed data: Users 48, Administrator 1, Projekts 10, Debates 103, Proposals 65, Polls 15, Legislation::Process 19, Settings 237. Admin `admin@consul.dev` / `Aa12345678` confirmed+verified+administrator.
- `bundle check`: dependencies satisfied. Rails boots in development; Rails boots in test with 262 tables.

**Repairs (needed to complete documented `db:dev_seed`)**
The fork's committed `db/dev_seeds` referenced model APIs that had changed: added `:terms_of_service` accessor on `User`; set GDPR consent fields; reordered settings before projekts; create per-type ProjektPhases; `projekt:`→`projekt_phase:` and `terms_of_service`→`resource_terms`; adapted Budget to single group/heading; built VotationType for poll questions; added required valuator_explanation/projekt_phase/recipient_group; keyword-splat fixes to `random_locales_attributes`. Added `database_cleaner` to `Gemfile_custom` (required by `db/dev_seeds.rb` and `spec/spec_helper.rb` but absent from the Gemfile).

**Incomplete/unknown**
- Documented plain `bin/rspec` does not launch due to a pre-existing spring/mutex_m default-gem conflict; tests run with `DISABLE_SPRING=1 bin/rspec` or `bundle exec rspec`. Some specs fail against further stale test factories not in installation scope.
- `/budgets` returns 404 (budgets are exposed under project phases in this fork).