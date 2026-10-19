## Method
Container-image deployment following the supplied guide (the only documented installation path for open_taki, which ships as a container image `codeberg.org/kosmos-eu/open_taki`). Docker was used in place of podman (podman not installed; Docker Engine 29.7.2 available and running in the shared Ubuntu 22.04 workspace at /workspace).

## Actions performed
1. **Explored workspace** (/workspace): open_taki source repository at commit ba6891a (Go 1.25, version 0.9.0 per `main.go`), with `Dockerfile`, `deploy.sh`, `config.yaml`. Docker daemon was running; the Codeberg registry `codeberg.org` was reachable and exposed `kosmos-eu/open_taki` tags: `latest`, `20260819-1601`, `20260819-2138` (the repo itself was renamed to `opentaki` upstream, with HTTP redirects, but the registry path in the guide still resolves).
2. **Pulled image**: `docker pull codeberg.org/kosmos-eu/open_taki:latest` → digest `sha256:c40b34fa00383e6d7e5d5f25279b0bbc8a7f16c86acf754b28c4e8c577dfc599`.
3. **Created `/workspace/taki-config.yaml`** (guide step 2, verbatim content: listen `:9998`, llm `http://your-llm:8012/v1`, collabora `http://collabora:9980`, whisper/embedding empty, pdf dpi 150/max 20, fallback, routing bleve_rules).
4. **Created `/workspace/tika.yml`** mirroring the guide's AFTER compose state: service name `tika`, image `codeberg.org/kosmos-eu/open_taki:latest`, volume `./taki-config.yaml:/etc/open_taki/config.yaml:ro`, network `opencloud-net`, `restart: always`, plus a host port mapping `9998:9998` so the guide's `curl http://localhost:9998/` verification works from the host.
5. **Started the service**: `docker compose -f tika.yml up -d tika` from /workspace → container `workspace-tika-1` created and running.

## Resulting state
- Container `workspace-tika-1` is **Up**, image `codeberg.org/kosmos-eu/open_taki:latest`, listening on `0.0.0.0:9998` (container port 9998 = service port per guide).
- Startup log: `open_taki 0.9.0 starting on :9998` (LLM: http://your-llm:8012/v1, Collabora: http://collabora:9980, Whisper: disabled, DocMeta: enabled).
- Access point: `http://localhost:9998/` (health), `PUT http://localhost:9998/rmeta/text` (Tika-compatible v1 extraction), v2 protocol via `X-Taki-Protocol: v2` header.

## Not executed (environment constraints, not part of the open_taki install itself)
- Guide steps 4 (OpenCloud-side) and 5: OpenCloud is not deployed in this environment, so the `opencloud search index --all-spaces --insecure` reindex and OpenCloud log check for "open_taki detected" were not run. The open_taki service itself (the software being installed) is fully installed and verified.
- No live LLM/Collabora backends exist here, so OCR/office conversion paths were not exercised; text and email extraction paths were tested instead.