# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** open_taki

**Description:** AI-powered document analysis as a drop-in replacement for Apache Tika: OCR, summarization, classification and transcription on your own infrastructure.

## Supplied installation guide

## Guide: Installation.md

## Quick Start

### 1. Replace Tika image in your compose

Edit `tika.yml` in your OpenCloud compose directory:

```yaml
# tika.yml — BEFORE
services:
  tika:
    image: apache/tika:latest-full
    networks:
      opencloud-net:
    restart: always

  opencloud:
    environment:
      SEARCH_EXTRACTOR_TYPE: tika
      SEARCH_EXTRACTOR_TIKA_TIKA_URL: http://tika:9998
      FRONTEND_FULL_TEXT_SEARCH_ENABLED: "true"
```

```yaml
# tika.yml — AFTER
services:
  tika:
    image: codeberg.org/kosmos-eu/open_taki:latest
    networks:
      opencloud-net:
    restart: always
    volumes:
      - ./taki-config.yaml:/etc/open_taki/config.yaml:ro
    logging:
      driver: ${LOG_DRIVER:-local}

  opencloud:
    environment:
      SEARCH_EXTRACTOR_TYPE: tika
      SEARCH_EXTRACTOR_TIKA_TIKA_URL: http://tika:9998
      FRONTEND_FULL_TEXT_SEARCH_ENABLED: "true"
```

Note: The service name stays `tika`, the URL stays `http://tika:9998`. OpenCloud doesn't know the difference.

### 2. Create taki-config.yaml

```yaml
# taki-config.yaml
listen: ":9998"

# LLM Backend — for PDF OCR, image description, meta extraction
# Point to any OpenAI-compatible API (vLLM, microllm, ollama, etc.)
llm:
  api_base: "http://your-llm:8012/v1"
  model: "local"
  max_tokens: 4096

# Collabora — office document conversion
# Uses the Collabora instance already in your OpenCloud stack.
# Handles: DOC, XLS, PPT, ODT, ODS, ODP and all LibreOffice formats.
# If not set, only pandoc-supported formats work (DOCX, ODT, EPUB, RTF).
collabora:
  url: "http://collabora:9980"

# Whisper — audio/video transcription (optional)
# Point to any OpenAI-compatible Whisper API.
whisper:
  api_base: ""  # e.g. "http://your-whisper:8019/v1"
  model: "whisper-large-v3"

# Embedding — for vector search (optional, used with v2 protocol)
embedding:
  api_base: ""  # e.g. "http://your-embed:8019/v1"
  model: "nomic-ai/nomic-embed-text-v1.5"

# PDF rendering settings
pdf:
  dpi: 150
  max_pages: 20

# pdftotext fast-path: skip LLM if pdftotext extracts enough text
fallback:
  min_chars: 200
  min_chars_per_page: 50

# Content routing (active with v2 protocol)
# Controls what goes into bleve fulltext index vs. vector-only.
# Everything always gets embedded for vector search.
routing:
  vector: always
  bleve_rules:
    # Documents → bleve (keyword searchable)
    - match:
        mime: ["application/pdf", "application/msword", "application/vnd.openxmlformats-*"]
      features: [meta, entities, summary]
    # Spreadsheets → bleve
    - match:
        mime: ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml*"]
      features: [meta]
    # Email → bleve
    - match:
        mime: ["message/*"]
      features: [meta, entities]
    # Text → bleve (cheap)
    - match:
        mime: ["text/*"]
      features: []
    # Images, audio, video → vector only (no bleve bloat)
    # Project spaces → override: everything to bleve
    - match:
        space_type: ["project"]
        mime: ["*"]
      features: [meta, entities, summary]
```

### 3. Restart

```bash
cd /your/opencloud/compose
podman compose down tika opencloud
podman compose up -d tika opencloud
```

### 4. Verify

Check OpenCloud logs for:
```
open_taki detected (version: 0.7.0), using v2 protocol
```

Check taki health:
```bash
curl http://localhost:9998/
# → {"name":"open_taki","version":"0.7.0","features":{"office":true,"pdf":true,...}}
```

### 5. Reindex (optional)

```bash
podman exec opencloud-1 opencloud search index --all-spaces --insecure
```

---

## Architecture

### Minimal setup (PDF + text only)

```yaml
# Just LLM, no Collabora needed
llm:
  api_base: "http://your-llm:8012/v1"
```

Handles: PDF (pdftotext + LLM OCR), DOCX/ODT/EPUB/RTF (pandoc), HTML, email, archives, plain text.

### Recommended setup (full office support)

```yaml
llm:
  api_base: "http://your-llm:8012/v1"
collabora:
  url: "http://collabora:9980"
```

Adds: DOC, XLS, PPT, and all other LibreOffice-supported formats via Collabora's `/cool/convert-to` API. Collabora is already part of most OpenCloud deployments.

### Full setup (with audio + vector)

```yaml
llm:
  api_base: "http://your-llm:8012/v1"
collabora:
  url: "http://collabora:9980"
whisper:
  api_base: "http://your-whisper:8019/v1"
embedding:
  api_base: "http://your-embed:8019/v1"
```

