# Etherpad

## Installation

### Quick install (one-liner)

The fastest way to get Etherpad running. Requires `git` and Node.js >= 24.

**macOS / Linux / WSL:**

```sh
curl -fsSL https://raw.githubusercontent.com/ether/etherpad/master/bin/installer.sh | sh
```

**Windows (PowerShell):**

```powershell
irm https://raw.githubusercontent.com/ether/etherpad/master/bin/installer.ps1 | iex
```

Both installers clone Etherpad into `./etherpad-lite`, install dependencies, and
build the frontend. When the installer finishes, run:

```sh
cd etherpad-lite && pnpm run prod
```

Then open <http://localhost:9001>.

To install and start in one go:

```sh
# macOS / Linux / WSL
ETHERPAD_RUN=1 sh -c "$(curl -fsSL https://raw.githubusercontent.com/ether/etherpad/master/bin/installer.sh)"
```

```powershell
# Windows
$env:ETHERPAD_RUN=1; irm https://raw.githubusercontent.com/ether/etherpad/master/bin/installer.ps1 | iex
```

### Docker-Compose

The official image is published to both Docker Hub (`etherpad/etherpad`) and GitHub Container Registry (`ghcr.io/ether/etherpad`) with identical tags. Use whichever suits your environment; GHCR avoids Docker Hub's anonymous pull rate limits.

```yaml
services:
  app:
    user: "0:0"
    image: etherpad/etherpad:latest  # or: ghcr.io/ether/etherpad:latest
    tty: true
    stdin_open: true
    volumes:
      - plugins:/opt/etherpad-lite/src/plugin_packages
      - etherpad-var:/opt/etherpad-lite/var
    depends_on:
      - postgres
    environment:
      NODE_ENV: production
      ADMIN_PASSWORD: "${DOCKER_COMPOSE_APP_ADMIN_PASSWORD:?Set DOCKER_COMPOSE_APP_ADMIN_PASSWORD to a strong value}"
      DB_CHARSET: ${DOCKER_COMPOSE_APP_DB_CHARSET:-utf8mb4}
      DB_HOST: postgres
      DB_NAME: ${DOCKER_COMPOSE_POSTGRES_DATABASE:-etherpad}
      DB_PASS: "${DOCKER_COMPOSE_POSTGRES_PASSWORD:?Set DOCKER_COMPOSE_POSTGRES_PASSWORD to a strong value}"
      DB_PORT: ${DOCKER_COMPOSE_POSTGRES_PORT:-5432}
      DB_TYPE: "postgres"
      DB_USER: ${DOCKER_COMPOSE_POSTGRES_USER:-admin}
      # For now, the env var DEFAULT_PAD_TEXT cannot be unset or empty; it seems to be mandatory in the latest version of etherpad
      DEFAULT_PAD_TEXT: ${DOCKER_COMPOSE_APP_DEFAULT_PAD_TEXT:- }
      DISABLE_IP_LOGGING: ${DOCKER_COMPOSE_APP_DISABLE_IP_LOGGING:-false}
      SOFFICE: ${DOCKER_COMPOSE_APP_SOFFICE:-null}
      TRUST_PROXY: ${DOCKER_COMPOSE_APP_TRUST_PROXY:-false}
    restart: always
    ports:
      - "${DOCKER_COMPOSE_APP_PORT_PUBLISHED:-9001}:${DOCKER_COMPOSE_APP_PORT_TARGET:-9001}"

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${DOCKER_COMPOSE_POSTGRES_DATABASE:-etherpad}
      POSTGRES_PASSWORD: "${DOCKER_COMPOSE_POSTGRES_PASSWORD:?Set DOCKER_COMPOSE_POSTGRES_PASSWORD to a strong value}"
      POSTGRES_PORT: ${DOCKER_COMPOSE_POSTGRES_PORT:-5432}
      POSTGRES_USER: ${DOCKER_COMPOSE_POSTGRES_USER:-admin}
      PGDATA: /var/lib/postgresql/data/pgdata
    restart: always
    # Exposing the port is not needed unless you want to access this database instance from the host.
    # Be careful when other postgres docker container are running on the same port
    # ports:
    #   - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
  plugins:
  etherpad-var:
```

### Requirements

[Node.js](https://nodejs.org/) >= 24.

### Windows, macOS, Linux

1. Download the latest Node.js runtime from [nodejs.org](https://nodejs.org/).
2. Install pnpm: `npm install -g pnpm` (Administrator privileges may be required).
3. Clone the repository: `git clone -b master`
4. Run `pnpm i`
5. Run `pnpm run build:etherpad`
6. Run `pnpm run prod`
7. Visit `http://localhost:9001` in your browser.

### Docker container

Find [here](doc/docker.md) information on running Etherpad in a container.
