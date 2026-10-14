Installed Qonnectra at /workspace (repo commit c07d840) using the guide's Docker Compose development method (docker-compose.dev.yml), after fixing repo/env blockers.

Context: Docker 29.7.2 / Compose v5.5.0, 8 CPU / 7.6 GB RAM. Working dir for all Compose commands: /workspace/deployment.

Method used (final): `docker compose -f docker-compose.dev.yml up -d` (images built earlier via `... build`). This is the guide's documented Method 2 (local HTTPS via Caddy internal CA). The guide's primary Quick Start (`docker compose up -d --build`, production compose) was attempted first and abandoned: every service defines deploy.resources memory limits, and the host runs cgroup v2 in threaded mode, so runc aborts with `cannot enter cgroupv2 "/sys/fs/cgroup/docker" with domain controllers -- it is in threaded mode`.

Fixes applied (files edited under /workspace/deployment):
- postgres/Dockerfile: base `postgis/postgis:17-3.5` (bullseye) → `postgres:17-bookworm`, installing postgresql-17-postgis-3 + postgresql-17-pgrouting from PGDG bookworm-pgdg (bullseye-pgdg repo was removed upstream, 404; and its pgrouting deb needs libstdc++6>=13.1 which bullseye lacks).
- postgres/init.sh: wrapped REVOKE on model_permission/route_permission with to_regclass guards (tables don't exist during first-time init).
- docker-compose.dev.yml: fixed nginx mounts (nginx.conf→/etc/nginx/nginx.conf, default.conf→/etc/nginx/conf.d/default.conf); replaced broken QGIS heredoc with printf; added missing backend-wms service required by nginx/default.conf.
- Created deployment/.env with local credentials, keys, domains; set API_URL=http://backend:8000/api/v1/ (internal) and rebuilt the frontend image.
- Installed OpenJDK 21 and generated base-map tiles with Planetiler (github release) into deployment/tiles/germany.mbtiles (documented prerequisite; repo ships no mbtiles).

Resulting state: 9 containers running (db healthy, backend, backend-wms, frontend, nginx, qgis-server healthy, tileserver healthy, pg-error-parser, caddy on 80/443). 108/108 migrations applied; postgis/pgrouting/dblink/pgcrypto created; admin superuser created. Entry points: https://app.localhost, https://api.localhost, https://admin.localhost/admin, https://qgis.localhost, https://tiles.localhost, https://files.localhost; DB also at localhost:5440.

Incomplete/unknown: QGIS projects dir holds only the 16-byte placeholder test-project.qgz (user-provided), so OGC requests with MAP return 500; tile data covers only Monaco.