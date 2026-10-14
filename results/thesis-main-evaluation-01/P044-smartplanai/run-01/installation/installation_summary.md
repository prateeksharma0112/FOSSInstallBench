## Method and context
Repository checked out at `/workspace` (commit `1d70807`). Installation followed the supplied guide's Linux method, `make run`, which executes `docker compose -f deployment/docker-compose.yml up --build`. This builds the image from `/workspace/Dockerfile` and starts a Streamlit container exposing port 8501.

## Actions performed
1. Inspected repo: `Makefile`, `Dockerfile`, `pyproject.toml`, `deployment/docker-compose.yml`, `README.md`.
2. Verified Docker prerequisites: Docker Engine 29.7.2, Compose v5.5.0, buildx 0.36.1 — all present and running.
3. `make` was NOT preinstalled; installed it via `apt-get install -y make` (GNU Make 4.3).
4. Ran the documented command in the background: `cd /workspace && nohup make run </dev/null >/tmp/build.log 2>&1 &` (PID 678).
5. Build ran (~7 min): installed Poetry + dependencies (streamlit, paddleocr 3.3.2, paddlepaddle 3.2.2, opencv, geopandas, etc.) and preloaded PaddleOCR German models; produced image `blp-streamlit-pipeline:latest` (3.11 GB).
6. Compose created container `deployment-streamlit-pipeline-1` and started it.

## Resulting state
- Image: `blp-streamlit-pipeline:latest` present.
- Container: `deployment-streamlit-pipeline-1` in `Up` state, 0 restarts, no errors/tracebacks in logs; Streamlit reports "You can now view your Streamlit app in your browser" at http://localhost:8501.
- Access point: http://localhost:8501 (host port 8501 -> container 8501).

## Known caveat (not an install failure)
Docker health status is `unhealthy`. Root cause is a bug in the image's HEALTHCHECK (`HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health`) combined with the runtime image not containing `curl`. `docker inspect ... .State.Health` shows `ExitCode: 127`, `Output: "/bin/sh: 1: curl: not found"`. The application endpoint itself responds correctly.

## Working directory
Build invoked from `/workspace`; compose file at `/workspace/deployment/docker-compose.yml` with build context `..` = `/workspace`. Build log at `/tmp/build.log`.

No alternative method was needed; the documented method succeeded.