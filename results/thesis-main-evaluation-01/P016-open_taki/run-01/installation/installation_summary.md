## Method
Used the installation guide's primary documented method: deploy the prebuilt Docker image `codeberg.org/kosmos-eu/open_taki:latest` as a drop-in Apache Tika replacement (service name `tika`, port 9998).

## Environment / context
- Workspace (host-side repo checkout): `/workspace` (git commit `ba6891a`, module `codeberg.org/kosmos-eu/open_taki`).
- Runtime: Docker Engine 29.7.2 with Compose v5.5.0, running natively in the container. Network access to codeberg.org confirmed (HTTP 200). `go` and `podman` are NOT installed in this environment; the guide's podman-based restart commands were therefore executed with the Docker equivalent.
- Container: `workspace-tika-1` (service `tika`), image `codeberg.org/kosmos-eu/open_taki:latest` (394 MB), `0.0.0.0:9998->9998/tcp`, status Up.

## Actions performed
1. Explored the checked-out repo (`Dockerfile`, `go.mod`, `deploy.sh`, `config.yaml`, `main.go`, README/DEPLOYMENT docs).
2. Pulled the prebuilt image `codeberg.org/kosmos-eu/open_taki:latest` (digest sha256:c40b34fa...) successfully from codeberg.org.
3. Inspected the image: entrypoint `open_taki`, default cmd `/etc/open_taki/config.yaml`, exposed port 9998/tcp; bundled tools verified (`pdftotext`, `pandoc`, `python3`+PyMuPDF). Note: `ffmpeg` is NOT present in the prebuilt image.
4. Created `/workspace/taki-config.yaml` exactly per the guide (listen :9998; llm, collabora, whisper, embedding, pdf, fallback, routing sections). Note the guide's version says 0.7.0 while the current image is 0.9.0.
5. Created `/workspace/tika.yml` compose file with the `tika` service (image, config volume mount at `/etc/open_taki/config.yaml:ro`, restart always, port 9998, opencloud-net).
6. Launched with `docker compose -f /workspace/tika.yml up -d`; container started and logged `open_taki 0.9.0 starting on :9998`.

## Verification results (all passed)
- `GET /` → HTTP 200, JSON `{"name":"open_taki","version":"0.9.0","status":"ok","features":{"archive":true,"audio":false,"docmeta":true,"email":true,"image":true,"office":true,"pdf":true,"taki_v2":true},...}`.
- `GET /version` → `open_taki 0.9.0`.
- `PUT /rmeta/text` text/plain → Tika-style JSON, `X-TAKI:method: passthrough`.
- `PUT /tika/text` text/html → extracted via `pandoc`.
- `PUT /rmeta/text` application/pdf → extracted via `pdftotext` (2 pages).
- `PUT /rmeta/text` DOCX → extracted via `pandoc`.
- v2 protocol request (`X-Taki-Protocol: v2`, `X-Taki-Features: meta`, `X-Taki-Source-Ref`) → extended response incl. `X-TAKI:routing`.

## Incomplete / unknown state
- Optional enrichment backends (LLM at :8012, Collabora office conversion, Whisper, embedding/vector) are external services not provisioned here; their network calls fail as expected but do not affect core Tika-compatible extraction. `office` feature reports true because Collabora is configured, though it is unreachable.
- Video transcription (`ffmpeg`) will not work with the prebuilt image since ffmpeg is absent from it (present only in the repo's own Dockerfile).

## Access point / startup command
Start/stop: `docker compose -f /workspace/tika.yml up -d` / `down`. API: http://localhost:9998/ (health at `/`, version at `/version`, Tika endpoints `/rmeta/text`, `/tika/text`).