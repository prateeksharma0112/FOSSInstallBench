**Method used:** Default method from the guide — pull pre-built images from `registry.opencode.de` (no login required; `docker compose pull` exited 0) and start with `docker compose up -d`. The local-build alternative (`docker-compose.build.yml`) was not needed.

**Environment/working directory:** Docker 29.7.2 + Compose v5.5.0 already present. Repository pre-checked out at `/workspace` (commit `6f9c4ea`). All compose commands run as root from `/workspace`.

**Configuration (`/workspace/.env`, created from `.env.example` per guide):**
- `API_CREDENTIAL_ENCRYPTION_KEY` generated with `openssl rand -base64 32` via the guide's exact `sed` command.
- `DB_PASSWORD`, `INITIAL_ADMIN_PASSWORD`, `SWAGGER_HTTP_AUTH_PASSWORD`, `FRONTEND_COOKIE_VALIDATION_KEY`, `BACKEND_COOKIE_VALIDATION_KEY` randomized with openssl (guide requires adapting passwords/cookie keys).
- `APP_DOMAIN=localhost`, `LETSENCRYPT_EMAIL=admin@localhost` (no public domain available in the sandbox).
- `TRAEFIK_TLS_CERTRESOLVER` set empty (documented local-development option in `.env.example`) so Traefik does not run a dead Let's Encrypt resolver.

**Startup state:** `docker compose up -d` exited 0. `docker compose ps` shows all 4 services Up: `postgres_dashapp_container` (healthy), `traefik_proxy_container` (ports 80/443 published), `yii2_vue_dash_container` (web, image `registry.opencode.de/.../gitlab-profile:latest`), `iothubsh_adapter` (uvicorn, image `.../gitlab-profile/iothubsh-adapter:latest`). Named volumes created: `workspace_db_data`, `workspace_yii2-uploaded-files`, `workspace_yii2-system-assets`, `workspace_letsencrypt_data`, `workspace_iothubsh-adapter-data`.

**Observed startup:** Web container log shows PostgreSQL base schema init, "25 migrations were applied. Migrated up successfully.", then Apache "resuming normal operations" (Apache 2.4.68).

**Access points (per guide, with sandbox caveats):**
- Traefik on host :80/:443 routes on `Host: APP_DOMAIN` (here `localhost`); HTTP router correctly issues 301 → `https://localhost/`. TLS termination for `localhost` has no certificate (resolver disabled), so HTTPS via Traefik is not usable in the sandbox; this is an environment limitation, not an install defect.
- Web app verified directly inside the web container: `GET /` → 200; administration at `/administration` (initial account `admin`, password from `INITIAL_ADMIN_PASSWORD` read at init — confirmed `admin` row in `backendusers`); Swagger at `/administration/docs/` → 401 without credentials, 200 with `admin:<SWAGGER_HTTP_AUTH_PASSWORD>`; measurements API `POST /api/v1/node/measurements` → 400 with valid Yii validation error body (endpoint live, requires Bearer credential + non-empty `measurements` array per `docs/`).
- iothubsh-adapter: uvicorn up on :8000, `/docs` and `/openapi.json` → 200; webhook routes (`/webhook/config`, `/webhook/measurement`) proxied by Traefik on the APP_DOMAIN host (301 observed, same TLS caveat).

**No incomplete work.** Stack is left running. Known access commands: `docker compose logs -f web postgres`, `docker compose exec -T postgres psql -U yii2_user -d yii2_db`.