## Method used
Manual Setup (Option 2) from Installation.md, executed inside the shared container (Ubuntu 22.04, root) at the pre-cloned repo `/workspace`. Option 1 (Dev Containers) was not usable without VS Code, so the documented manual path was taken.

## Actions performed
1. **Toolchain**: Installed Node.js v24.15.0 (matches `engines` in package.json) from nodejs.org tarball into `/usr/local`; installed pnpm 11.2.2 via `npm install -g pnpm`; installed system lib `libatomic1` (required by the pnpm/node binaries).
2. **Docker services** (as per guide Option 2):
   - `docker run --name postgis -d -p 5432:5432 -e POSTGRES_PASSWORD=postgrespw postgis/postgis`
   - `docker run --name valkey-cache -d -p 6379:6379 valkey/valkey` (PubSub/cache)
   - `docker run --name valkey-queue -d -p 6380:6379 valkey/valkey` (BullMQ queue, noeviction)
3. **Dependencies**: `pnpm install` in `/workspace` (first attempt died on a transient registry fetch timeout at 1991/1995 packages; retried with `npm_config_fetch_timeout=600000` and completed: `Done in 1m 50s`). Copied `web-ifc*.wasm` files from `node_modules/web-ifc/` to `web/public/web-ifc/` (needed because `.npmrc` sets `ignore-scripts=true`; same step as `.devcontainer/setup.sh`).
4. **Environment**: Created `/workspace/.env` from `.env.defaults` with all required vars (DATABASE_URL/TEST/SHADOW pointing to localhost:5432, VALKEY_SERVER/PORT=6379, VALKEY_PERSISTENT_SERVER/PORT=6380, SESSION_KEY/CRYPTO_SECRET/STORAGE_KEY/STORAGE_SECRET generated with `openssl rand`, WEBAPP_DEV_USER_PW set).
5. **Database**: `pnpm prisma generate`; `pnpm setupDb` (created `ffy_dev`, `ffy_shadow`, `ffy_test`); `pnpm prisma migrate reset --force` (applied 7 migrations and ran the seed — users, scenarios, parcels, geodata, weather, EPSG projections).
6. **Codegen**: `pnpm codegen` — generated `shared/graphql/types.ts` and `api/lib/graphql/schema.graphql` successfully.
7. **Server**: `pnpm dev` running in background (log at `/tmp/dev.log`); Fastify log shows `Server listening at http://127.0.0.1:3000`, plus Vite dev client.

## Known access points / restart commands
- App + API: `http://localhost:3000` (restart: `cd /workspace && pnpm dev`)
- GraphQL: `POST http://localhost:3000/api/graphql`
- Auth (seeded dev user): `superadmin@buildplace.io` / `somepassword` (all seeded users use `somepassword`)
- Containers to keep running: `postgis` (5432), `valkey-cache` (6379), `valkey-queue` (6380)