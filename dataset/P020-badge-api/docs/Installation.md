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
