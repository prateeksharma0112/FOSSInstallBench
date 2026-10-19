**Method:** Primary documented path — `cp .env.example .env`, set required vars, `docker compose up -d --build` in /workspace (Ubuntu 22.04 dind sandbox, WSL2 host, Docker 29.7.2, Compose v5.5.0).

**Environment setup:** Created `/workspace/.env` from `.env.example`; generated random `PAYLOAD_SECRET`/`HOCUSPOCUS_SECRET` (openssl rand -hex 32), kept default `NEXT_PUBLIC_HOCUSPOCUS_URL=ws://localhost:1234`, set `NEXT_PUBLIC_SERVER_URL=http://localhost:3020` (matching the published host port).

**Build:** `docker compose up -d --build` built the `web` image (Next.js 15.4.11 multi-stage: deps → builder with `npm run generate:types`, `generate:importmap`, `next build` → runner with volumes pre-created nextjs-owned) and the `hocuspocus` image (node:22-alpine, `npm install --omit=dev`); pulled `mongo:7` and `axllent/mailpit`.

**Environment obstacle + workaround:** All container creation initially failed: `runc create failed: ... cannot enter cgroupv2 "/sys/fs/cgroup/docker" with domain controllers -- it is in threaded mode`. Root cause: the sandbox itself runs in a cgroup namespace whose root cgroup (`/proc/self/cgroup` = `0::/docker`) is in cgroup-v2 "threaded" mode; minimal-test bisection showed `docker run --rm busybox true` succeeds while `docker run --rm --memory 1g busybox true` fails with the identical error — runc cannot write cgroup limit files in that state, and the compose files set `deploy.resources.limits.memory` on every service. Attempts to clear threaded mode (`echo 0 > cgroup.threads`) were silent no-ops from inside the namespace. Workaround: local-only override file `/workspace/docker-compose.noresources.yml` (same multi-file pattern as the guide's prod setup) with `deploy: !reset null` for all four services, started via `docker compose -f docker-compose.yml -f docker-compose.noresources.yml up -d`.

**Final state (running, loopback-only):**
- `workspace-web-1` — Up (healthy), 127.0.0.1:3020 → container :3000
- `workspace-hocuspocus-1` — Up, 127.0.0.1:1234 (board WebSocket, Hocuspocus v2.15.3 "Ready.")
- `workspace-mongo-1` — Up (healthy), 127.0.0.1:27019 → :27017
- `workspace-mailpit-1` — Up (healthy), 127.0.0.1:1025/8025 (dev mailcatcher)

**Known access points:** portal `http://localhost:3020` (Host: urbankit.de → /de), workspace login (Host: app.urbankit.de → /de/login), health `http://localhost:3020/api/health`, board WS `ws://localhost:1234`. To re-run the stack: `cd /workspace && docker compose -f docker-compose.yml -f docker-compose.noresources.yml up -d`.

**Not done (documented as optional/VPS-only):** production override `docker-compose.prod.yml` (Mongo root auth, un-published Mongo port, `restart: always`), demo-account seeding (`npm run seed:demo`), backup/restore scripts, external nginx/TLS for the urbankit.de domains — all out of scope for the base install in this environment.