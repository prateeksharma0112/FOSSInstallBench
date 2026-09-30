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
