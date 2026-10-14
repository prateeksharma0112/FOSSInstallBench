Installed Harbor v2.15.0 locally using the guide's manual Docker Compose method, pulling images from the documented remote registry 8gears.container-registry.com/8gcr/ (the guide's `task` CLI was not preinstalled, so its equivalent manual commands were used). Working directory: /workspace.

Actions:
- Verified Docker Engine 29.7.2 / Compose v5.5.0, openssl, free ports 80/443, sufficient disk/memory.
- Confirmed all 7 required Harbor images exist at tag v2.15.0 in 8gears.container-registry.com/8gcr/.
- Generated deploy/compose/config/token_service_key.pem via openssl (RSA 4096, traditional format) and chmod 644.
- Created deploy/compose/example/local/.env from .env.example with IMAGE_REPO=8gears.container-registry.com/8gcr/ (HARBOR_TAG=v2.15.0, TLS disabled via /dev/null mounts).
- Pre-pulled the 7 images, then ran: docker compose -f ../../docker-compose.yaml --env-file .env up -d (from deploy/compose/example/local).

Result: all 9 containers up and healthy (portal, core, jobservice, registry, registryctl, trivy-adapter, exporter, postgresql, redis). Harbor UI/API at http://localhost with admin/Harbor12345. Stack left running. No incomplete work.

Access points: http://localhost ; API http://localhost/api/v2.0/ping. Stop with `docker compose -f ../../docker-compose.yaml --env-file .env down` (add -v to drop volumes).