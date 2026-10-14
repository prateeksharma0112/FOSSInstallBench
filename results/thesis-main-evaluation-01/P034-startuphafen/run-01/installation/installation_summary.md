## Installation of Startuphafen

**Context:** Ubuntu 22.04 container, Docker 29.7.2 (DinD) available, no Node.js/npm preinstalled. Repository checked out at /workspace (commit 868cad5, v2.0.0 release). The supplied guide ("Installation.md") documents the devcontainer-based developer setup: build the VS Code devcontainer from `.devcontainer/devcontainer.json` (which merges `apps/startuphafen-backend/src/assets/docker-compose.yml` and `.devcontainer/dev-compose.yml`), run `npm install`, then use `npm scripts front/back`.

**Method used (final):** Reproduced the documented devcontainer stack via Docker Compose directly (headless equivalent of building the VS Code devcontainer), then built and ran the app.

Steps:
1. Installed Node.js 20.18.0 to /opt/node20 (symlinked into /usr/local/bin) for the nx/Angular toolchain. Also installed Node.js 22.18.0 to /opt/node22 for the backend runtime.
2. `npm install` in /workspace (2636 packages).
3. `npx prisma generate` — Prisma Client v6.19.1 generated.
4. `docker compose -f apps/startuphafen-backend/src/assets/docker-compose.yml -f .devcontainer/dev-compose.yml up -d database keycloak keycloak-database maildev caddy pgadmin devcontainer` — built the `startuphafen-keycloak:26.1.2` image and the devcontainer image; all containers started.
5. `npx prisma migrate deploy` — "All migrations have been successfully applied" (57 migrations) against pgvector DB.
6. Built backend: `npx nx run startuphafen-backend:build:development` (webpack compiled successfully) and frontend: `npx nx run startuphafen-frontend:build:production` (dev build only failed on a component-style budget).
7. Created `apps/startuphafen-backend/src/assets/.localConfigs.json` per the guide (git check-ignore confirms it is ignored).
8. Started the compiled backend (`node dist/apps/startuphafen-backend/main.js`) and `nx serve startuphafen-frontend` inside the `startuphafen-devcontainer` compose service (hostnames used by the bundled Caddyfile.local are `devcontainer:5000` / `devcontainer:4201`), so the Caddy proxy on port 4000 can route to them.

**Running state (verified):** caddy(4000), database(pgvector pg15, healthy), keycloak-database(pg15 healthy), keycloak(26.1.2 healthy), maildev(1080), pgadmin(3838), devcontainer. Frontend, backend and Keycloak are all reachable via http://localhost:4000.

**Deviation from guide (required):** The Keycloak dev realm import crashed in a restart loop (`PasswordPolicyNotMetException: invalidPasswordMinSpecialCharsMessage`) because the realm `passwordPolicy` requires upper/lower/digit/special characters of length 8, while the realm's seeded passwords are `admin`/`alice`/`marie` (documented in the guide). Setting `passwordPolicy` to `""` in `.devcontainer/keycloak/imports/startuphafen.json` allowed the realm and all three users to import successfully; the container then reported healthy. This is the only tracked repository file changed.

**Abandoned attempt:** Running the backend directly on the host with Node 20 failed with `ERR_REQUIRE_ESM` (the ESM-only `@trpc-limiter/memory@1.0.0` required from CJS output). Node 22 (matching the deployment compose `node:22.18.0`) was used instead.

**Known/incomplete state:** MistralAI (chat/HWK-AI), Strapi, ERiC and OZG are unconfigured and the vector embeddings corpus is empty by design in the open-source release, as documented in the README. maildev's own healthcheck reports "unhealthy" because maildev 3.0.0 lacks a `/healthz` endpoint, though the service is up on 1080.
