## Startuphafen installation — SUCCESS

**Workspace:** `/workspace` (repo at commit `868cad5`, "v2.0.0 release", branch detached). Execution context: Ubuntu 22.04 host container, Docker 29.7.2, Node.js 20.20.2 installed via NodeSource.

### Method
The guide's documented path is a VS Code Dev Container built from `.devcontainer/devcontainer.json` (compose files `apps/startuphafen-backend/src/assets/docker-compose.yml` + `.devcontainer/dev-compose.yml`) with the apps run via npm scripts `front` and `back`. The documented compose references files that do not exist in the repo (`.devcontainer/keycloak/entrypoint.sh`, `.devcontainer/keycloak/themes`) and its `devcontainer` service depends on the Docker-in-Docker/VS Code desktop features. I reproduced the same architecture headlessly:

1. **Prep:** `npm install` in `/workspace` (lockfile, ~1400 pkgs); backend production build `npx nx run startuphafen-backend:build:development` → `dist/apps/startuphafen-backend`.
2. **Infra:** new compose file `/workspace/.devcontainer/dev-fixed.yml` (validated with `docker compose config`), services: `devcontainer` (image `mcr.microsoft.com/devcontainers/typescript-node:20-bookworm`, mounts `/workspace`), `caddy:2.11-alpine` (BACKEND_HOST=devcontainer:5000, FRONTEND_HOST=devcontainer:4201, port 4000), `database` (pgvector/pgvector:pg15, app/app), `keycloak-database` (postgres:15.5, kc/kc), `keycloak` (quay.io/keycloak/keycloak:26.1.2, port 28080→8180, realm import from `.devcontainer/keycloak/imports/startuphafen.json`, theme mount), `maildev` (:1080), `pgadmin` (:3838). Started with `docker compose -f .devcontainer/dev-fixed.yml up -d`.
3. **Keycloak repair:** realm import initially failed: `Caused by: org.keycloak.models.ModelException: invalidPasswordMinSpecialCharsMessage` (stack: `DefaultExportImportManager.importRealm`). KC 26 validates imported user credentials against the realm password policy; documented dev passwords (admin/alice/marie) fail `length(8) and … specialChars(1) …`. Fixed by relaxing `passwordPolicy` to `length(5)` in the dev realm JSON; import then logged `Realm 'startuphafen' imported` / `Import finished successfully`.
4. **Config:** created `apps/startuphafen-backend/src/assets/.localConfigs.json` per the guide template, adjusted to the current schema (`finanzaemter: []` instead of a string `bufaNr`/`jurisdiction` object, and omitted the `mistral` block whose empty `apiKey` throws in `MistralAIEmbeddings` and crashes startup; omitting it is schema-optional and the routers warn + degrade).
5. **Apps:** inside the `devcontainer` service, ran the documented `npm run back` (`nx run startuphafen-backend:serve:development`, watch) and `npm run front` (`nx serve startuphafen-frontend`). First frontend attempt SIGBUSed due to stale host nx caches (`.nx`, `node_modules/.cache/nx`, `.angular/cache`); after clearing and running with `NX_DAEMON=false` it compiled.

### Resulting state (all verified)
- **caddy :4000** (documented dev access point): frontend HTML 200 (title "Startuphafen"), `/styles.css` 200, `/trpc` proxied — `GET /trpc/FeatureFlags.getFeatureFlags` → 200 with 6 real DB rows, `/kc-admin` 302 (Keycloak admin console, admin/admin), `/kc` login flow with the startuphafen theme ("Anmeldung bei startuphafen").
- **backend :5000** (inside devcontainer): log `pgvector extension successfully enabled`, `All migrations have been successfully applied` (57 migrations), `[ ready ] http://0.0.0.0:5000`; root `GET /` → 200.
- **frontend :4201** (inside devcontainer): `Angular Live Development Server is listening on 0.0.0.0:4201`, `Compiled successfully`.
- **keycloak :28080** (host-published): JWKS `…/realms/startuphafen/protocol/openid-connect/certs` 200; password grant logins alice (roles `user`,`activatedUser`) and admin (admin-cli) → 200 Bearer tokens.
- **database:** 13 tables (FeatureFlag, Project, Answers, ShUser, VectorEmbedding, ChatSession, …), `_prisma_migrations`=57.
- **pgadmin :3838** 302; **maildev :1080** up (SMTP 1025 as configured; the compose healthcheck `/healthz` 404s on the v3 image, hence "unhealthy" status — cosmetic).

### Access points
- Development URL: `http://localhost:4000` (caddy); Keycloak admin `http://localhost:4000/kc-admin`; keycloak direct `:28080`; pgadmin `:3838` (pgadmin@example.com / secret); maildev `:1080`.
- Dev logins (per README): admin/admin (realm + app admin), alice/alice (activated), marie/marie (first-login flow).
- Restart: `docker compose -f /workspace/.devcontainer/dev-fixed.yml up -d`, then in `startuphafen-devcontainer`: `npm run back` and `npm run front` (or `npx nx serve startuphafen-frontend` with `NX_DAEMON=false`).

### Incomplete/out-of-scope (documented in the release notes)
No strapi/ERiC/OZG/Mistral credentials (placeholders/dev mode only); chatbot & HWK pre-check disabled without a Mistral key; ERiC gateway/ELSTER certificate, strapi content, PLZ mapping, and HWK form left as placeholders by design. The maildev healthcheck mismatch is cosmetic.