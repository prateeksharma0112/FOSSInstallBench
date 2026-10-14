## Method used: Docker Compose local deployment (documented "Local startup")

Working directory: `/workspace` (repository checked out at commit `399b8b1`).

### Prerequisites resolved
- Docker Engine 29.7.2 and Docker Compose v5.5.0 were preinstalled and the daemon was running (`/var/run/docker.sock`, `overlay2` driver).
- `jq` was missing; installed via `apt-get install -y jq` (v1.6). `openssl` (3.0.2) was already present.
- Node.js/npm were not installed on the host, but this is not required since all builds occur inside Docker images (node:24).

### Steps performed
1. `chmod +x scripts/*.sh` then ran `./scripts/init.sh` (exit 0). This copied `config-templates` → `config`, generated `.env` with service ports and random DB/RabbitMQ secrets, injected credentials into all service config JSON files, generated a CA cert + key under `config/certificates/`, and created user PKCS#12 key files `config/admin.p12` (password `admin`) and `config/demo.p12` (password `demo`).
2. `docker compose build` — built all 26 images (all services plus migration and plugin-installer images). Took ~35 minutes; completed with all images tagged `workspace-*`.
3. `docker compose up -d` — started 20 containers (postgres:17, rabbitmq:3-management, redis, and 17 application services including migration/plugin-installer jobs which exited successfully after running).
4. Initial `event` service came up unhealthy because it started before RabbitMQ was ready and never opened port 7004. `docker compose restart event` resolved it (it then logged `server-listening-started` on 7004).

### Final state — verified
- `docker compose ps`: 20 running containers, all `(healthy)`.
- All API services respond HTTP 200 on `/test/ping`: admin-api:8102, cabinet-api:8101, id-api:8100, register:8103, external-reader:8104, filestorage:8105, persist-link:3346, sign-tool:3004, pdf-generator:7007, plus internal gateway:7003, manager:3002, notification:3003, task:3000.
- Frontends serve pages: admin panel at `http://localhost:8082` (title "Liquio Admin", HTTP 200), cabinet at `http://localhost:8081` (title "Liquio Cabinet", HTTP 200), id-front at `:8080` (HTTP 200).
- PostgreSQL databases created and migrated: bpmn (58 tables), id (14), notify (14), register (7), filestorage (5), persist_link (3).
- RabbitMQ has the expected `bpmn-*` queues declared by the services.
- Admin/demo certificate files present at `config/admin.p12` and `config/demo.p12`.

### Access points / startup commands
- Admin panel: http://localhost:8082 (key `config/admin.p12`, password `admin`)
- Cabinet: http://localhost:8081 (key `config/demo.p12`, password `demo`)
- Restart: `cd /workspace && docker compose up -d`
- Note: The example-process import and Playwright test steps from the guide require browser interaction and were not executed; the platform itself is fully deployed and healthy.

### Abandoned/not-attempted method
- Kubernetes (minikube/helm) installation was not attempted; minikube/kubectl/helm are not installed and the Docker Compose method is a fully documented and successful alternative.