## Method
Docker Compose development stack (guide section "Docker Compose (Development with Local HTTPS)"), run from `/workspace/deployment` with `docker compose -f docker-compose.dev.yml up -d --build`. Host: /workspace (Linux, Docker Engine 29.7.2, Compose v5.5.0, 8 CPU / 7.6 GB RAM). The production compose path was not used (requires an external Let's Encrypt domain).

## Actions performed
1. Created `/workspace/deployment/.env` from the documented values (README section 2.1) with generated secrets for `DJANGO_SECRET_KEY`, `DB_PASSWORD`, `QGIS_DB_PASSWORD`; superuser `admin`/`Admin!LocalDev123`; plus `QGIS_DB_USER`, `QGIS_PG_SERVICE_NAME`, `API_URL`/`PUBLIC_API_URL`/`PUBLIC_TILE_SERVER_URL` build args, and `DJANGO_ALLOWED_HOSTS` extended to `api.localhost,admin.localhost,app.localhost,files.localhost,qgis.localhost,tiles.localhost,localhost,127.0.0.1`.
2. Ran the build; images built: `qonnectra/db:dev`, `qonnectra/backend:dev` (also used for pg-error-parser and backend-wms), `qonnectra/frontend:dev`, `qonnectra/caddy:dev`, plus `qgis/qgis-server:3.44.7-noble`, `maptiler/tileserver-gl:v5.6.0`, `nginx:stable-alpine`.
3. Fixed repo defects blocking the documented flow (details in the report message): `deployment/postgres/Dockerfile` (PGDG source → `apt-archive.postgresql.org` because `apt.postgresql.org` dropped the bullseye suite), `deployment/postgres/init.sh` (conditional REVOKE of `model_permission`/`route_permission`), `deployment/docker-compose.dev.yml` (nginx volume mounts, qgis-server command rewrite, added `backend-wms` service).
4. Cleared the half-initialized `deployment/postgres/data` bind mount and restarted; DB re-initialized cleanly with PostGIS, pgRouting, dblink, pgcrypto extensions and the `qgis_user` role.
5. Backend startup ran compilemessages/collectstatic, 108 migrations, superuser creation, and `load_initial_data`.
6. Created a minimal valid empty `/workspace/deployment/tiles/germany.mbtiles` placeholder (documented as user-generated via Planetiler) so tileserver-gl starts; applied one-off `REVOKE ALL ON model_permission, route_permission FROM qgis_user`.

## Final state
`docker compose -f docker-compose.dev.yml ps`: all 9 containers Up — `qonnectra_db_dev` (healthy, port 5440→5432), `qonnectra_backend_dev`, `qonnectra_backend_wms_dev`, `qonnectra_frontend_dev`, `qonnectra_nginx_dev`, `qonnectra_qgis_server_dev` (healthy), `qonnectra_tileserver_dev` (healthy), `qonnectra_caddy_dev` (0.0.0.0:80/443), `qonnectra_pg_error_parser_dev`.

## Access points (via Caddy internal-CA HTTPS; verified from this sandbox with `curl --resolve <host>:443:127.0.0.1` since the sandbox DNS does not resolve `*.localhost`)
- Frontend: `https://app.localhost` (303 → `/login`, SvelteKit UI renders; login `admin` / `Admin!LocalDev123`)
- API: `https://api.localhost/api/v1/` (200); login at `POST /api/v1/auth/login/`
- Admin: `https://admin.localhost/admin` (302 → login)
- QGIS: `https://qgis.localhost/ows/?MAP=/projects/<project>.qgz` (WMS/WFS; requires `Authorization: Bearer <token>`; note bundled `test-project.qgz` is a 16-byte placeholder)
- Tiles: `https://tiles.localhost` (tilejson 200; no basemap tiles until real mbtiles generated with Planetiler)
- WebDAV: `https://files.localhost` (401 unauth, 207 PROPFIND auth)
- Database: `localhost:5440` (user `qonnectra_user` / pass in `.env`)

## Known gaps
- `germany.mbtiles` is an empty placeholder; generate real data with Planetiler per `deployment/README.md` for basemap rendering.
- WireGuard VPN service exists only in the production compose, not the dev stack (optional QGIS-Desktop DB access feature).
- Browser use of the HTTPS endpoints requires trusting Caddy's internal CA (`docker compose -f docker-compose.dev.yml exec caddy caddy trust`, documented).