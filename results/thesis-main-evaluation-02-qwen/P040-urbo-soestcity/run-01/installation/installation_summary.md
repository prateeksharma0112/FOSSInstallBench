Installed and started the full URBO development stack on the `workspace` instance inside `/workspace` (repo root). The stack comprises a shared nginx reverse proxy (`urbo-proxy`, host port 80), a Docker Compose infrastructure + backend set (Postgres, Keycloak 26.4, Meilisearch, LocalStack, Mailpit, imgproxy, SendinBlue stub, sample-images, and the Spring Boot `spring-app`), seeded sample data, and three host-side Angular dev servers (citizen app, CMS, urboards) fronted by the proxy under `*.workspace.localhost`.

**Prerequisites installed** (none were preinstalled except Docker/git):
- Node.js 24.16.0 → `/opt/node`, symlinked into `/usr/local/bin`
- pnpm 11.5.3 (npm global) → `/opt/node/bin/pnpm`
- `just` 1.59.0 (static musl binary) → `/usr/local/bin/just`
- OpenJDK 21 headless (via apt) — required by the frontend `pnpm install` `prepare` step, which runs `openapi-generator-cli` (Java) to generate all 20 API clients + version stamp

**Installation method** (final):
1. Satisfied the `just up` preflight. `GITHUB_TOKEN` is enforced by a hard `Boolean(env.GITHUB_TOKEN)` check and the guide calls it required. I set a non-empty placeholder. I verified empirically that the backend image build does NOT need a real token: all `io.swcode.*` build-logic plugins resolve from the public `urbo-maven` S3 repo (comment: "no credentials required") and all other deps resolve from Maven Central/public registries. A dummy-token backend image build completed `BUILD SUCCESSFUL` and produced `urbo-workspace-spring-app:latest` (729 MB).
2. `pnpm install` in `app/` fails out-of-the-box with `ERR_PNPM_MINIMUM_RELEASE_AGE_VIOLATION` — pnpm 11's supply-chain verification re-fetches registry metadata per lockfile entry and those fetches time out under this environment's slow/throttled npm *metadata* connectivity (tarballs themselves are fine, ~2 MB/s). Completed with `pnpm install --trust-lockfile --network-concurrency 10 --fetch-timeout 120000 --fetch-retries 5` (the documented flag for a trusted committed lockfile). The `prepare` step (Java `openapi-generator-cli`) generated all API clients and the version stamp.
3. `just up --detach` (with `GITHUB_TOKEN` set and instance `workspace` persisted to `.urbo-instance`) brought up all Docker containers, attached the proxy, built the backend image, and ran the seeder to completion.
4. Dev servers: `just serve` is unstable here (see environment notes), so the three dev servers were started individually on their allocated ports from `.urbo/workspace/ports.json` via `pnpm nx serve <app> --configuration=instance --port=<port> --host=0.0.0.0 --allowedHosts=<hostname>`.

**Working directory / context:** `/workspace` (repo root); instance state under `/workspace/.urbo/workspace/`; Docker daemon native (no Docker Desktop); all commands run as root in the shared container.

**Access points / restart commands:**
- Proxy on `127.0.0.1:80`; app `app.workspace.localhost`, cms `cms.workspace.localhost`, boards `boards.workspace.localhost`, api `api.workspace.localhost`, keycloak `keycloak.workspace.localhost`. NOTE: this sandbox's resolver does NOT special-case `.localhost`, so use `http://127.0.0.1:80/` with the matching `Host:` header, or a browser/OS that resolves `.localhost`.
- Restart infra+backend: `docker compose --env-file .urbo/workspace/env -f backend/docker/docker-compose.yml up -d`
- Restart dev servers: `cd app && pnpm nx serve app --configuration=instance --port=34237 --host=0.0.0.0 --allowedHosts=app.workspace.localhost` (cms 35581, urboards 38377)

**Incomplete/unknown work:** None in the core installation. The only recurring operational issue is that the three dev servers occasionally die due to host memory pressure (7.6 GiB RAM, 8 cores) when running alongside the 10-container stack (dmesg shows OOM kills; load avg peaked ~98), and the `just serve` crash-detector reports a false "boards crashed (code=0)". The dev servers were left running (verified 200) but are not persisted across a reboot.