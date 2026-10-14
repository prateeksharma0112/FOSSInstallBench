## URBO installation summary

**Final method (successful):** the documented `just up` workflow, run as `URBO_INSTANCE=urbo GITHUB_TOKEN=dummy-token-for-build just up --detach` from `/workspace`.

**Context / environment:** Ubuntu 22.04 container, root, Docker Engine 29.7.2 daemon reachable, 8 CPUs, ~7.6 GB RAM. Network reachable to npmjs, github.com, deb.nodesource and the public S3 Maven repo; GitHub Packages (`maven.pkg.github.com` / `npm.pkg.github.com`) returns 401 without a token. No GITHUB_TOKEN was available in the environment.

**Prerequisites installed (not present in base image):**
- `just` 1.42.4 → `/usr/local/bin/just`
- Node.js 24.21.0 (NodeSource apt repo); npm 11.19.0
- pnpm 12.11.2 (`npm i -g pnpm`)
- `libatomic1` (pnpm launcher dependency)
- OpenJDK 21 (`openjdk-21-jdk-headless`) — required by the frontend `prepare` script because `openapi-generator-cli` shells out to `java`

**Actions performed:**
1. Ran `just doctor`; only `GITHUB_TOKEN` failed the preflight.
2. First attempt: fixed `libatomic1`, then re-ran `just up`. Next failure was the frontend `prepare` step (`java: not found`) — installed JDK 21.
3. Re-ran `just up`; Nx aborted with a corrupted SQLite cache (`FOREIGN KEY constraint failed`). Cleared `/workspace/app/.nx/workspace-data` and the Nx daemon.
4. Re-ran `just up --detach` with a dummy token — all four steps completed: frontend deps installed, backend image built (10m33s, Gradle `bootJar` inside Docker), containers started healthy, sample data seeded (39s).
5. Wrote `/workspace/.urbo-instance` = `urbo` so `just status`/`just urls`/`just serve` address the running instance.
6. Started the host dev servers (`pnpm nx serve app|cms|urboards --configuration=instance …`); `cms` and `boards` came up (HTTP 200 on 44541/46277). The `app` dev server completed its build but the Nx process exited; it was confirmed to serve correctly when launched directly.

**Resulting state (verified):** all stack containers healthy (`spring-app`, `keycloak`, `localstack`, `sendinblue-api`, `mailpit`, `postgres`, `meilisearch`, `imgproxy`, `sample-images`) plus the shared `urbo-proxy` on port 80. Backend `/v3/api-docs` and swagger-ui return 200; MeiliSearch health `available`; Keycloak `/realms/master` 200; sample data import completed successfully and the seeded marker written.

**Notable finding:** despite the guide requiring a classic PAT with `read:packages`, the backend image built fine with a dummy token — the build-logic plugin is served from the credential-free public S3 Maven repo and all `@sw-code/*` npm packages are workspace links, so no authenticated registry was actually used.

**Paths:** repo `/workspace`; instance state `/workspace/.urbo/urbo/` (env, nginx.conf, ports.json, seeded, logs); identifier file `/workspace/.urbo-instance`.

**Incomplete/unknown:** the execution sandbox's shell backend became permanently unreachable about an hour after startup (repeated Podman/SSH handshake errors), preventing a final repeat check of the `app` dev server and the proxy-fronted frontends. All core containerised services were already verified healthy and serving before that point.

**Access points / startup commands:** `just up` (or `just up --detach` + `just serve`); URLs `http://app|cms|boards|api|keycloak|meilisearch|...​.urbo.localhost` (see `just urls`); Postgres on host port 32768.