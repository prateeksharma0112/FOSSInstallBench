**Method used:** Docker Compose local deployment per Installation.md (the Kubernetes method was not used; no cluster available in this environment).

**Execution context:** Ubuntu 22.04 container, working directory `/workspace` (repository at commit `399b8b1`), Docker 29.7.2 with Compose v5.5.0, 8 CPUs / 7.6 GB RAM.

**Steps performed:**
1. Prerequisites: Docker, Docker Compose, Git, openssl were present. `jq` (required by `scripts/init.sh`) was missing and installed via `apt-get install -y jq`. Node.js on the host was not needed — all component Dockerfiles build inside `node:24` images.
2. `./scripts/init.sh` (in `/workspace`): copied `config-templates/` to `config/`, generated `.env` (service ports, Postgres/RabbitMQ credentials), injected secrets into all service configs, generated the Central Authority (`config/certificates/ca.crt` + `ca.key`), and user keys `config/admin.p12` (password `admin`) and `config/demo.p12` (password `demo`).
3. `docker compose build --parallel`: built all 26 service images from source in `/workspace/components/*`. Total build ~55 minutes; the slowest step was `npm ci` in the admin-front stage (~32 min) due to slow network. All images tagged `workspace-<service>:latest`.
4. `docker compose up -d`: started 20 containers (all services plus postgres, rabbitmq, redis).
5. **Recovery action:** the `event` container came up `unhealthy`. Diagnosis: it started before RabbitMQ was accepting connections (compose uses `service_started`, not a health condition); the AMQP reconnect path in `components/event/src/lib/message_queue/index.ts` schedules a fresh `init()` but never resolves the original connection promise, so `useRouter()` never ran and port 7004 was never bound (process idle at 0% CPU). Fixed with `docker compose restart event` after RabbitMQ became healthy — logs then showed `server-listening-started at http://0.0.0.0:7004` and the container became healthy.

**Final state:** all 20 containers `Up (healthy)` in `/workspace` (build log at `/workspace/build.log`).
- Admin panel: http://localhost:8082 (admin.p12, password `admin`)
- Cabinet: http://localhost:8081 (demo.p12, password `demo`)
- ID front: http://localhost:8080
- APIs: 8100 (id-api), 8101 (cabinet-api), 8102 (admin-api), 8103 (register), 8104 (external-reader), 8105 (filestorage)
- Example data files for later import exist in `/workspace/examples/` (register-100-10*.dat, workflow-1000.bpmn) but were not imported; that part of the guide is a manual browser exercise.