# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** Pomodoro

**Description:** Local focus timer for greater efficiency in everyday administrative work: fixed work blocks, conscious breaks and honest time tracking that also counts interrupted focus sessions.

## Supplied installation guide

## Guide: Installation.md

## Installation

Requires Python 3.10+ on macOS.

```bash
git clone <this repo>
cd pomodoro
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

This installs the `pomodoro` console command (via the entry point defined
in `pyproject.toml`) into your active environment.

## Starting it

```bash
pomodoro
```

This opens the app window. Configure Focus/Break minutes, round count,
and the optional long break in the "Einstellungen" panel, then hit
**Start**. Switch to the **Statistik** tab any time to see your history.

## Building a double-clickable macOS app

If you'd rather launch Pomodoro from the Dock / Launchpad than from a
terminal, bundle it into a standalone `Pomodoro.app` with
[PyInstaller](https://pyinstaller.org/):

```bash
./packaging/build.sh
```

That script installs the build dependency (`pip install -e ".[package]"`),
renders the app icon, runs PyInstaller against
[`packaging/Pomodoro.spec`](packaging/Pomodoro.spec), and ad-hoc code-signs
the result (required to run on Apple Silicon). When it finishes:

```bash
cp -R dist/Pomodoro.app /Applications/
open /Applications/Pomodoro.app
```

The bundle is self-contained — it ships its own Python and Qt, so it runs
on any Mac (macOS 11+) without a Python install. Pass `--dmg` to also get
a `dist/Pomodoro.dmg` for copying it to another machine:

```bash
./packaging/build.sh --dmg
```

Because the app isn't signed with an Apple Developer ID, the first launch
on another Mac needs a right-click → **Open** (or *System Settings →
Privacy & Security → Open Anyway*) to get past Gatekeeper. On the machine
that built it, it just opens.

The phase-end sounds and all settings/history work exactly as in the
terminal version — see the two sections below.

## Adding your own sounds

The app plays an MP3 at the end of each Focus round and each Break. Drop
your own files into [`sounds/`](sounds/) using these exact names:

| File             | Played when...                 |
|-------------------|--------------------------------|
| `focus_end.mp3`  | a Focus round finishes          |
| `break_end.mp3`  | a short or long Break finishes  |

No MP3s are shipped in this repo (see [`sounds/README.md`](sounds/README.md)).
Without them the app doesn't crash — it just falls back to a terminal
beep and shows a small hint in the window. The lookup folder can be
overridden with the `POMODORO_SOUNDS_DIR` environment variable.

**In the packaged `Pomodoro.app`**, whatever `sounds/` files were present
at build time are bundled inside the app. To swap them afterwards without
rebuilding, drop `focus_end.mp3` / `break_end.mp3` into
`~/Library/Application Support/Pomodoro/sounds/` — that location is
checked first and wins over the bundled copies.

## Running Pomodoro in a container

The primary way to use Pomodoro is still the native macOS app above, but a
[`Dockerfile`](Dockerfile) is also provided to make it cloud-ready — the same
window, unmodified, made reachable from a plain browser tab:

```bash
docker build -t pomodoro .
docker run --rm -p 6080:6080 \
  -v pomodoro-data:/home/pomodoro/.local/share/Pomodoro \
  pomodoro
```

Then open <http://localhost:6080/vnc.html> — the actual Qt window is
rendered on a virtual display inside the container and streamed to the
browser via VNC/noVNC (see [`docker/entrypoint.sh`](docker/entrypoint.sh)).
There is no separate "web version"; it's the same app.

Two things behave differently than on macOS, both by design of what a
container is:

- **Sound and system notifications are silent.** `afplay`/`osascript` don't
  exist on Linux, and this image doesn't bridge PulseAudio/D-Bus out to the
  host — the app already degrades gracefully in that case (a terminal beep
  instead of the sound file, no notification), so nothing crashes, but you
  won't hear or see either.
- **Data only survives a restart if you mount a volume**, as in the command
  above — otherwise settings and history disappear with the container. The
  data directory can also be overridden explicitly with `POMODORO_DATA_DIR`.

## Configuration & data storage

Settings (last-used timer configuration, theme, project tag) and your
focus history are stored automatically under a per-OS user data directory
(`src/pomodoro/persistence/paths.py`) — `~/Library/Application Support/Pomodoro/`
on macOS, `~/.local/share/Pomodoro/` on Linux (including the container image,
respecting `$XDG_DATA_HOME` if set), or `%APPDATA%\Pomodoro\` on Windows.
Set `POMODORO_DATA_DIR` to use an explicit location instead:

```
settings.json   # last-used configuration (JSON)
pomodoro.db     # completed focus rounds (SQLite)
```

Every Focus round is appended to `pomodoro.db` with its timestamp,
duration, optional project tag, and whether it ran to completion —
that's the data the Statistics tab aggregates into "today / this week /
all-time" totals and the 7-day chart. Since 0.2.0, a Focus round you
cancel early is recorded too, with the time actually elapsed up to that
point, instead of being discarded; only Break phases are never recorded
at all. You can wipe this history from inside the app (Statistik tab →
"Historie zurücksetzen"), which asks for confirmation first since it
can't be undone.

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

## Environment
- Workspace/repo: `/workspace` (checked out at commit 5432007, gitlab ci change)
- OS: Ubuntu 22.04.5 LTS (Linux x86_64). The supplied guide documents macOS, but the same Python/venv install method was used here.
- Virtual environment: `/workspace/.venv` (Python 3.10.12)

## Method used (documented venv/editable install)
1. Installed prerequisites absent from the base image: `python3`, `python3-pip`, `python3-venv` (apt).
2. `cd /workspace && python3 -m venv .venv && source .venv/bin/activate`
3. `pip install --upgrade pip`
4. `pip install -e .` — success. Built editable wheel `pomodoro_timer-0.3.0-0.editable`, installed `PySide6 6.11.2`, `shiboken6`, and the console script `/workspace/.venv/bin/pomodoro`.

## Additional system prerequisites installed (undocumented; needed on Linux)
Qt6 runtime libraries: `libgl1`, `libegl1`, `libglib2.0-0`, `libxkbcommon-x11-0`, `libxcb-cursor0`, `libxcb-xinerama0`, `libdbus-1-3`, `libfontconfig1`, `libsm6`, `libice6`, `libxrender1`, `libxi6`, `libxtst6`, `libxrandr2`, `libxcursor1`, `libxcomposite1`, `libxdamage1`, `libxfixes3`, `libxext6`, `libx11-xcb1`, `libnss3`, `libasound2`. Without these, importing PySide6 failed with `ImportError: libGL.so.1` then `libglib-2.0.so.0`.

## Verification / access
- Console command present: `/workspace/.venv/bin/pomodoro`
- Launch test: `QT_QPA_PLATFORM=offscreen pomodoro` ran until an 8s timeout (exit 124), indicating the Qt window/event loop started without error.
- Test suite: `QT_QPA_PLATFORM=offscreen python -m pytest -q` → 20 passed.

## Startup command
```
source /workspace/.venv/bin/activate
pomodoro
```
(In this headless container a display backend is required, e.g. QT_QPA_PLATFORM=offscreen, or the repo's Docker/noVNC setup.)

## Not attempted / not applicable
- macOS PyInstaller app bundling (`./packaging/build.sh`, `packaging/Pomodoro.spec`, code signing) — macOS-only, N/A on Linux.
- Docker image build — a documented alternative, not needed since the native venv install succeeded.
- MP3 sound files / POMODORO_* env vars were not configured (optional; app degrades gracefully).

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