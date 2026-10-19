# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** Mitmachportal Würzburg

**Description:** Digital participation platform of the city and district of Würzburg for participatory budgeting, proposals and other participation formats.

## Supplied installation guide

## Guide: Installation.md

## Development setup

Prerequisites: `git`, **Ruby 3.1.4**, **Node.js 20.11.0**, PostgreSQL, CMake,
`pkg-config`, `shared-mime-info` and ImageMagick.

```bash
git clone git@github.com:hanuschka/consul.git
cd consul
bundle install
npm install
cp config/database.yml.example config/database.yml
cp config/secrets.yml.example config/secrets.yml
bin/rake db:create
bin/rake db:schema:load
bin/rake db:dev_seed
RAILS_ENV=test bin/rake db:setup
```

> A fresh database loads the committed `db/schema.rb` (`db:schema:load`) rather than
> replaying migrations from zero. Some historical migrations introspect current models, so
> a from-zero `db:migrate` does not run cleanly on an empty database; `schema.rb` is the
> authoritative source.

Run the app locally:

```bash
bin/rails s
```

Run the tests:

```bash
bin/rspec
```

The seed data includes a default admin user (already verified, so it can do everything):

> **user:** admin@consul.dev
> **pass:** Aa12345678

`db:dev_seed` also creates users for every role at the same password (`Aa12345678`) —
e.g. `mod@consul.dev`, `manager@consul.dev`, `valuator@consul.dev`, `verified@consul.dev`,
`unverified@consul.dev`.

## Production setup