Adds: Audio/video transcription via Whisper, vector embeddings for semantic search.

---

## Extraction Methods

| Content Type | Method | Requires |
|---|---|---|
| PDF (text-based) | pdftotext | poppler-utils (built-in) |
| PDF (scans) | LLM Vision OCR | llm.api_base |
| DOCX, ODT, EPUB, RTF | pandoc | pandoc (built-in) |
| DOC, XLS, PPT, ODS, ODP | Collabora convert-to | collabora.url |
| Images (JPEG, PNG, ...) | LLM Vision | llm.api_base |
| Audio (MP3, WAV, ...) | Whisper transcription | whisper.api_base |
| Video (MP4, ...) | ffmpeg + Whisper | whisper.api_base + ffmpeg |
| Email (EML) | Go net/mail | built-in |
| MSG (Outlook) | String extraction | built-in |
| HTML, XML | pandoc | pandoc (built-in) |
| Archives (ZIP, 7z, TAR) | Recursive extraction | built-in tools |
| Plain text, CSV, code | Passthrough | nothing |

---

## LLM Backend Options

open_taki works with any OpenAI-compatible chat/completions API:

| Backend | Setup | Notes |
|---|---|---|
| **microllm** | `api_base: http://microllm:8012/v1` | Routing proxy, recommended |
| **vLLM** | `api_base: http://vllm:8011/v1` | Direct GPU inference |
| **ollama** | `api_base: http://ollama:11434/v1` | Easy local setup |
| **OpenAI** | `api_base: https://api.openai.com/v1` | Cloud, needs API key |

For OCR, a vision-capable model is required (qwen3.5, GPT-4V, etc.).

---

## Protocol Versions

### v1 (default, Tika-compatible)

No special headers needed. Response is standard Tika JSON:
```json
[{"X-TIKA:content": "extracted text...", "Content-Type": "application/pdf"}]
```

Works with any Tika client. No code changes needed in OpenCloud.

### v2 (extended, auto-detected)

OpenCloud with kosmos edition auto-detects open_taki and sends:
```
X-Taki-Protocol: v2
X-Taki-Features: meta,entities,summary,embedding
X-Taki-Source-Ref: <space-id>/<file-path>
```

Response includes:
```json
[{
  "X-TIKA:content": "extracted text...",
  "X-TAKI:method": "pdftotext",
  "X-TAKI:meta": {"title": "...", "author": "...", "language": "de", "doc_type": "contract"},
  "X-TAKI:entities": [{"type": "person", "value": "Max Mustermann"}, ...],
  "X-TAKI:summary": "Mietvertrag zwischen...",
  "X-TAKI:embedding": [0.023, -0.118, ...],
  "X-TAKI:routing": {"content_target": "both", "meta_target": "bleve", "vector_target": "vector"}
}]
```

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

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

# ENVIRONMENT

You have access to the same container used for installation, including the files and dependencies left by the installation attempt. Each terminal call starts a fresh shell in `/workspace`. Shell-local directory changes, exported variables, and environment activation do not persist between calls. Include any required directory change, environment variables, or activation of an existing environment in each command.

# VALIDATION PROCEDURE

1. Review the guide and installation summary. Use the summary to locate the software and its components, and confirm the installation method, locations, and runtime context through inspection.
2. Identify the expected software behavior described in the guide and select checks appropriate to the resulting installation.
3. Run the checks in the correct directory and runtime environment. If needed, start the installed software within the boundaries below. Prefer evidence of software behavior over file existence alone.
4. Record the commands, observed results, and limitations. Assess the outcome using the definitions below and your own observations.

Distinguish the final installation method from abandoned attempts. Missing files required only by another installation method do not establish failure. A process not already running, or a timed-out or unavailable check, does not by itself establish failure.

# VALIDATION BOUNDARIES

You may inspect files, dependencies, processes and ports, run diagnostic commands, start or run the existing installation, and query local interfaces.

Do not install or update dependencies, build missing artifacts, perform missing setup or migrations, edit files or configuration, or repair the installation. Application startup and normal runtime file creation are permitted only when they do not perform these prohibited actions.

# OUTCOME DEFINITIONS

- `success`: Objective evidence obtained during validation demonstrates that the installation is complete and the software is operational according to the supplied guide.
- `failure`: Objective evidence obtained during validation demonstrates that the resulting installation is incomplete or cannot operate without further installation or repair work.
- `inconclusive`: The evidence is insufficient to establish either success or failure, including when observations are ambiguous or an environmental limitation prevents a reliable assessment.

# FINAL OUTPUT

Return the structured validation report with these three fields:

- `assessed_outcome`: Report `success`, `failure`, or `inconclusive` according to the definitions above.
- `outcome_evidence`: Record observable command results or execution evidence that directly support the assessed outcome. Include the exact command, working directory or runtime context, exit code where available, and relevant output for decisive checks. For an inconclusive assessment, record the observations or execution limitations preventing a decision.
- `assessment_summary`: Explain in detail what you inspected, how you performed validation, and how the observations support your assessment. Include checks that could not be completed, limitations, and unresolved uncertainty.