Installed Audiominer (v2.4.0 repo, commit e962370) via the recommended Docker Compose **CPU** method described in Installation.md, working in `/workspace/deployments/example-opencode` with Docker 29.7.2 on an Ubuntu 22.04 host (8 CPUs / 7.6 GB RAM).

**Steps performed:**
1. Copied `.env-example` to `.env` and appended a placeholder `HF_TOKEN` (guide requires an HF token for model download; none was provided in the environment, so a placeholder was used).
2. Pulled the four required images from the private registry `registry.opencode.de/bpa/audiominer/audiominer/` — `web-service:latest`, `asr-service:latest`, `fs-watcher:latest` plus `library/redis:7`. Notably these pulled **anonymously** (no `docker login` was actually required; no auth stored in `/root/.docker/config.json`).
3. Started the stack with the exact documented command: `docker compose --env-file .env-example --env-file .env -f compose.yml -f compose.cpu.yml up -d`.

**Config fix applied (required for the `latest` image to function):** The `latest` image is **v2.5.1** while the repo/template is **v2.4.0**. The v2.5.1 ASR service reads a `presets:` config block; the example template `asr-service.cpu.default.yml` only contains the legacy `model_settings` block, so every job failed with `Preset default not found`. I appended a `presets:` section (id `default`, base `whisperx`, whisper large-v3 CPU options) to `deployments/example-opencode/asr-service.cpu.default.yml` — the only file modified in the repo (42-line addition).

**HF-token limitation:** The ASR service attempted to download the gated `pyannote/speaker-diarization-3.1` and `pyannote/segmentation-3.0` models, which returned **HTTP 401** (gated, require a real access-approved HF token; only a placeholder was available). The pyannote backend loads its model unconditionally, so I removed the `diarize` process step from the preset to let the core Whisper ASR produce transcripts. As a result, **speaker diarization is not active** in this instance; a real `HF_TOKEN` would enable it.

**Resulting running state (left up):**
- `audiominer-local-redis-1` (redis:7, 6379)
- `audiominer-local-web-service-1` (port 127.0.0.1:8090 → 8090) — public web UI
- `audiominer-local-asr-service-1` (port 127.0.0.1:8091 → 8090) — admin UI / ASR
- `audiominer-local-fs-watcher-1` — watches `watch/`, mounts to `/mnt`

**Access points / start commands:** public UI `http://localhost:8090`, admin UI `http://localhost:8091`, file workflow via `deployments/example-opencode/watch/` (drop audio/video → transcript written alongside). Restart: `docker compose --env-file .env-example --env-file .env -f compose.yml -f compose.cpu.yml up` (in `deployments/example-opencode`).