A production deploy needs Ruby, Rails, PostgreSQL, Nginx, Puma, SMTP, Memcached,
DelayedJob, HTTPS (Let's Encrypt) and Capistrano. The steps below set this up manually.

### Manual installation

These steps assume a clean **Ubuntu 22.04 or 24.04** server with `root`/`sudo` access. All
application commands run as the unprivileged `deploy` user, from the app directory
(`/home/deploy/consul/current` once Capistrano is in use, or wherever you check the code
out for a first deploy).

#### 1. Create the deploy user

```bash
adduser --disabled-password deploy
usermod -aG sudo deploy
# allow passwordless sudo for the deploy user (Capistrano/maintenance)
echo 'deploy ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/deploy
```

Add your SSH public key to `/home/deploy/.ssh/authorized_keys` and log in as `deploy` for
the remaining steps.

#### 2. System packages

```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y \
  build-essential cron tmux vim htop git-core wget curl \
  zlib1g-dev libssl-dev libreadline-dev libyaml-dev \
  libxml2-dev libxslt1-dev libffi-dev libcurl4-openssl-dev \
  libpq-dev imagemagick ruby-dev shared-mime-info policykit-1 \
  libgeos-dev proj-bin pandoc
```

#### 3. PostgreSQL

```bash
sudo apt-get install -y postgresql postgresql-contrib python3-psycopg2
sudo systemctl enable --now postgresql

# create the deploy DB role and database
sudo -u postgres createuser --encrypted deploy
sudo -u postgres createdb --owner deploy consul_production

# enable the extensions CONSUL relies on, in a dedicated schema
sudo -u postgres psql -d consul_production <<'SQL'
CREATE SCHEMA IF NOT EXISTS shared_extensions AUTHORIZATION deploy;
CREATE EXTENSION IF NOT EXISTS plpgsql;
CREATE EXTENSION IF NOT EXISTS unaccent  SCHEMA shared_extensions;
CREATE EXTENSION IF NOT EXISTS pg_trgm   SCHEMA shared_extensions;
SQL
```

PostgreSQL should listen on `localhost` only; do not expose port 5432 externally.

#### 4. Ruby and Node

Install the exact versions pinned in the repo (`.ruby-version` → **3.1.4**,
`.node-version` → **20.11.0**). Use whichever version managers you prefer; the examples
below use RVM for Ruby and `fnm` for Node:

```bash
# Ruby (RVM)
\curl -sSL https://get.rvm.io | bash -s stable
source ~/.rvm/scripts/rvm
rvm install "$(cat .ruby-version)"

# Node (fnm)
curl -fsSL https://fnm.vercel.app/install | bash
fnm install "$(cat .node-version)"
```

#### 5. Application code and dependencies

```bash
git clone git@github.com:hanuschka/consul.git /home/deploy/consul/current
cd /home/deploy/consul/current
git checkout a14            # the release tag you deploy to production

bundle config set --local path 'vendor/bundle'
bundle config set --local without 'development test'
bundle install

fnm exec npm install --production
```

#### 6. Configuration and secrets

```bash
cp config/secrets.yml.example   config/secrets.yml
cp config/database.yml.example  config/database.yml

# generate a production secret_key_base
bin/rake secret
```

`config/secret_emails.yml` is gitignored and has no example, but it is **required** for
deployment: Capistrano lists it under `:linked_files`, so `cap deploy` fails if
`shared/config/secret_emails.yml` does not exist. You must create it. It is a
newline-separated allowlist of "partner" email addresses; a single placeholder address
(`admin@consul.dev`) is enough to start.

Edit `config/secrets.yml` for the `production` environment:

- set `secret_key_base` to the value generated above,
- set `server_name` to your domain,
- keep `force_ssl: true`,
- fill in the SMTP block under `smtp_settings` (see **Email** below),
- set `http_basic_username` / `http_basic_password` (and `http_basic_auth`) if you want to
  password-protect the site.

Set the database name / host / user / password in `config/database.yml`, pointing the
`production` environment at the `consul_production` database created in step 3.

#### 7. Load schema, seed and precompile

A fresh production database loads the committed `db/schema.rb` rather than replaying
migrations from zero (see the note in the development section — a from-zero `db:migrate`
does not run cleanly). Capistrano runs `db:migrate` on later deploys once the schema is in
place.

```bash
RAILS_ENV=production bin/rake db:schema:load
RAILS_ENV=production bin/rake db:seed
RAILS_ENV=production bin/rake assets:precompile
RAILS_ENV=production bundle exec whenever --update-crontab
```

#### 8. Application server (Puma)

Run Puma as a systemd service bound to a UNIX socket that Nginx proxies to. Create
`/etc/systemd/system/puma.service` (adjust paths/worker counts to the box), then:

```bash
sudo systemctl enable --now puma
```

#### 9. Web server (Nginx) and HTTPS

```bash
sudo apt-get install -y nginx python3-certbot-nginx
```

Configure an Nginx vhost that proxies to the Puma socket, then obtain a certificate
(renewal is handled automatically by `certbot.timer`):

```bash
sudo certbot --nginx --expand -d your-domain.example
```

#### 10. Background jobs and cache

```bash
# Memcached
sudo apt-get install -y memcached
sudo systemctl enable --now memcached
```

Run DelayedJob workers as systemd instances. Install a template unit at
`/etc/systemd/system/delayed_job@.service` and start one instance per worker:

```bash
sudo systemctl enable --now delayed_job@1 delayed_job@2
sudo systemctl status 'delayed_job@*'
```

#### 11. Subsequent deploys (Capistrano)

After the first release, new code is shipped with Capistrano from your local machine.
`config/deploy.rb` already sets `repo_url` to `https://github.com/hanuschka/consul.git` and
defines the `production`, `staging` and `preproduction` stages. Per-target deploy settings
(`deploy_to`, `ssh_port`, server IP, user) live in `config/deploy-secrets/` (gitignored,
one file per client). The ref to ship — a branch or release tag — is chosen with the
`branch` env var (Capistrano resolves it through `git rev-parse`, so a tag works too):

```bash
branch=a14 cap production deploy
```

> See `config/deploy.rb` for how the per-client secrets file is selected.

### Email

CONSUL sends mail asynchronously through the DelayedJob queue. Configure SMTP in the
`production` block of `config/secrets.yml`:

```yaml
mailer_delivery_method: "smtp"
smtp_settings:
  :address:              "smtp.example.com"
  :port:                 "587"
  :domain:               "your-domain.example"
  :user_name:            "username"
  :password:             "password"
  :authentication:       "plain"
  :enable_starttls_auto: true
```

Because mail is queued, SMTP misconfiguration surfaces in the worker logs rather than as a
500 error. Inspect the last failure from the Rails console:

```bash
RAILS_ENV=production bin/rails runner 'puts Delayed::Job.last&.last_error'
```

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

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