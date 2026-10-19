# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** Audiominer

**Description:** Service for the automated transcription of audio and video files via web UI or file system connection

## Supplied installation guide

## Guide: Installation.md

# Installation

## Voraussetzungen

* Für den Modell-Download wird ein Hugging-Face Token benötigt.
Siehe Anleitung: [Hugging Face Token erstellen](huggingface_token.md).

## Docker Compose (empfohlen)

Eine lauffähige Vorlage befindet sich unter `deployments/example-opencode`.
Diese Dateien sind als Ausgangspunkt gedacht und können angepasst werden.

### Anmeldung bei `registry.opencode.de`

Die Anmeldung ist erforderlich, um die bereitgestellten Images abrufen zu können.
Dazu wird ein *Personal Access Token* benötigt (Berechtigung: `read_repository`):
[https://gitlab.opencode.de/-/user_settings/personal_access_tokens](https://gitlab.opencode.de/-/user_settings/personal_access_tokens)

```bash
docker login -u <TOKEN_NAME> -p <TOKEN_VALUE> registry.opencode.de
```

### Demo starten

1. Hugging-Face Token in die `.env` eintragen (sonst können die Modelle nicht geladen werden).

    Beispiel:
    ```properties
    # Inhalt der .env
    HF_TOKEN=<YOUR_HF_TOKEN>
    ```

2. Die Compose-Konfiguration ist in mehrere Dateien aufgeteilt:
    * `compose.yml` – Redis, Web Service, FS Watcher (Notify Service ist auskommentiert)
    * `compose.gpu.yml` – ASR Service mit GPU-Konfiguration
    * `compose.cpu.yml` – ASR Service als CPU-Variante

3. Start (CPU oder GPU):
    ```bash
    cd deployments/example-opencode

    # CPU
    docker compose --env-file .env-example --env-file .env -f compose.yml -f compose.cpu.yml up

    # GPU
    docker compose --env-file .env-example --env-file .env -f compose.yml -f compose.gpu.yml up
    ```

### Zugriff / Nutzung

Nach dem Start:

* **Admin-Oberfläche:** [http://localhost:8091](http://localhost:8091)
* **Öffentliche Web-Oberfläche:** [http://localhost:8090](http://localhost:8090)
* **Datei-Workflow:** Im Verzeichnis `watch` (auf gleicher Ebene) Audio-/Videodateien ablegen.
Sobald fertig, werden Transkripte dort ebenfalls gespeichert.

### Eigene Konfiguration verwenden

Empfohlen: Vorlage kopieren, z. B. nach `deployments/local-demo`.

```bash
# Beispiel
cp -r deployments/example-opencode deployments/local-demo
cd deployments/local-demo

# .env-example nach .env kopieren/umbenennen und HF_TOKEN setzen
# Optional: Notify Service in compose.yml aktivieren (auskommentieren entfernen)

# CPU
docker compose --env-file .env -f compose.yml -f compose.cpu.yml up

# GPU
docker compose --env-file .env -f compose.yml -f compose.gpu.yml up
```



# Links

* [Project Wiki](https://gitlab.opencode.de/bpa/audiominer/audiominer/-/wikis/home)

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

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