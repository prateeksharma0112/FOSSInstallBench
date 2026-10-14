Installed and started TruSpace from /workspace at the checked-out commit using the documented local-dev workflow.

Method / working directory: /workspace (the shared installation workspace with the repository).

Steps:
1. Inspected environment: Ubuntu 22.04, Docker 29.7.2, Docker Compose v5.5.0, git/curl/openssl available, 8 CPUs, 7.6 GiB RAM, ~950 GiB free disk. Docker daemon reachable.
2. The guide directs the first run of ./start.sh to launch an interactive configuration wizard requiring the user to choose profile 1 (local-dev) and press ENTER. Because non-interactive execution is required, I ran the same documented configuration step non-interactively: `printf '1\n' | bash scripts/configure-env.sh`. This selected the local-dev profile, applied all preset defaults (BUILD_OR_PULL_IMAGES=build, ports 3000/8000/3333, AI enabled, malware scanning disabled, localhost/http), auto-generated JWT_SECRET and WEBUI_SECRET_KEY via openssl, and wrote /workspace/.env (exit 0).
3. Ran the documented start command `./start.sh` from /workspace in the background, logging to /tmp/start.log. It detected the existing .env, loaded it, created ./volumes/* directories, copied default terms, built the backend and frontend images locally (docker-compose.build.yml), pulled ipfs/kubo v0.42.0, ipfs/ipfs-cluster v1.1.6, and ghcr.io/open-webui/open-webui:0.10.2-ollama, then started all services via `docker compose -f docker-compose.yml -f docker-compose-frontend.yml -f docker-compose-ai.yml -f docker-compose.build.yml up -d ipfs0 cluster0 webui backend frontend`.
4. start.sh completed its IPFS readiness loop ("✔ IPFS API is ready") and the script finished.

Final state: All 5 containers running — truspace-frontend (0.0.0.0:3000), truspace-backend (0.0.0.0:8000), ipfs0 (healthy; 5001/8080/4001), cluster0 (9094/9096/9097), workspace-webui-1 (healthy; 3333->8080). Persistent data stored under /workspace/volumes/.

Access points: Frontend http://localhost:3000, API http://localhost:8000/api, Open WebUI http://localhost:3333, IPFS API http://localhost:5001.

Known caveats: The interactive wizard itself was not driven via stdin prompts; instead the underlying configure-env.sh was executed directly with the default local-dev selection, then start.sh used the generated .env. No other installation method was attempted (this single documented method succeeded).