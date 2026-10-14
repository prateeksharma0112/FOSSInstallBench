## Erlebnis.Stadt Menden — installation attempt

Execution context: Ubuntu 22.04 container (podman), root, working dir `/workspace` at commit `e5a8336`. Nothing was preinstalled; Docker daemon was available.

### Prerequisites installed (not present initially)
- Node.js v22.23.2 extracted to `/opt/node`, binaries symlinked into `/usr/local/bin` (node/npm/npx/pnpm/pnpx/nx).
- pnpm 10.20.0 and nx 23.2.1 installed globally via npm.
- JDK 21 (`/opt/jdk21`) and JDK 25 (`/opt/jdk25`) downloaded from Adoptium; symlinked `/usr/local/bin/java`.

### Backend (Kotlin/Spring Boot) — installed and running
- Working dir `/workspace/backend`.
- The README claims a GitHub token and JDK 21 are required, but `settings.gradle.kts` resolves `io.swcode.*` artifacts from the public S3 maven repo `https://urbo-maven.s3.eu-central-1.amazonaws.com/releases` (HTTP 200), so no token was needed.
- The Gradle build actually requires **JDK 25** (README says 21). With JDK 21 the build failed configuring the root project: `Could not resolve io.swcode.urbo.buildlogic:logic:1.0.56 ... Dependency requires at least JVM runtime version 25`. The repo's `.github/workflows/backend.yml` confirms `javaVersion: "25"`. With JDK 25:
  - `./gradlew :menden-app:compileKotlin --no-daemon` → BUILD SUCCESSFUL.
  - `./gradlew :menden-app:bootJar --no-daemon` → produced `/workspace/backend/menden-app/build/libs/menden-app.jar` (174,324,581 bytes).
- `cd /workspace/backend/docker && docker compose up -d` started all documented services; `docker ps` shows postgres, keycloak, meilisearch, localstack, wiremock all up (keycloak/postgres/localstack/wiremock healthy).
- Ran `/opt/jdk25/bin/java -jar menden-app/build/libs/menden-app.jar`; Spring Boot started, ran Flyway migration, created Meilisearch indexes and imported events. `curl http://localhost:8081/health` returned `{"groups":["liveness","readiness"],"status":"UP"}`.

### Frontend `app/` and `cms/` — NOT installed
- Both `.npmrc` files set `@sw-code:registry=https://npm.pkg.github.com`. Dependencies include private `@sw-code/urbo-*` 2.0.268 packages.
- `cd /workspace/app && pnpm install --no-frozen-lockfile` failed: `ERR_PNPM_FETCH_401 GET https://npm.pkg.github.com/download/@sw-code/urbo-core/2.0.268/...: Unauthorized - 401`.
- `cd /workspace/cms && pnpm install --no-frozen-lockfile` failed identically on `@sw-code/urbo-backend-api`.
- The guide explicitly requires a GitHub Personal Access Token (`GITHUB_TOKEN`, scopes `read:packages`). No such token existed in the environment (env dump, `/run/secrets`, `~/.npmrc`, git config all checked). No public mirror exists: `registry.npmjs.org/@sw-code/urbo-core` → 404, GitHub Packages unauthenticated → 401, GitLab package registry for the project → `[]`.

### Final state
Backend installed, built, and running with its Docker infrastructure up. Web app and CMS could not be installed due to missing private GitHub Packages credentials. Known commands: backend jar run as above (API :8080, management/health :8081); frontend `cd app && pnpm install && pnpm nx serve erlebnis.stadt`; CMS `cd cms && pnpm install && pnpm start`.