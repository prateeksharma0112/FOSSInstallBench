**Goal:** Install/run UrbanKIT Plattform per the supplied deployment guide.

**Method used (final):** Docker Compose with the base `docker-compose.yml`, plus a locally added `docker-compose.override.yml` (see below).

**Working directory:** `/workspace` (the checked-out repo at commit `d170d74`).

**Environment:** Docker 29.7.2, Docker Compose v5.5.0, 8 CPUs, ~7.6 GiB RAM. Sandbox uses cgroup v2 with `/sys/fs/cgroup` in `domain threaded` mode and the `docker` cgroup in `threaded` mode.

**Steps performed:**
1. `cp .env.example .env`; set `PAYLOAD_SECRET` and `HOCUSPOCUS_SECRET` to local dev values. `NEXT_PUBLIC_SERVER_URL=http://localhost:3000` and `NEXT_PUBLIC_HOCUSPOCUS_URL=ws://localhost:1234` retained from the example.
2. `docker compose up -d --build` — built `workspace-web` (Next.js 15 + Payload 3 multi-stage image, ~2.5 GB) and `workspace-hocuspocus`; pulled `mongo:7` and `axllent/mailpit`. Build logs at `/workspace/compose_build.log`.
3. First container start failed: `runc create failed: unable to apply cgroup configuration: cannot enter cgroupv2 "/sys/fs/cgroup/docker" with domain controllers -- it is in threaded mode`. Repro'd with a minimal `docker run --rm -m 512m alpine echo ok` (also fails), while `docker run --rm alpine echo ok` (no limits) succeeds — isolating the cause to the `deploy.resources.limits` blocks in `docker-compose.yml` combined with the threaded cgroup hierarchy.
4. Added `/workspace/docker-compose.override.yml` resetting `deploy.resources.limits` for all four services (`!reset {}`). Re-ran `docker compose up -d` — all containers started.

**Resulting state (all verified):**
- `web` — Up, healthy, `127.0.0.1:3020 -> 3000`
- `mongo` — Up, healthy, `127.0.0.1:27019 -> 27017`
- `hocuspocus` — Up, `127.0.0.1:1234 -> 1234` (logs: "Hocuspocus v2.15.3 … Ready")
- `mailpit` — Up, healthy, `127.0.0.1:1025` / `127.0.0.1:8025`
- `curl http://localhost:3020/api/health` → `{"ok":true}` (HTTP 200)
- `Host: urbankit.de` → 307 to `/de` → HTTP 200 portal page; `Host: app.urbankit.de` → 307 to `/dashboard` → HTTP 200; `/admin` → HTTP 200; `/api/users` → HTTP 403 (Payload↔Mongo working, auth enforced).

**Startup/access commands:**
- Start: `cd /workspace && docker compose up -d` (no `--build` needed after first build)
- Access: web at http://127.0.0.1:3020 (admin at `/admin`), hocuspocus WS at ws://127.0.0.1:1234, mailpit UI at http://127.0.0.1:8025, Mongo at 127.0.0.1:27019.

**Abandoned/partial attempts:** The initial unmodified `docker compose up -d --build` built images but could not run any container due to the cgroup limit error; this was recovered from by the override file, not a separate installation method. The production override (`-f docker-compose.prod.yml`) and demo-account seeding were not exercised (not required to run the stack).

**Incomplete/unknown:** The `docker-compose.override.yml` is a sandbox-only adjustment not present in the upstream guide; remove it on a normal host if the memory limits are wanted.