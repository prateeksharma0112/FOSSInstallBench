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

## QuattroMap installation

**Working directory / repo:** `/workspace` (git commit 24041c0, "Update .gitlab-ci.yml"). This is the shared installation workspace on Ubuntu 22.04.

**Prerequisite — Node.js:**
- The environment had no `node`/`npm` (`exit code 127`). The Ubuntu 22.04 apt candidate is only `nodejs 12.22.9`, too old for the project's toolchain.
- Added the NodeSource `setup_20.x` repo and ran `apt-get install -y nodejs`, yielding `node v20.20.2` and `npm 10.8.2`.
- Downloaded the NodeSource setup script from `https://deb.nodesource.com/setup_20.x` (a non-apt-source registry), so this step is a non-guide prerequisite action.

**Method used (per the guide's Develop section):**
1. `npm install` in `/workspace` → `added 403 packages` (exit 0). Emitted EBADENGINE warnings: `webpack-dev-server@6.0.0` requires `node >= 22.15.0`, `p-retry@8.0.0` requires `node >=22`; these were warnings only and did not block execution.
2. `npm run build` (`webpack`) → `webpack 5.110.3 compiled with 4 warnings` (exit 0). Warnings are performance/size and a maplibre dynamic-require notice, not errors. Output produced at `/workspace/dist/`: `bundle.js` (~1.29 MB), `index.html`, `oss-licenses.json`, `img/`, `vendor/`.
3. `npm start` (`webpack serve`) → dev server compiled successfully (`152 modules`) and served the app.

**Verification (evidence):**
- `curl http://localhost:8080/` → HTTP 200, `<title>QuattroMap</title>`, 9372 bytes.
- `curl http://localhost:8080/bundle.js` → HTTP 200, 1,356,256 bytes.
- Dev server log: `[webpack-dev-server] Project is running at: ... http://localhost:8080/`.

**Access points / startup commands:**
- Production build served from `/workspace/dist` (any static server).
- Dev server: `npm start` in `/workspace`, default `http://localhost:8080/` (one run bound `8081` because a previous instance still held `8080`).

**Cleanup:** All webpack/dev-server processes started during verification were terminated.

**Unknown/incomplete:** None material. The only caveat is the Node engine mismatch warning from `webpack-dev-server@6.0.0` (declares Node >= 22.15.0) while the installed runtime is Node 20; build and dev server nonetheless functioned and served correctly.

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