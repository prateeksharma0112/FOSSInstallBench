# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** Badge API

**Description:** The badge program checks openCode repositories and awards badges that are displayed in the openCode software directory.

## Supplied installation guide

## Guide: Installation.md

# Badge API

The Badge API evaluates various project metrics fetched from a git provider (currently only gitlab is supported) and assigns corresponding badges to the project. Each badge can be tied to specific conditions, such as project maintenance, reuse, compliance, or open-source status.

Checkout the [releases](https://gitlab.opencode.de/open-code/badgebackend/badge-api/-/releases) for details on the latest version and changes.

## Configuration

The badge api is configured using a yaml configuration file with the name `.badge-api.yaml`. The program looks for this file in the current working directory and inside `/etc/badge-api/`.

In order to allow a flexible configuration of the API the actual configuration is available [here](https://gitlab.opencode.de/open-code/badgebackend/badge-config). The config will automatically be reloaded every few minutes from the remote location/server.

The documentation for the configuration can be found [here](https://badges.opencode.de/concepts/configuration/).

## Development

1. Launch Backend

- Optional: Launch Database: `docker compose up -d postgresql`
- `cp .env.example .env`
- Go through defined platforms in `.badge-api.yaml` -> `gitClients`
  - `cp secrets/glpat.secret.example secrets/glpat.secret`
  - Generate token: [Docs](https://gitlab.opencode.de/-/user_settings/personal_access_tokens)
    - Scope: `read_api`
- For GitHub generate a token here: [tokens](https://github.com/settings/tokens) (No extra permissions).
- `make run`

2. Optional: Run checks via CLI

- `go run main.go check --help` Show help for all available commands
- `go run main.go check --repository "https://gitlab.opencode.de/open-code/badgebackend/badge-api"` Run check for a given repository
- `go run main.go check --all-repositories https://gitlab.opencode.de` Run checks for all repositories for a given GitLab Instance
- `REMOTE_CONFIG_URL="https://gitlab.opencode.de/open-code/badgebackend/badge-config/-/raw/my-fancy-branch-name/" go run main.go check --repository "https://gitlab.opencode.de/open-code/badgebackend/badge-api"` override the REMOTE_CONFIG_URL

3. Run Demo Frontend

- Checkout [Documentation Repo](https://gitlab.opencode.de/open-code/badgebackend/gitlab-profile)
- npm i && npm run dev
  - Open locally: http://localhost:3000/de/#api-small-demo

4. Speedup testing by running local nginx cache:

- `docker compose up cache`
- Run using `NGINX_OPENCODE_PROXY=true go run main.go check --all-repositories https://gitlab.opencode.de`
- Clear cache: `sudo rm -R ./dev/nginx-cache/*`
- Or in short: `sudo rm -R ./dev/nginx-cache/* ; docker compose up cache`

5. Generate mocks if necessary

- `make mocks`

6. Tests

- Run tests using VSCode Testing Suite

7. Linting (Optional)

- Install [golangci-lint](https://golangci-lint.run/docs/welcome/install/local/)
- `golangci-lint run`

8. Performance Profiling

- Set Env Variable `ENABLE_PROFILING=true`
- Run program
- Open results in browser: `go tool pprof -http=:6060 cpu.prof`

## Deployment (currently, to be changed in future)

1. Clone Repository: `git clone git@gitlab.opencode.de:open-code/badgebackend/badge-api.git && cd badge-api`
2. Create pull secret for private docker registry: `kubectl create secret docker-registry regcred --docker-server=registry.opencode.de --docker-username='<name>' --docker-password='<key>' -n <your-namespace>`
3. Modify the values file in the helm-chart folder. Pay special attention to the `config` and `secretMounts` sections.
   - The secretFileMounts section is used to mount any tokens needed for git providers into the pod.
   - **The secretFileMounts and the config section must match in file paths!**
4. Install with helm: `helm install badge-api ./helm-chart`

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

## Installation: Badge API (openCode badge backend)

**Workspace:** `/workspace` (repo checked out at the pinned SHA; root of the badge-api Go module `gitlab.opencode.de/open-code/badgebackend/badge-api`). All work was done as root inside the active container (Ubuntu 22.04, x86_64, Docker Engine 29.7.2 present).

### Prerequisites installed (not present initially)
- **Go 1.26.4** (required by `go.mod`): downloaded `go1.26.4.linux-amd64.tar.gz` from https://go.dev/dl/, SHA256 verified against the official release list (`1153d3d5…ad7f`), extracted to `/usr/local/go`, symlinked `go`/`gofmt` into `/usr/local/bin`, PATH export appended to `/root/.bashrc`. `go version` → `go1.26.4 linux/amd64`.
- **make** (used by `make run`): `apt-get update && apt-get install -y make` → GNU Make 4.3 at `/usr/bin/make`.

### Build
- `cd /workspace && go mod download` (exit 0) and `go build -o badge-api -ldflags -w -trimpath main.go` (exit 0) → binary `/workspace/badge-api` (88,406,058 bytes).

### Configuration (per guide)
- `cp .env.example .env` → `/workspace/.env` (POSTGRES_*, DEVGUARD_FRONTEND/BACKEND).
- `cp secrets/glpat.secret.example secrets/glpat.secret` (and the same for `glpat-dev.secret` / `ghpat.secret` covering all `gitClients` in `.badge-api.yaml`).
- **Deviation required for operation:** with the placeholder token `glpat-XXX`, the app's mandatory remote-config fetch failed (`GET …/api/v4/projects/open-code%2Fbadgebackend%2Fbadge-config/repository/files/… : 401`) and the program panicked (`panic: no config loaded`). Verified that gitlab.opencode.de's API allows **unauthenticated** reads of public projects, so the three token files were written **empty**; with that, config and all remote resources load. A real GitLab PAT (`read_api`) or DevGuard credentials would be needed for full-fidelity checks (e.g., `members/all`, DevGuard CVE lookups), which warn gracefully in their absence.
- Optional PostgreSQL (`docker compose up -d postgresql`) was **not** started — the guide marks it optional; `serve` does not require it (DB saving is only used by `check` and can be disabled via `SKIP_SAVE_TO_DATABASE=true`).

### Running instance (final method)
- `cd /workspace && make run` → `go run main.go serve` running in background as PID 21562/21596 (log: `/workspace/badge-api-serve.log`), listening on **:8080**.
- Log confirms: remote config fetched from `https://gitlab.opencode.de/open-code/badgebackend/badge-config/-/raw/main/.badge-api.yaml`, 17 badge SVGs fetched and cached (e.g., `/api/v1/svg/670fe48085aeeb75978b299f6c0a40ff.svg`), "starting config refresher each 10 minutes", "starting server port=8080".
- API surface: `GET /api/v1/info`, `GET /api/v1/repositories/{url}/sarif`, `GET /api/v1/repositories/{url}/badges/{badgeID}[/sarif]`, `GET /api/v1/svg/{svgKey}`, `/metrics`.

### Verification
- `curl http://localhost:8080/api/v1/info` → **200**, JSON with gitClients + full remote badge definitions.
- `curl http://localhost:8080/api/v1/svg/670fe48085aeeb75978b299f6c0a40ff.svg` → **200**, real badge SVG content.
- `curl http://localhost:8080/metrics` → **200**.
- Documented CLI: `SKIP_SAVE_TO_DATABASE=true ./badge-api check --repository "https://gitlab.opencode.de/open-code/badgebackend/badge-api"` ran all badge observers against the live GitLab (expected 401 warnings only for `members/all` and DevGuard "token is empty", which continue without failing).

### State
- Server left running on :8080; built binary at `/workspace/badge-api`; log at `/workspace/badge-api-serve.log`; token files are empty (placeholder, no real credentials).

# ENVIRONMENT

You have access to the same container used for installation, including the files and dependencies left by the installation attempt. Each terminal call starts a fresh shell in `/workspace`. Shell-local directory changes, exported variables, and environment activation do not persist between calls. Include any required directory change, environment variables, or activation of an existing environment in each command.

# VALIDATION PROCEDURE

1. Review the guide and installation summary. Use the summary to locate the software and its components, and confirm the installation method, locations, and runtime context through inspection.
2. Identify the expected software behavior described in the guide and select checks appropriate to the resulting installation.
3. Run the checks in the correct directory and runtime environment. If needed, start the installed software within the boundaries below. Prefer evidence of software behavior over file existence alone.
4. Record the commands, observed results, and limitations. Assess the outcome using the definitions below and your own observations.

Distinguish the final installation method from abandoned attempts. Missing files required only by another installation method do not establish failure. A process not already running, or a timed-out or unavailable check, does not by itself establish failure.

# VALIDATION BOUNDARIES

You may inspect files, dependencies, processes and ports, run diagnostic commands, start or run the existing installation, and query local interfaces.

Do not install or update dependencies, build missing artifacts, perform missing setup or migrations, edit files or configuration, or repair the installation. Application startup and normal runtime file creation are permitted only when they do not perform these prohibited actions.

# OUTCOME DEFINITIONS

- `success`: Objective evidence obtained during validation demonstrates that the installation is complete and the software is operational according to the supplied guide.
- `failure`: Objective evidence obtained during validation demonstrates that the resulting installation is incomplete or cannot operate without further installation or repair work.
- `inconclusive`: The evidence is insufficient to establish either success or failure, including when observations are ambiguous or an environmental limitation prevents a reliable assessment.

# FINAL OUTPUT

Return the structured validation report with these three fields:

- `assessed_outcome`: Report `success`, `failure`, or `inconclusive` according to the definitions above.
- `outcome_evidence`: Record observable command results or execution evidence that directly support the assessed outcome. Include the exact command, working directory or runtime context, exit code where available, and relevant output for decisive checks. For an inconclusive assessment, record the observations or execution limitations preventing a decision.
- `assessment_summary`: Explain in detail what you inspected, how you performed validation, and how the observations support your assessment. Include checks that could not be completed, limitations, and unresolved uncertainty.