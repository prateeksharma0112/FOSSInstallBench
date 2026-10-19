## Execution context
Shared workspace `/workspace` (repo `gitlab.opencode.de/stadt-menden/erlebnis.stadt` at commit `e5a8336`), Ubuntu 22.04 container with Docker/Podman (compose v5.5.0), running as root.

## Method: followed Installation.md for all three components (backend, app, cms)

### 1. Prerequisites installed
- Node.js 22.23.3 via NodeSource apt repo + npm 10.9.9; pnpm 10.20.0 via corepack (app requires pnpm@10.20.0, cms pnpm@10.17.1 — 10.20.0 satisfies both)
- OpenJDK 21 via apt (per guide's JDK 21 requirement)
- Docker compose already present

### 2. Backend (per backend/README.md) — COMPLETED AND RUNNING
- `cd /workspace/backend/docker && docker compose up -d` → 5 containers up: menden-backend-postgres (healthy, port 5432), menden-backend-keycloak (healthy, port 8090), menden-backend-meilisearch (port 7700, health 200 with masterKey), menden-backend-localstack (port 4566, health 200), poi-test-api (wiremock, port 3000, healthy)
- First `./gradlew help` on JDK 21 failed: "Could not resolve io.swcode.urbo.buildlogic:logic:1.0.56 — Dependency requires at least JVM runtime version 25. This build uses a Java 21 JVM." (guide says JDK 21; repo CI `backend.yml` sets javaVersion "25")
- Installed Amazon Corretto 25 to `/opt/java25` and re-ran: `cd /workspace/backend && JAVA_HOME=/opt/java25 ./gradlew :menden-app:bootRun --no-daemon` → build succeeded, log `/tmp/bootrun.log`: `Tomcat started on port 8080 (http)`, `Started MendenCmsApplicationKt in 39.151 seconds`; app connected to Postgres, imported 75 events, configured Meilisearch indexes
- Backend Maven deps resolved from public S3 repo (urbo-maven.s3.eu-central-1.amazonaws.com) — no GitHub token required at this commit; guide's token section for backend is outdated (referenced file `buildSrc/src/main/kotlin/io/swcode/menden/common-conventions.gradle.kts` does not exist at this commit)
- Currently running: Java PID 10139 with `io.swcode.menden.cms.app.MendenCmsApplicationKt`

### 3. Frontends (per app/README.md and cms/README.md) — FAILED
- `cd /workspace/app && pnpm install --frozen-lockfile` → exit 1: `ERR_PNPM_FETCH_401 GET https://npm.pkg.github.com/download/@sw-code/urbo-core/2.0.268/3b99378d594249f34d24ea1ef24ff7630c914acc: Unauthorized - 401` (after downloading 1700+ public packages)
- `cd /workspace/cms && pnpm install --frozen-lockfile` → same 401 on private `@sw-code/*` packages
- Both `.npmrc` files contain only `@sw-code:registry=https://npm.pkg.github.com` without an `_authToken` line; guide requires adding a GitHub PAT (env `GITHUB_TOKEN` or in `.npmrc`) — no token exists in environment or repository
- Verified no alternative: `registry.npmjs.org/@sw-code/*` → 404 for all 5 probed packages; unauthenticated `npm.pkg.github.com` metadata/tarball → 401; GitHub org `sw-code` public repos (package-dist, public-packages, urbo-registry) do not serve these npm packages
- Result: `pnpm nx serve erlebnis.stadt`, `pnpm nx build erlebnis.stadt`, and `pnpm start` (cms) cannot be executed; `node_modules` in both workspaces are partially populated and incomplete

## Access points (backend, running)
- API: http://localhost:8080 (e.g. `GET /v1/feature-collection/experiences` → 200)
- Keycloak admin: http://localhost:8090 (admin/admin)
- Meilisearch: http://localhost:7700 (key: masterKey)
- Postgres: localhost:5432 (postgres/postgres, DBs: urbo, keycloak)
- LocalStack S3: localhost:4566; WireMock test API: localhost:3000

## Incomplete/unknown
- Frontend dependencies not installed (missing GitHub PAT — EXTERNAL_RESOURCE); frontend serve/build unverified. The guide's documented method is correct; it simply cannot proceed without the credential it declares as a prerequisite.