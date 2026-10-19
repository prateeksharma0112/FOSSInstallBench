**Method used:** The documented Linux installation from Installation.md: clone/checkout repository (already present at /workspace, commit 1d70807), ensure Docker service running, then `make run` in the repository directory. The Windows method (`windows_run.cmd`) was not applicable (environment is Ubuntu 22.04).

**Execution context:** Shared workspace container at /workspace, root user, Docker Engine-Community 29.7.2 (dockerd + containerd running) with Docker Compose plugin v5.5.0.

**Actions performed:**
1. Verified Docker prerequisite: `docker version` / `docker info` — engine 29.7.2 running, compose plugin available.
2. Installed missing prerequisite `make` (GNU Make 4.3) via `apt-get install -y make`, since the documented `make run` target requires it.
3. Ran the documented command `make run` from /workspace (backgrounded to /workspace/make_run.log). This executed `docker compose -f deployment/docker-compose.yml up --build`.
4. Build completed: image `blp-streamlit-pipeline:latest` (3.11 GB) built from the multi-stage Dockerfile (Python 3.13-slim, Poetry deps, PaddleOCR model preloading, ffmpeg/poppler-utils). Dockerfile note: first-run build takes a while, as the guide states.
5. Compose started container `deployment-streamlit-pipeline-1` (service name `streamlit-pipeline-1`), running `python3 -u -m streamlit run run.py` as appuser, port mapping 0.0.0.0:8501->8501/tcp.

**Final state / access point:**
- App is running: `http://localhost:8501/` (Streamlit UI of the SmartPlanAI building-plan digitization pipeline).
- Startup command for future use: `make run` (or `docker compose -f deployment/docker-compose.yml up --build`) in /workspace.
- Stop: `docker compose -f deployment/docker-compose.yml down` in /workspace.

**Known caveat (not an installation defect):** `docker ps` shows the container as `Up (unhealthy)`. The unhealthy status is caused by the Dockerfile HEALTHCHECK `CMD curl --fail http://localhost:8501/_stcore/health` — `curl` is not installed in the runtime image (`/bin/sh: 1: curl: not found`, exit 127). The application itself is healthy: external HTTP checks against both the root page and the health endpoint return 200, and the container log contains no errors/tracebacks.

**Incomplete/unknown state:** None. The build log at /workspace/make_run.log and `docker logs deployment-streamlit-pipeline-1` retain the full build/startup output.