**Method used:** Primary documented installation path (non-docker): Node.js v24 + pnpm + self-managed PostgreSQL 15 with PostGIS, `pnpm install`, `pnpm run start`. The Docker Compose alternative was not needed.

**Environment:** Ubuntu 22.04 container (root), working directory `/workspace` (repo checkout at assigned SHA).

**Actions performed:**
1. **Node.js v24.22.0** (satisfies engines `>=24.0.0`): downloaded official `node-v24.22.0-linux-x64.tar.xz` from nodejs.org, verified SHA-256 (`cc2f601c…9e98` matches SHASUMS256.txt), extracted to `/usr/local/node-v24.22.0-linux-x64`, symlinked `node`/`npm`/`npx`/`pnpm`/`pnpx` into `/usr/local/bin`.
2. **pnpm 11.1.2** installed via `npm install -g pnpm@11.1.2` (exact match of the `packageManager` field in `package.json`).
3. **PostgreSQL 15**: Ubuntu 22.04 repos only offer PG14, so the official PGDG apt repository (`apt.postgresql.org`, key `ACCC4CF8.asc`) was added; installed `postgresql-15` (15.19) and `postgresql-15-postgis-3` (PostGIS 3.6.4). An auto-pulled `postgresql-18` cluster (created by the `postgis` meta package) was left down; the required PG15 cluster `15/main` was created with `pg_createcluster 15 main --port=5432 --start` and is online on port 5432.
4. **Database setup** (per guide): `ALTER USER postgres WITH PASSWORD 'geobakery'` (matches `env.dev.sample` credentials); `CREATE EXTENSION IF NOT EXISTS postgis;` and `postgis_raster` created; sample data restored with `pg_restore --dbname=postgres --no-owner /workspace/sql/data` (83 MB custom-format dump). Exit code 1, but only a single non-fatal error: `unrecognized configuration parameter "transaction_timeout"` (a PG17+ setting embedded in the dump) — consistent with the guide's documented "warnings expected during restore" behavior. Tables in schemas `ga`, `ga_efa`, etc. confirmed restored.
5. **Configuration**: created `/workspace/.env.dev` as a copy of `.env.dev.sample` (points to `localhost:5432`, user `postgres`/`geobakery`, db `postgres`), as the guide instructs ("use the env.dev.sample file as a starting point").
6. **Dependencies**: `pnpm install` in `/workspace` completed successfully ("Done in 22s using pnpm v11.1.2").
7. **Service start**: `pnpm run start` (nest start) running as a background process (PID 6519 wrapper, nest server PID 6568); log shows `Nest application successfully started` with all routes mapped (v2/intersect, v2/transform*, v2/valuesAtPoint, v2/within, v2/nearestNeighbour, v2/topics, /health, /metrics) after successful TypeORM DB connection.

**Access points (service is currently running):**
- Swagger UI: http://localhost:3000/api
- OpenAPI JSON: http://localhost:3000/api-json
- Health: http://localhost:3000/health
- API: http://localhost:3000/v2/{topics,intersect,within,nearestNeighbour,valuesAtPoint,transformGeoJSONToEsriJSON,transformEsriJSONToGeoJSON}
- PostgreSQL: localhost:5432 (postgres/geobakery, PostGIS + postgis_raster, test data in `postgres` DB)

**Restart/start commands:** from `/workspace`: `pnpm run start` (compile+run), `pnpm run start:dev` (watch), `pnpm run start:prod` after `pnpm run build`; PostgreSQL started via `pg_ctlcluster 15 main start`.

**No incomplete work.** The Docker Compose route (`docker compose up`) remains available but was not exercised since the primary method succeeded.