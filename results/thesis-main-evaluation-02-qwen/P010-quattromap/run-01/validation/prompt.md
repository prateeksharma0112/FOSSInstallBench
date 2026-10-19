# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** QuattroMap

**Description:** Browser tool for the synchronous display of up to four different map windows.

## Supplied installation guide

## Guide: Installation.md

## Konfiguration

Sie können einige Standardeinstellungen von [QuattroMap](https://kreis-viersen.usercontent.opencode.de/quattromap) festlegen, indem Sie diese in der [config.json](./src/config.json) bearbeiten:


|Parameter|Erklärung|Beispiel|
|:---|:---|:---|
|"center"|Gibt die Zentrumskoordinate des Kartenfensters beim Starten an. Angabe geographisch mit Längen- und Breitenangabe in EPSG 4326.|"center": [6.391263, 51.258812]|
|"zoom"|Definiert die Zoomstufe beim Start. Wertebereich: 0 (fern) - 22 (nah)|"zoom": 16|
|"maps"|Optionale Angabe über die Anzahl der Kartenfenster. Mögliche Werte: 1, 2, 3, 4; Standardwert: 4| "maps": 2|
|"crosshair"| Optionale Definition der Fadenkreuzfarbe. Mögliche Werte: black, red, orange, yellow, green, blue, pink; Standardwert: black|"crosshair": "red"|
|"map_x": {"layer": `layername`} *Optional*: "overlay": `layername`, "overlay_opacity": `opacity-value`, }|Voreinstellung der dargestellten Dienste des Kartenfensters x (1-4) beim Starten der QuattroMap. `layer` enthält einen Namen eines Dienstes, die unter "layer" definiert sind. `overlay` enthält einen Namen eines Dienstes, der als Abdeckungslayer dient und muss nur angegeben werden, wenn ein Abdeckungslayer verwendet werden soll. `overlay_opacity` definiert die Deckkraft des Abdeckungslayers. Mögliche Werte: 0 (transparent) - 1 (opak); Standardwert: 0.5| "map_1": {"layer": "NRW Luftbild Farbe", "overlay": "NRW Schummerung", "overlay_opacity": 0.4}|
|"layer": [ .. ]|Enthält die Definitionen der wählbaren Dienste im Dropdown Menü||
|"name"|Name des Dienstes, der im Dropdown Menü und beim Klick auf den Info-Button erscheint.|"name": "NRW Alkis TN"|
|"attribution"|Attribution zur Beschreibung der verwendeten Dienste, die über den Info-Button dargestellt wird. HTML-Tags können verwendet werden.|"attribution": "Land NRW (2021) Deutschland ? Zero ? Version 2.0 (`<a target='_blank' rel='noopener noreferrer' href='https://www.govdata.de/dl-de/zero-2-0'>www.govdata.de/dl-de/zero-2-0</a>`)"|
|"url"|URL des WMS 1.3.0 Dienstes oder OpenStreetMap XYZ-Tiles|"url": "`https://www.wms.nrw.de/geobasis/wms_nw_alkis`"|
|"layer"|Darzustellende Layer des Dienstes. Mehrere Layer werden mit Komma getrennt.|"layer": "nutzungsarten,flurstuecke"|
|"format"| Abzurufendes Rasterformat (`png` oder `jpeg`) der Kacheln. Da png Transparenz ermöglicht, ist png zu empfehlen. Jedoch können nicht alle Dienste png liefern.|"format": "png"|
|"category"|Begriff zur Kategorisierung der Dienste im Dropdown-Menü.|"category": "GeoBasis NRW"|
|"onlyOverlay"|Mit diesem optionalen Parameter lässt sich der entsprechende Dienst nur als Overlay verwenden.|"onlyOverlay": true|
|"style"|Optionaler Parameter zur Auswahl eines bestimmten Stils. Stile können von Diensten angeboten werden.|"style": "Farbe"|
|"compactAttribution"|Mit diesem optionalen Parameter lässt sich festlegen, ob die Attribution mit dem Layernamen bei Auswahl des Layers ausgeklappt (`false`) oder eingeklappt ist (`true` = Standardwert).|"compactAttribution": "false"|

## Develop

```bash
# clone the repository
git clone https://github.com/kreis-viersen/quattromap/
cd quattromap
```
Install the deps, start the dev server and open the web browser on `http://localhost:8080/`.

```bash
# install dependencies
npm install
# start dev server
npm start
```

The build process will watch for changes to the filesystem, rebuild and autoreload QuattroMap. However note this from the [webpack-dev-server docs](https://webpack.js.org/configuration/dev-server/):

> webpack uses the file system to get notified of file changes. In some cases this does not work. For example, when using Network File System (NFS). Vagrant also has a lot of problems with this. In these cases, use polling. ([snippet source](https://webpack.js.org/configuration/dev-server/#devserverwatchoptions-))

```bash
# build the app
npm run build
```
Once the build is finished, you'll find it at `dist/`.

```bash
# publish files to a gh-pages branch on GitHub
npm run deploy
```

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

## Installation: QuattroMap

**Environment:** Ubuntu 22.04 container, shared workspace at `/workspace` (repo already checked out at commit `24041c0`). Node.js/npm were NOT preinstalled.

### Method (final)
Followed the guide's "Develop" section: `npm install` + `npm start` (dev server) and `npm run build`, after first installing the Node.js prerequisite.

### Steps performed
1. **Prerequisite (not in guide):** Installed Node.js 20.20.2 / npm 10.8.2 via the NodeSource apt repository (`curl -fsSL https://deb.nodesource.com/setup_20.x | bash` then `apt-get install -y nodejs`), because the project's webpack 5.110 / webpack-dev-server 6 require Node >= 18 and Ubuntu 22.04's repo node is older.
2. `cd /workspace && npm install` — exit 0; 283 packages in `/workspace/node_modules` (npm reported 15 pre-existing audit vulnerabilities, non-blocking).
3. `cd /workspace && npm run build` — exit 0; webpack 5.110.3 compiled with warnings only (bundle size / dynamic-require notices, non-fatal). Build output in `/workspace/dist/`: `index.html`, `bundle.js` (~1.24 MiB), `vendor/maplibre/`, `img/`, `oss-licenses.json`.
4. `cd /workspace && npm start` (webpack-dev-server, per webpack.config.js with no explicit port → default 8080, matching the guide) — compiled successfully; verified serving then stopped the server by PID so port 8080 is now free.

### Access points / startup
- Dev server: `cd /workspace && npm start` → http://localhost:8080/
- Production build: `/workspace/dist/` (static, servable by any web server); `npm run deploy` publishes to gh-pages (not run).
- Runtime configuration lives in `/workspace/src/config.json` (center, zoom, maps, crosshair, layers) per the guide.

### Final state
Node 20.20.2 + npm 10.8.2 installed system-wide; `/workspace/node_modules` and `/workspace/dist/` populated; no dev server currently running. No source files were modified.

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