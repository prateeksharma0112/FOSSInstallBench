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