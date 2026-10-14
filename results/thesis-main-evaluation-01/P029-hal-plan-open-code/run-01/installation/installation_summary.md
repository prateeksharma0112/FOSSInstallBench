## HAL-Plan / Buildplace — Installation Summary

**Context:** Ubuntu 22.04 container, working directory `/workspace` (repository already checked out at target SHA). Docker Engine 29.7.2 present; no Node/pnpm preinstalled. Method used: **Manual Setup (Option 2)** from the guide, supplemented by repo `.env.defaults`, `scripts/setupDb.ts`, and `.devcontainer/` files. The Dev Containers method (Option 1) was not used because it requires the VS Code Dev Containers extension/UI.

**Prerequisites installed:**
- Node.js 24.15.0 → `https://nodejs.org/dist/v24.15.0/node-v24.15.0-linux-x64.tar.xz`, extracted to `/usr/local` (`node`, `npm` now in PATH).
- pnpm 11.2.2 → `npm install -g pnpm@11.2.2`.

**Backing services (Docker containers, running):**
- `postgis` — `postgis/postgis:17-3.5`, `0.0.0.0:5432->5432`, `POSTGRES_USER=postgres`, `POSTGRES_PASSWORD=postgrespw`, `POSTGRES_DB=ffy_dev`.
- `valkey-cache` — `valkey/valkey:8.1.4`, `0.0.0.0:6379->6379`, `maxmemory-policy allkeys-lru`.
- `valkey-queue` — `valkey/valkey:8.1.4`, `0.0.0.0:6380->6379`, `maxmemory-policy noeviction`, appendonly.

**Repository setup (in `/workspace`):**
- `cp .env.defaults .env`, then edited `.env`: generated random `SESSION_KEY` and `CRYPTO_SECRET` (32-byte hex via Node crypto), set `WEBAPP_DEV_USER_PW=devpassword123`, appended `VALKEY_PERSISTENT_SERVER=localhost` and `VALKEY_PERSISTENT_PORT=6380`.
- `pnpm install` (success, ~2m52s).
- `pnpm prisma generate` (Prisma client + Pothos types).
- `pnpm setupDb` → created databases `ffy_shadow`, `ffy_test` (ffy_dev created by container).
- `pnpm prisma migrate reset --force` → applied 7 migrations and ran the seed.
- `pnpm codegen` → generated GraphQL types and gql-tada output.
- Copied `web-ifc` wasm files into `web/public/web-ifc/` (per `.devcontainer/setup.sh`).

**Startup / access:**
- Start command: `pnpm dev` (currently running in background; log at `/tmp/dev.log`).
- App URL: http://localhost:3000 (HTTP 200). GraphQL endpoint at `http://localhost:3000/api/graphql`. Dev inspector on 127.0.0.1:9229.

**State:** Fully installed and running. No incomplete work in the documented dev path. Production build (`pnpm build`/`pnpm start`) was not exercised.