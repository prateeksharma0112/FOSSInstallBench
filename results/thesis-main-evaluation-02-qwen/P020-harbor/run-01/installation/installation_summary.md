**Method used:** Manual Docker Compose deployment from the guide's "Manual Start" section (equivalent to the documented `task dev:release:up IMAGE_REPO=...` remote-images path, executed as non-interactive `up -d` rather than foreground `up`), pulling pre-built images from the remote registry 8gears.container-registry.com/8gcr/ at tag v2.15.0 (the tag from `.env.example`).

**Working directory / context:** Repository at `/workspace` (8gears Harbor fork, commit d9bf927). All compose commands run from `/workspace/deploy/compose/example/local/` using `docker compose -f ../../docker-compose.yaml --env-file .env`. Runs as root inside the container; Docker Engine 29.7.2 with Compose v5.5.0 (prerequisites met).

**Actions performed:**
1. Copied `.env.example` → `.env` in `/workspace/deploy/compose/example/local/` and set `IMAGE_REPO=8gears.container-registry.com/8gcr/` to pull remote images (no pre-built local images existed).
2. Created `/workspace/deploy/compose/config/` (absent in the fresh checkout; the guide omits the `mkdir -p` that the Taskfile's `gen:private-key:local` performs) and generated the 4096-bit RSA token key at `/workspace/deploy/compose/config/token_service_key.pem` per the guide's openssl commands, chmod 644.
3. `docker compose pull` — all 9 images (harbor-portal/core/jobservice/registryctl/registry, trivy-adapter, harbor-exporter v2.15.0, postgres:16-alpine, valkey:8) pulled successfully.
4. `docker compose up -d` — stack started; project name `harbor-local`.

**Final state (verified):** All 9 containers `Up ... (healthy)`: core, exporter, jobservice, portal, postgresql, redis, registry, registryctl, trivy-adapter. Portal publishes 0.0.0.0:80→8080 and 443→8443.

**Access points:** UI/API at http://localhost with `admin` / `Harbor12345` (TLS disabled via `/dev/null` mounts, as designed). Registry push/pull endpoint: `localhost:80`.

**Known commands:** Stop: `docker compose -f ../../docker-compose.yaml --env-file .env down` (keep data) or `down -v` (destroy volumes), run from `/workspace/deploy/compose/example/local`.

**Incomplete/unknown:** None. The optional mkcert HTTPS setup was not done (TLS intentionally disabled per the local dev configuration).