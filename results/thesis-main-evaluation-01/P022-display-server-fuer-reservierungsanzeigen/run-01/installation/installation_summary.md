## Installation Summary

**Project:** display-server (Display Server für Reservierungsanzeigen) — FastAPI service serving HTML reservation pages from the Biletado booking API.

**Context:** Repository pre-checked-out at commit `fccc32f` in `/workspace`. Docker Engine 29.7.2 and Docker Compose v5.5.0 available. Python not present on host (not needed; containerized install).

**Method (per guide):** Docker Compose.
1. `docker compose build` in `/workspace` — built image `docker.io/library/display-server:latest` (167 MB). Dockerfile uses `python:3.13-slim` + `pip install -r requirements.txt` (fastapi 0.139.2, uvicorn 0.51.0, httpx 0.28.1, authlib 1.7.2, Jinja2 3.1.6) — all installed successfully.
2. `cp .env.example .env` in `/workspace`.
3. `docker network create shared-net` (compose file declares `shared-net` as external — this prerequisite is not mentioned in the guide).
4. `docker compose up -d` — container `display-server` started, port `127.0.0.1:8001->8001`.

**Observed startup behavior:** With placeholder `.env.example` values, the container starts but Uvicorn lifespan calls `auth.signin()` against `https://your_tenant-api.smart-city-booking.de/auth/signin`, producing `httpx.ConnectError: [SSL: CERTIFICATE_VERIFY_FAILED] ... self-signed certificate` and `Application startup failed. Exiting.` This is inherent to needing real Biletado credentials (the guide states the booking platform must be available first).

**Verification / working state:** A minimal mock Biletado backend (implementing `/auth/signin`, `/auth/refresh`, `/{tenant}/bookables`, `/{tenant}/bookings`) was run temporarily on `shared-net`; `API_BASE_URL` was set to `http://mock-backend:8002/api`. The service then authenticated, completed startup (`Application startup complete.`), fetched data (`Updated bookings cache.`), and served pages: `GET /resources/Room-A` → 200, `GET /resources?ids=Room-A|Room-B` → 200 with rendered "Raumübersicht" HTML. Mock backend was removed and `.env` restored from `.env.example`; container stopped with `docker compose down` (image retained). NOTE: `docker-compose.yml` sets `BASE_PATH=/display-server`; direct root paths (`/resources/...`) nonetheless returned 200.

**Final method used:** Docker Compose (build + up). Abandoned attempts: none (the placeholder-credential startup failure was diagnosed, not a method failure).

**Access point / startup:** Configure valid Biletado credentials in `/workspace/.env`, then `docker compose up -d`; pages at `http://localhost:8001/resources/{resource}`. Logs: `docker compose logs -f`. Stop: `docker compose down`. Working dir: `/workspace`.